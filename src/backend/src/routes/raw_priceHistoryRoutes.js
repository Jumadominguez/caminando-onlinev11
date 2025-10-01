const express = require('express');
const router = express.Router();
const priceHistoryController = require('../controllers/raw_priceHistoryController');

// GET /api/pricehistories - Get all PriceHistory entries with filters
router.get('/', (req, res, next) => {
  console.log('GET /api/pricehistories called');
  next();
}, priceHistoryController.getPriceHistories);

// GET /api/pricehistories/:id - Get single PriceHistory by ID
router.get('/:id', priceHistoryController.getPriceHistory);

// GET /api/pricehistories/product/:productId - Get price history for a product
router.get('/product/:productId', priceHistoryController.getProductPriceHistory);

// GET /api/pricehistories/product/:productId/latest - Get latest price for a product
router.get('/product/:productId/latest', priceHistoryController.getLatestPrice);

// GET /api/pricehistories/product/:productId/stats - Get price statistics for a product
router.get('/product/:productId/stats', priceHistoryController.getProductPriceStats);

// GET /api/pricehistories/stats - Get price history statistics
router.get('/stats', priceHistoryController.getPriceHistoryStats);

// GET /api/pricehistories/changes - Get price change statistics
router.get('/changes', priceHistoryController.getPriceChangeStats);

// POST /api/pricehistories - Create a new PriceHistory entry
router.post('/', priceHistoryController.createPriceHistory);

// POST /api/pricehistories/bulk - Bulk create PriceHistory entries
router.post('/bulk', priceHistoryController.createPriceHistories);

// PUT /api/pricehistories/:id - Update PriceHistory
router.put('/:id', priceHistoryController.updatePriceHistory);

// DELETE /api/pricehistories/:id - Delete PriceHistory
router.delete('/:id', priceHistoryController.deletePriceHistory);

// DELETE /api/pricehistories/bulk - Bulk delete PriceHistory entries
router.delete('/bulk', priceHistoryController.deletePriceHistories);

module.exports = router;