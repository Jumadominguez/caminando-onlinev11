const { MongoClient } = require('mongodb');

async function initializeAdminDatabase() {
  console.log('🚀 Inicializando base de datos admin de MongoDB...');

  const mongoUri = process.env.MONGO_URI || 'mongodb://localhost:27017';
  const client = new MongoClient(mongoUri);

  try {
    // Conectar al admin database
    await client.connect();
    const adminDb = client.db('admin');

    console.log('📡 Conectado a MongoDB admin database');

    // Crear usuario administrador
    console.log('👤 Creando usuario administrador...');
    await adminDb.command({
      createUser: 'admin',
      pwd: 'admin123456',
      roles: [
        { role: 'userAdminAnyDatabase', db: 'admin' },
        { role: 'readWriteAnyDatabase', db: 'admin' },
        { role: 'dbAdminAnyDatabase', db: 'admin' },
        { role: 'clusterAdmin', db: 'admin' }
      ]
    });

    // Crear usuario para la aplicación Caminando Online
    console.log('🏪 Creando usuario para aplicación Caminando Online...');
    await adminDb.command({
      createUser: 'caminando_user',
      pwd: 'caminando_secure_2025',
      roles: [
        { role: 'readWrite', db: 'caminando_online_db' },
        { role: 'dbAdmin', db: 'caminando_online_db' }
      ]
    });

    // Crear usuario para scraping (permisos de solo lectura en algunos casos)
    console.log('🔍 Creando usuario para scraping...');
    await adminDb.command({
      createUser: 'scraper_user',
      pwd: 'scraper_secure_2025',
      roles: [
        { role: 'readWrite', db: 'caminando_online_db' },
        { role: 'read', db: 'caminando_online_db' }
      ]
    });

    // Verificar usuarios creados
    const users = await adminDb.command({ usersInfo: 1 });
    console.log('✅ Usuarios creados en admin database:');
    users.users.forEach(user => {
      console.log(`   - ${user.user} (${user.roles.map(r => r.role).join(', ')})`);
    });

    console.log('🎉 Base de datos admin configurada exitosamente!');
    console.log('');
    console.log('📝 Resumen de configuración:');
    console.log('   • Usuario admin: admin / admin123456');
    console.log('   • Usuario app: caminando_user / caminando_secure_2025');
    console.log('   • Usuario scraper: scraper_user / scraper_secure_2025');
    console.log('');
    console.log('⚠️  IMPORTANTE: Cambia estas contraseñas en producción!');
    console.log('🔧 Para usar autenticación: mongodb://caminando_user:caminando_secure_2025@localhost:27017/caminando_online_db');

  } catch (error) {
    console.error('❌ Error configurando admin database:', error.message);

    // Si hay error de autenticación, intentar sin credenciales primero
    if (error.message.includes('not authorized')) {
      console.log('🔄 Intentando configuración inicial sin autenticación...');
      console.log('💡 MongoDB podría necesitar configuración inicial sin auth');
      console.log('   1. Detener MongoDB');
      console.log('   2. Iniciar sin --auth: mongod --dbpath /data/db');
      console.log('   3. Ejecutar este script');
      console.log('   4. Reiniciar con autenticación: mongod --auth --dbpath /data/db');
    }
  } finally {
    await client.close();
    console.log('🔌 Conexión cerrada');
  }
}

// Ejecutar si se llama directamente
if (require.main === module) {
  initializeAdminDatabase().catch(console.error);
}

module.exports = { initializeAdminDatabase };