const express = require('express');
const router = express.Router();
const supermarketInfoController = require('../controllers/raw_supermarketInfoController');

// GET /api/supermarketinfo - Get all SupermarketInfo entries with filters
router.get('/', (req, res, next) => {
  console.log('GET /api/supermarketinfo called');
  next();
}, supermarketInfoController.getSupermarketInfos);

// GET /api/supermarketinfo/:id - Get single SupermarketInfo by ID
router.get('/:id', supermarketInfoController.getSupermarketInfo);

// GET /api/supermarketinfo/domain/:domain - Get SupermarketInfo by domain
router.get('/domain/:domain', supermarketInfoController.getSupermarketInfoByDomain);

// GET /api/supermarketinfo/stats - Get supermarket info statistics
router.get('/stats', supermarketInfoController.getSupermarketInfoStats);

// POST /api/supermarketinfo - Create a new SupermarketInfo
router.post('/', supermarketInfoController.createSupermarketInfo);

// POST /api/supermarketinfo/bulk - Bulk create SupermarketInfo entries
router.post('/bulk', supermarketInfoController.createSupermarketInfos);

// PUT /api/supermarketinfo/:id - Update SupermarketInfo
router.put('/:id', supermarketInfoController.updateSupermarketInfo);

// DELETE /api/supermarketinfo/:id - Delete SupermarketInfo
router.delete('/:id', supermarketInfoController.deleteSupermarketInfo);

// DELETE /api/supermarketinfo/bulk - Bulk delete SupermarketInfo entries
router.delete('/bulk', supermarketInfoController.deleteSupermarketInfos);

// PATCH /api/supermarketinfo/:id/toggle - Activate/Deactivate SupermarketInfo
router.patch('/:id/toggle', supermarketInfoController.toggleSupermarketInfo);

// POST /api/supermarketinfo/:id/scraped - Update last scraped timestamp
router.post('/:id/scraped', supermarketInfoController.updateLastScraped);

// ==================== DIA ROUTES ====================

// POST /api/dia/supermarketinfo - Create a new Dia SupermarketInfo
router.post('/dia', supermarketInfoController.createDiaSupermarketInfo);

// PUT /api/dia/supermarketinfo/:id - Update Dia SupermarketInfo
router.put('/dia/:id', supermarketInfoController.updateDiaSupermarketInfo);

// PATCH /api/dia/supermarketinfo/:id/toggle - Activate/Deactivate Dia SupermarketInfo
router.patch('/dia/:id/toggle', supermarketInfoController.toggleDiaSupermarketInfo);

// POST /api/dia/supermarketinfo/:id/scraped - Update last scraped timestamp for Dia
router.post('/dia/:id/scraped', supermarketInfoController.updateDiaLastScraped);

module.exports = router;