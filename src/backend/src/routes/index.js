const express = require('express');
const router = express.Router();

// Import route modules
const userRoutes = require('./userRoutes');
const productRoutes = require('./productRoutes');
const commerceRoutes = require('./commerceRoutes');
const systemRoutes = require('./systemRoutes');
const supermarketRoutes = require('./supermarketRoutes');

// Mount routes
router.use('/users', userRoutes);
router.use('/products', productRoutes);
router.use('/commerce', commerceRoutes);
router.use('/system', systemRoutes);
router.use('/supermarkets', supermarketRoutes);

// Health check route
router.get('/health', (req, res) => {
  res.json({
    status: 'OK',
    message: 'API is working',
    timestamp: new Date().toISOString(),
    version: '1.0.0'
  });
});

// API info route
router.get('/', (req, res) => {
  res.json({
    message: 'Caminando Online API v1.0.0',
    version: '1.0.0',
    endpoints: {
      users: '/api/users',
      products: '/api/products',
      commerce: '/api/commerce',
      system: '/api/system',
      supermarkets: '/api/supermarkets'
    },
    docs: '/api/docs'
  });
});

module.exports = router;