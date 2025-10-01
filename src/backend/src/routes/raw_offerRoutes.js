const express = require('express');
const router = express.Router();
const offerController = require('../controllers/raw_offerController');

// GET /api/offers - Get all Offers with filters
router.get('/', (req, res, next) => {
  console.log('GET /api/offers called');
  next();
}, offerController.getOffers);

// GET /api/offers/:id - Get single Offer by ID
router.get('/:id', offerController.getOffer);

// GET /api/offers/active - Get active offers
router.get('/active', offerController.getActiveOffers);

// GET /api/offers/supermarket/:supermarketId - Get offers by supermarket
router.get('/supermarket/:supermarketId', offerController.getOffersBySupermarket);

// GET /api/offers/stats - Get offer statistics
router.get('/stats', offerController.getOfferStats);

// POST /api/offers - Create a new Offer
router.post('/', offerController.createOffer);

// POST /api/offers/bulk - Bulk create Offers
router.post('/bulk', offerController.createOffers);

// PUT /api/offers/:id - Update Offer
router.put('/:id', offerController.updateOffer);

// DELETE /api/offers/:id - Delete Offer
router.delete('/:id', offerController.deleteOffer);

// DELETE /api/offers/bulk - Bulk delete Offers
router.delete('/bulk', offerController.deleteOffers);

// PATCH /api/offers/:id/toggle - Activate/Deactivate Offer
router.patch('/:id/toggle', offerController.toggleOffer);

// GET /api/offers/:id/validate - Check if offer is valid
router.get('/:id/validate', offerController.validateOffer);

module.exports = router;