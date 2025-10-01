const express = require('express');
const router = express.Router();

// Import route modules
// const userRoutes = require('./userRoutes');
// const productRoutes = require('./productRoutes');
// const commerceRoutes = require('./commerceRoutes');
// const systemRoutes = require('./systemRoutes');
// const supermarketRoutes = require('./supermarketRoutes');
const productTypesRoutes = require('./raw_productTypeRoutes');

// New Carrefour raw data routes
const categoriesRoutes = require('./raw_categoryRoutes');
const subcategoriesRoutes = require('./raw_subcategoryRoutes');
const filtersRoutes = require('./raw_filterRoutes');
const offersRoutes = require('./raw_offerRoutes');
const priceHistoriesRoutes = require('./raw_priceHistoryRoutes');
const supermarketInfoRoutes = require('./raw_supermarketInfoRoutes');

// Mount routes
// router.use('/users', userRoutes);
// router.use('/products', productRoutes);
// router.use('/commerce', commerceRoutes);
// router.use('/system', systemRoutes);
// router.use('/supermarkets', supermarketRoutes);
router.use('/producttypes', productTypesRoutes);

// New Carrefour raw data endpoints
router.use('/categories', categoriesRoutes);
router.use('/subcategories', subcategoriesRoutes);
router.use('/filters', filtersRoutes);
router.use('/offers', offersRoutes);
router.use('/pricehistories', priceHistoriesRoutes);
router.use('/supermarketinfo', supermarketInfoRoutes);

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
      // users: '/api/users',
      // products: '/api/products',
      // commerce: '/api/commerce',
      // system: '/api/system',
      // supermarkets: '/api/supermarkets',
      // Carrefour raw data endpoints
      categories: '/api/categories',
      subcategories: '/api/subcategories',
      producttypes: '/api/producttypes',
      filters: '/api/filters',
      offers: '/api/offers',
      pricehistories: '/api/pricehistories',
      supermarketinfo: '/api/supermarketinfo'
    },
    docs: '/api/docs'
  });
});

module.exports = router;