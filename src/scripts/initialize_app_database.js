const { MongoClient } = require('mongodb');

// Configuración de conexión
const MONGO_URI = 'mongodb://caminando_user:caminando_secure_2025@localhost:27017/caminando_online_db';
const DB_NAME = 'caminando_online_db';

async function initializeApplicationDatabase() {
  let client;

  try {
    console.log('📡 Conectando a MongoDB aplicación database...');

    // Conectar con autenticación
    client = new MongoClient(MONGO_URI);
    await client.connect();

    const db = client.db(DB_NAME);
    console.log('✅ Conectado exitosamente a caminando_online_db');

    // 1. Crear colección supermarkets con datos base
    console.log('🏪 Creando colección supermarkets...');
    const supermarketsCollection = db.collection('supermarkets');

    const supermarkets = [
      {
        _id: 'carrefour',
        name: 'Carrefour',
        baseUrl: 'https://www.carrefour.com.ar',
        logo: '🏪',
        country: 'Argentina',
        currency: 'ARS',
        active: true,
        lastScraped: null,
        scrapeConfig: {
          userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
          timeout: 30000,
          retries: 3
        }
      },
      {
        _id: 'jumbo',
        name: 'Jumbo',
        baseUrl: 'https://www.jumbo.com.ar',
        logo: '🛒',
        country: 'Argentina',
        currency: 'ARS',
        active: true,
        lastScraped: null,
        scrapeConfig: {
          userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
          timeout: 30000,
          retries: 3
        }
      },
      {
        _id: 'dia',
        name: 'Dia',
        baseUrl: 'https://www.dia.com.ar',
        logo: '🏬',
        country: 'Argentina',
        currency: 'ARS',
        active: true,
        lastScraped: null,
        scrapeConfig: {
          userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
          timeout: 30000,
          retries: 3
        }
      }
    ];

    await supermarketsCollection.insertMany(supermarkets);
    console.log('✅ Supermercados insertados');

    // 2. Crear colección categories con datos base
    console.log('📂 Creando colección categories...');
    const categoriesCollection = db.collection('categories');

    const categories = [
      {
        _id: 'alimentos',
        name: 'alimentos',
        displayName: 'Alimentos',
        description: 'Productos alimenticios y bebidas',
        icon: '🍎',
        color: '#4CAF50',
        priority: 1,
        active: true,
        featured: true,
        subcategories: [],
        metadata: { productCount: 0 }
      },
      {
        _id: 'bebidas',
        name: 'bebidas',
        displayName: 'Bebidas',
        description: 'Bebidas alcoholicas y no alcoholicas',
        icon: '🥤',
        color: '#2196F3',
        priority: 2,
        active: true,
        featured: true,
        subcategories: [],
        metadata: { productCount: 0 }
      },
      {
        _id: 'limpieza',
        name: 'limpieza',
        displayName: 'Limpieza',
        description: 'Productos de limpieza y hogar',
        icon: '🧽',
        color: '#FF9800',
        priority: 3,
        active: true,
        featured: false,
        subcategories: [],
        metadata: { productCount: 0 }
      },
      {
        _id: 'perfumeria',
        name: 'perfumeria',
        displayName: 'Perfumería',
        description: 'Cuidado personal y perfumería',
        icon: '🧴',
        color: '#E91E63',
        priority: 4,
        active: true,
        featured: false,
        subcategories: [],
        metadata: { productCount: 0 }
      }
    ];

    await categoriesCollection.insertMany(categories);
    console.log('✅ Categorías insertadas');

    // 3. Crear colecciones vacías para el resto
    console.log('📁 Creando colecciones restantes...');

    const collections = [
      'subcategories',
      'producttypes',
      'products',
      'filters',
      'offers'
    ];

    for (const collectionName of collections) {
      await db.createCollection(collectionName);
      console.log(`✅ Colección ${collectionName} creada`);
    }

    // 4. Crear índices recomendados
    console.log('🔍 Creando índices...');

    // Índices para supermarkets
    await supermarketsCollection.createIndex({ active: 1 });
    await supermarketsCollection.createIndex({ name: 1 });

    // Índices para categories
    await categoriesCollection.createIndex({ active: 1, priority: -1 });
    await categoriesCollection.createIndex({ name: 1 });
    await categoriesCollection.createIndex({ featured: 1 });

    console.log('✅ Índices creados');

    // 5. Verificar configuración
    console.log('🔍 Verificando configuración...');

    const stats = await db.stats();
    console.log(`📊 Base de datos configurada:`);
    console.log(`   • Colecciones: ${stats.collections}`);
    console.log(`   • Documentos totales: ${stats.objects}`);
    console.log(`   • Tamaño: ${(stats.dataSize / 1024 / 1024).toFixed(2)} MB`);

    console.log('🎉 Base de datos de aplicación inicializada exitosamente!');

  } catch (error) {
    console.error('❌ Error inicializando base de datos:', error.message);
    process.exit(1);
  } finally {
    if (client) {
      await client.close();
      console.log('🔌 Conexión cerrada');
    }
  }
}

// Ejecutar inicialización
initializeApplicationDatabase().catch(console.error);