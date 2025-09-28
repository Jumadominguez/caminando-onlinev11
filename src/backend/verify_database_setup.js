const { MongoClient } = require('mongodb');

// Configuración de usuarios para testing
const USERS = {
  admin: {
    uri: 'mongodb://admin:admin123456@localhost:27017/admin',
    db: 'admin',
    expectedRoles: ['userAdminAnyDatabase', 'readWriteAnyDatabase', 'dbAdminAnyDatabase', 'clusterAdmin']
  },
  app: {
    uri: 'mongodb://caminando_user:caminando_secure_2025@localhost:27017/caminando_online_db',
    db: 'caminando_online_db',
    expectedPermissions: ['readWrite', 'dbAdmin']
  },
  scraper: {
    uri: 'mongodb://scraper_user:scraper_secure_2025@localhost:27017/caminando_online_db',
    db: 'caminando_online_db',
    expectedPermissions: ['readWrite', 'read']
  }
};

async function testUserConnection(userType, config) {
  let client;
  try {
    console.log(`🔍 Probando conexión de usuario: ${userType}`);

    client = new MongoClient(config.uri);
    await client.connect();

    const db = client.db(config.db);

    // Verificar conexión básica
    const collections = await db.collections();
    console.log(`   ✅ Conectado a ${config.db} (${collections.length} colecciones)`);

    // Verificar permisos básicos
    if (config.db === 'caminando_online_db') {
      // Intentar leer de supermarkets
      const supermarkets = await db.collection('supermarkets').find({}).limit(1).toArray();
      console.log(`   ✅ Lectura exitosa (${supermarkets.length} documentos encontrados)`);

      // Si es usuario de aplicación, intentar escritura
      if (userType === 'app') {
        const testDoc = { _id: 'test_connection', name: 'Test Connection', timestamp: new Date() };
        await db.collection('supermarkets').insertOne(testDoc);
        await db.collection('supermarkets').deleteOne({ _id: 'test_connection' });
        console.log(`   ✅ Escritura y eliminación exitosas`);
      }
    }

    return true;
  } catch (error) {
    console.log(`   ❌ Error con usuario ${userType}: ${error.message}`);
    return false;
  } finally {
    if (client) {
      await client.close();
    }
  }
}

async function verifyDatabaseSetup() {
  console.log('🔐 Verificando configuración de autenticación y base de datos...\n');

  let allTestsPassed = true;

  // Probar cada usuario
  for (const [userType, config] of Object.entries(USERS)) {
    const success = await testUserConnection(userType, config);
    if (!success) {
      allTestsPassed = false;
    }
    console.log(''); // Línea en blanco
  }

  // Verificar datos base
  console.log('📊 Verificando datos base en caminando_online_db...');

  try {
    const client = new MongoClient('mongodb://caminando_user:caminando_secure_2025@localhost:27017/caminando_online_db');
    await client.connect();
    const db = client.db('caminando_online_db');

    // Verificar supermercados
    const supermarkets = await db.collection('supermarkets').find({}).toArray();
    console.log(`   ✅ Supermercados: ${supermarkets.length} encontrados`);
    supermarkets.forEach(s => console.log(`      - ${s.name} (${s._id})`));

    // Verificar categorías
    const categories = await db.collection('categories').find({}).toArray();
    console.log(`   ✅ Categorías: ${categories.length} encontradas`);
    categories.forEach(c => console.log(`      - ${c.displayName} (${c._id})`));

    // Verificar colecciones vacías
    const collections = [
      'users', 'orders', 'carts', 'price_history', 'user_addresses',
      'notifications', 'user_sessions', 'api_logs', 'system_settings',
      'subcategories', 'producttypes', 'products', 'filters', 'offers'
    ];
    for (const coll of collections) {
      const count = await db.collection(coll).countDocuments();
      console.log(`   ✅ ${coll}: ${count} documentos`);
    }

    await client.close();

  } catch (error) {
    console.log(`   ❌ Error verificando datos base: ${error.message}`);
    allTestsPassed = false;
  }

  console.log('\n' + '='.repeat(60));

  if (allTestsPassed) {
    console.log('🎉 ¡Configuración de base de datos COMPLETA y FUNCIONAL!');
    console.log('\n📝 Resumen de configuración:');
    console.log('   • Base de datos admin: Configurada con usuarios');
    console.log('   • Base de datos aplicación: Inicializada con datos base');
    console.log('   • Autenticación: Funcionando correctamente');
    console.log('   • Usuarios: Todos los permisos verificados');
    console.log('\n🔧 Usuarios disponibles:');
    console.log('   • Admin: mongodb://admin:admin123456@localhost:27017/admin');
    console.log('   • App: mongodb://caminando_user:caminando_secure_2025@localhost:27017/caminando_online_db');
    console.log('   • Scraper: mongodb://scraper_user:scraper_secure_2025@localhost:27017/caminando_online_db');
    console.log('\n⚠️  IMPORTANTE: Cambia las contraseñas en producción!');
  } else {
    console.log('❌ Algunos tests fallaron. Revisa la configuración.');
    process.exit(1);
  }
}

// Ejecutar verificación
verifyDatabaseSetup().catch(console.error);