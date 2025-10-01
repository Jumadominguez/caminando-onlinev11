const express = require('express');
const router = express.Router();
const carrefourProductController = require('../controllers/carrefourProductController');

// GET /api/products - Get all Products with filters (Carrefour)
router.get('/', (req, res, next) => {
  console.log('GET /api/products called (Carrefour)');
  next();
}, carrefourProductController.getProducts);

// GET /api/products/:id - Get single Product by ID
router.get('/:id', carrefourProductController.getProduct);

// GET /api/products/category/:categoryId/subcategory/:subcategoryId - Get products by category and subcategory
router.get('/category/:categoryId/subcategory/:subcategoryId', carrefourProductController.getProductsByCategory);

// GET /api/products/stats - Get product statistics
router.get('/stats', carrefourProductController.getProductStats);

// GET /api/products/offers - Get products on offer
router.get('/offers', carrefourProductController.getProductsOnOffer);

// POST /api/products - Create a new Product
router.post('/', carrefourProductController.createProduct);

// POST /api/products/bulk - Bulk create Products
router.post('/bulk', carrefourProductController.createProducts);

// POST /api/products/filters - Get products by filters
router.post('/filters', carrefourProductController.getProductsByFilters);

// PUT /api/products/:id - Update Product
router.put('/:id', carrefourProductController.updateProduct);

// DELETE /api/products/:id - Delete Product
router.delete('/:id', carrefourProductController.deleteProduct);

// DELETE /api/products/bulk - Bulk delete Products
router.delete('/bulk', carrefourProductController.deleteProducts);

module.exports = router;