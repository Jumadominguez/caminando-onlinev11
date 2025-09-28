const express = require('express');
const router = express.Router();
const productController = require('../controllers/productController');

// Product routes
router.get('/products', productController.getProducts);
router.post('/products', productController.createProduct);
router.get('/products/:id', productController.getProductById);
router.put('/products/:id', productController.updateProduct);
router.delete('/products/:id', productController.deleteProduct);

// Category routes
router.get('/categories', productController.getCategories);
router.get('/categories/:id', productController.getCategoryById);
router.post('/categories', productController.createCategory);

// Subcategory routes
router.get('/subcategories', productController.getSubcategories);
router.get('/subcategories/:id', productController.getSubcategoryById);

// Product Type routes
router.get('/product-types', productController.getProductTypes);
router.get('/product-types/:id', productController.getProductTypeById);

// Offer routes
router.get('/offers', productController.getOffers);
router.get('/offers/:id', productController.getOfferById);

// Filter routes
router.get('/filters', productController.getFilters);

// Price History routes
router.get('/products/:productId/price-history', productController.getPriceHistory);
router.get('/products/:productId/price-stats', productController.getPriceStats);

module.exports = router;