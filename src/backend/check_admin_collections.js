const mongoose = require('mongoose');
require('dotenv').config();

async function checkCollections() {
  try {
    const conn = await mongoose.createConnection(process.env.MONGO_ADMIN_URI);
    const collections = await conn.db.listCollections().toArray();
    console.log('📋 Collections in admin database:');
    collections.forEach(col => console.log('  -', col.name));
    await conn.close();
  } catch (error) {
    console.error('❌ Error:', error.message);
  }
}

checkCollections();