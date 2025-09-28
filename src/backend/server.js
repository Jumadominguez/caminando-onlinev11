require('dotenv').config();
const mongoose = require('mongoose');
const app = require('./src/app');

// 🗄️ Arquitectura Multi-Database - 8 Bases de Datos Separadas
// Implementación según documentación en Library/archivos/database-architecture.md

// ============================================================================
// 1. BASES DE ADMINISTRACIÓN Y OPERACIONES
// ============================================================================

// Base admin - Usuarios, sesiones y carritos
const adminConnection = mongoose.createConnection(
  process.env.MONGO_ADMIN_URI || 'mongodb://localhost:27017/admin',
  {
    maxPoolSize: 10,
    serverSelectionTimeoutMS: 5000,
    socketTimeoutMS: 45000,
  }
);

// Base operations_db - Pedidos, logs y configuraciones
const operationsConnection = mongoose.createConnection(
  process.env.MONGO_OPERATIONS_URI || 'mongodb://localhost:27017/operations_db',
  {
    maxPoolSize: 10,
    serverSelectionTimeoutMS: 5000,
    socketTimeoutMS: 45000,
  }
);

// ============================================================================
// 2. BASE PROCESADA (FRONTEND)
// ============================================================================

// Base caminando_online_db - Datos normalizados para frontend
const processedConnection = mongoose.createConnection(
  process.env.MONGO_PROCESSED_URI || 'mongodb://localhost:27017/caminando_online_db',
  {
    maxPoolSize: 20,
    serverSelectionTimeoutMS: 5000,
    socketTimeoutMS: 45000,
  }
);

// ============================================================================
// 3. BASES RAW (SCRAPING POR SUPERMERCADO)
// ============================================================================

// Base carrefour - Datos raw de Carrefour
const carrefourConnection = mongoose.createConnection(
  process.env.MONGO_CARREFOUR_URI || 'mongodb://localhost:27017/carrefour',
  {
    maxPoolSize: 5,
    serverSelectionTimeoutMS: 5000,
    socketTimeoutMS: 45000,
  }
);

// Base dia - Datos raw de Dia
const diaConnection = mongoose.createConnection(
  process.env.MONGO_DIA_URI || 'mongodb://localhost:27017/dia',
  {
    maxPoolSize: 5,
    serverSelectionTimeoutMS: 5000,
    socketTimeoutMS: 45000,
  }
);

// Base jumbo - Datos raw de Jumbo
const jumboConnection = mongoose.createConnection(
  process.env.MONGO_JUMBO_URI || 'mongodb://localhost:27017/jumbo',
  {
    maxPoolSize: 5,
    serverSelectionTimeoutMS: 5000,
    socketTimeoutMS: 45000,
  }
);

// Base vea - Datos raw de Vea
const veaConnection = mongoose.createConnection(
  process.env.MONGO_VEA_URI || 'mongodb://localhost:27017/vea',
  {
    maxPoolSize: 5,
    serverSelectionTimeoutMS: 5000,
    socketTimeoutMS: 45000,
  }
);

// Base disco - Datos raw de Disco
const discoConnection = mongoose.createConnection(
  process.env.MONGO_DISCO_URI || 'mongodb://localhost:27017/disco',
  {
    maxPoolSize: 5,
    serverSelectionTimeoutMS: 5000,
    socketTimeoutMS: 45000,
  }
);

// ============================================================================
// GESTIÓN DE CONEXIONES Y MANEJO DE ERRORES
// ============================================================================

// Objeto centralizado de conexiones para acceso global
const databaseConnections = {
  // Bases de administración y operaciones
  admin: adminConnection,
  operations: operationsConnection,

  // Base procesada (frontend)
  processed: processedConnection,

  // Bases raw por supermercado
  carrefour: carrefourConnection,
  dia: diaConnection,
  jumbo: jumboConnection,
  vea: veaConnection,
  disco: discoConnection,
};

// Función para verificar estado de todas las conexiones
const checkConnections = async () => {
  const connectionStatus = {};

  for (const [name, connection] of Object.entries(databaseConnections)) {
    try {
      // Esperar a que la conexión esté lista
      if (connection.readyState === 1) { // 1 = connected
        await connection.db.admin().ping();
        connectionStatus[name] = 'connected';
        console.log(`✅ ${name}: Connected`);
      } else {
        connectionStatus[name] = 'connecting';
        console.log(`⏳ ${name}: Connecting...`);
      }
    } catch (error) {
      connectionStatus[name] = 'disconnected';
      console.error(`❌ ${name}: Connection failed - ${error.message}`);
    }
  }

  return connectionStatus;
};

// Event listeners para todas las conexiones
Object.entries(databaseConnections).forEach(([name, connection]) => {
  connection.on('connected', () => {
    console.log(`🔗 ${name}: MongoDB connected successfully`);
  });

  connection.on('error', (err) => {
    console.error(`❌ ${name}: MongoDB connection error:`, err);
  });

  connection.on('disconnected', () => {
    console.log(`🔌 ${name}: MongoDB disconnected`);
  });
});

// ============================================================================
// INICIALIZACIÓN DEL SERVIDOR
// ============================================================================

// Verificar conexiones antes de iniciar el servidor
const initializeServer = async () => {
  try {
    console.log('🚀 Initializing Caminando Online V4 Server...');
    console.log('📊 Waiting for database connections...');

    // Esperar 3 segundos para que las conexiones se establezcan
    await new Promise(resolve => setTimeout(resolve, 3000));

    console.log('📊 Checking database connections...');
    const status = await checkConnections();

    // Contar conexiones exitosas
    const connectedCount = Object.values(status).filter(s => s === 'connected').length;
    const totalConnections = Object.keys(status).length;

    console.log(`📈 Database Status: ${connectedCount}/${totalConnections} connections successful`);

    if (connectedCount === 0) {
      throw new Error('No database connections available. Server cannot start.');
    }

    if (connectedCount < totalConnections) {
      console.warn(`⚠️  Warning: ${totalConnections - connectedCount} database connections failed. Server starting with limited functionality.`);
    }

    // Hacer conexiones disponibles globalmente
    global.databaseConnections = databaseConnections;

    // Iniciar servidor
    const PORT = process.env.PORT || 5000;
    app.listen(PORT, () => {
      console.log(`🌐 Server running on port ${PORT}`);
      console.log(`🏗️  Architecture: Multi-database (8 databases)`);
      console.log(`📊 Connected databases: ${connectedCount}/${totalConnections}`);
      console.log('✅ Caminando Online V4 Server started successfully!');
    });

  } catch (error) {
    console.error('💥 Failed to initialize server:', error);
    process.exit(1);
  }
};

// Función para cerrar conexiones gracefully
const closeConnections = async () => {
  console.log('🔄 Closing database connections...');

  const closePromises = Object.entries(databaseConnections).map(async ([name, connection]) => {
    try {
      await connection.close();
      console.log(`🔌 ${name}: Connection closed`);
    } catch (error) {
      console.error(`❌ ${name}: Error closing connection:`, error);
    }
  });

  await Promise.all(closePromises);
  console.log('✅ All database connections closed');
};

// Manejo de señales para cierre graceful
process.on('SIGINT', async () => {
  console.log('\n🛑 Received SIGINT. Gracefully shutting down...');
  await closeConnections();
  process.exit(0);
});

process.on('SIGTERM', async () => {
  console.log('\n🛑 Received SIGTERM. Gracefully shutting down...');
  await closeConnections();
  process.exit(0);
});

// ============================================================================
// INICIAR SERVIDOR
// ============================================================================

initializeServer();