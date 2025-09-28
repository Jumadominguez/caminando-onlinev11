const mongoose = require('mongoose');
require('dotenv').config();

// Database URIs from environment - Arquitectura Multi-Database Correcta
const databases = {
  admin: process.env.MONGO_ADMIN_URI,
  operations_db: process.env.MONGO_OPERATIONS_URI,
  caminando_online_db: process.env.MONGO_PROCESSED_URI,
  carrefour: process.env.MONGO_CARREFOUR_URI,
  dia: process.env.MONGO_DIA_URI,
  jumbo: process.env.MONGO_JUMBO_URI,
  vea: process.env.MONGO_VEA_URI,
  disco: process.env.MONGO_DISCO_URI
};

async function initializeDatabases() {
  console.log('🚀 Initializing databases and collections...');

  for (const [dbName, uri] of Object.entries(databases)) {
    try {
      console.log(`\n📊 Connecting to ${dbName} database...`);

      // Connect to specific database
      const connection = await mongoose.createConnection(uri, {
        maxPoolSize: 10,
        serverSelectionTimeoutMS: 5000,
        socketTimeoutMS: 45000,
      });

      // Wait for connection to be ready
      await new Promise((resolve, reject) => {
        connection.once('open', resolve);
        connection.once('error', reject);
        // Timeout after 10 seconds
        setTimeout(() => reject(new Error('Connection timeout')), 10000);
      });

      console.log(`✅ Connected to ${dbName} database`);

      // Create collections if they don't exist
      const collections = getCollectionsForDatabase(dbName);

      for (const collectionName of collections) {
        try {
          // Check if collection exists
          const existingCollections = await connection.db.listCollections({ name: collectionName }).toArray();

          if (existingCollections.length === 0) {
            // Create collection
            await connection.db.createCollection(collectionName);
            console.log(`✅ Created collection: ${collectionName} in ${dbName}`);
          } else {
            console.log(`ℹ️  Collection ${collectionName} already exists in ${dbName}`);
          }
        } catch (error) {
          console.error(`❌ Error creating collection ${collectionName} in ${dbName}:`, error.message);
        }
      }

      // Close connection
      await connection.close();
      console.log(`✅ ${dbName} database initialized successfully`);

    } catch (error) {
      console.error(`❌ Error initializing ${dbName} database:`, error.message);
      console.error(`   URI: ${uri}`);
    }
  }

  console.log('\n🎉 Database initialization completed!');
  process.exit(0);
}

function getCollectionsForDatabase(dbName) {
  const collectionMap = {
    // Admin - Usuarios y autenticación
    admin: ['users', 'user_addresses', 'user_sessions', 'carts'],

    // Operations - Sistema y operaciones
    operations_db: ['orders', 'api_logs', 'notifications', 'system_settings'],

    // Processed - Datos normalizados para frontend
    caminando_online_db: ['categories', 'subcategories', 'products', 'producttypes', 'supermarkets', 'offers', 'filters', 'price_history'],

    // Raw data por supermercado
    carrefour: ['categories', 'subcategories', 'products', 'producttypes', 'offers', 'filters', 'price_history', 'supermarket-info'],
    dia: ['categories', 'subcategories', 'products', 'producttypes', 'offers', 'filters', 'price_history', 'supermarket-info'],
    jumbo: ['categories', 'subcategories', 'products', 'producttypes', 'offers', 'filters', 'price_history', 'supermarket-info'],
    vea: ['categories', 'subcategories', 'products', 'producttypes', 'offers', 'filters', 'price_history', 'supermarket-info'],
    disco: ['categories', 'subcategories', 'products', 'producttypes', 'offers', 'filters', 'price_history', 'supermarket-info']
  };

  return collectionMap[dbName] || [];
}

// Handle errors
process.on('unhandledRejection', (error) => {
  console.error('❌ Unhandled rejection:', error);
  process.exit(1);
});

process.on('uncaughtException', (error) => {
  console.error('❌ Uncaught exception:', error);
  process.exit(1);
});

// Run initialization
initializeDatabases();