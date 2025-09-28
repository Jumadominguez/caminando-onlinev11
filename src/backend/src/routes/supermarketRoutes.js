const express = require('express');
const router = express.Router();
const supermarketController = require('../controllers/supermarketController');

// Supermarket routes
router.get('/supermarkets', supermarketController.getSupermarkets);
router.post('/supermarkets', supermarketController.createSupermarket);
router.get('/supermarkets/:id', supermarketController.getSupermarketById);
router.get('/supermarkets/code/:code', supermarketController.getSupermarketByCode);
router.put('/supermarkets/:id', supermarketController.updateSupermarket);
router.delete('/supermarkets/:id', supermarketController.deleteSupermarket);

// Country-based routes
router.get('/supermarkets/country/:country', supermarketController.getSupermarketsByCountry);

// Statistics routes
router.get('/supermarkets/stats', supermarketController.getSupermarketStats);

// Update count routes
router.put('/supermarkets/:id/product-count', supermarketController.updateProductCount);
router.put('/supermarkets/:id/category-count', supermarketController.updateCategoryCount);

module.exports = router;