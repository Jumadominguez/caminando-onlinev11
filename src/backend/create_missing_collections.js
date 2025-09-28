const { MongoClient } = require('mongodb');

// Configuración de conexión - Sin autenticación para inicialización
const MONGO_URI = 'mongodb://localhost:27017/caminando_online_db';
const DB_NAME = 'caminando_online_db';

async function createMissingCollections() {
  let client;

  try {
    console.log('🔍 Verificando colecciones existentes...');

    client = new MongoClient(MONGO_URI);
    await client.connect();

    const db = client.db(DB_NAME);
    console.log('✅ Conectado exitosamente a caminando_online_db');

    // Obtener colecciones existentes
    const existingCollections = await db.listCollections().toArray();
    const existingNames = existingCollections.map(col => col.name);

    console.log('📋 Colecciones existentes:', existingNames);

    // Colecciones que deberían existir
    const requiredCollections = [
      'users', // 👤 Usuarios de la plataforma
      'orders', // 📦 Pedidos de usuarios
      'carts', // 🛒 Carritos de compra
      'price_history', // 📈 Historial de precios
      'user_addresses', // 📍 Direcciones de entrega
      'notifications', // 🔔 Notificaciones del sistema
      'user_sessions', // 🔐 Sesiones activas
      'api_logs', // 📊 Logs de APIs externas
      'system_settings', // ⚙️ Configuraciones del sistema
      'supermarkets',
      'categories',
      'subcategories',
      'producttypes',
      'products',
      'filters',
      'offers'
    ];

    // Crear colecciones faltantes
    const missingCollections = requiredCollections.filter(col => !existingNames.includes(col));

    if (missingCollections.length === 0) {
      console.log('✅ Todas las colecciones ya existen!');
      return;
    }

    console.log('📁 Creando colecciones faltantes:', missingCollections);

    for (const collectionName of missingCollections) {
      await db.createCollection(collectionName);
      console.log(`✅ Colección ${collectionName} creada`);
    }

    // Verificar resultado final
    const finalCollections = await db.listCollections().toArray();
    const finalNames = finalCollections.map(col => col.name);

    console.log('\n📊 Estado final de colecciones:');
    console.log(`   • Total: ${finalNames.length}`);
    console.log(`   • Nuevas creadas: ${missingCollections.length}`);
    console.log(`   • Existentes: ${existingNames.length}`);

    console.log('🎉 Verificación y creación completada!');

  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  } finally {
    if (client) {
      await client.close();
      console.log('🔌 Conexión cerrada');
    }
  }
}

// Ejecutar verificación
createMissingCollections().catch(console.error);