const express = require('express');
const router = express.Router();

// Import route modules
// const userRoutes = require('./users');
// const productRoutes = require('./products');
// const categoryRoutes = require('./categories');

// router.use('/users', userRoutes);
// router.use('/products', productRoutes);
// router.use('/categories', categoryRoutes);

// Placeholder route
router.get('/', (req, res) => {
  res.json({ message: 'API is working' });
});

module.exports = router;