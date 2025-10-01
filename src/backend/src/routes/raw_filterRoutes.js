const express = require('express');
const router = express.Router();
const filterController = require('../controllers/raw_filterController');

// GET /api/filters - Get all Filters with filters
router.get('/', (req, res, next) => {
  console.log('GET /api/filters called');
  next();
}, filterController.getFilters);

// GET /api/filters/:id - Get single Filter by ID
router.get('/:id', filterController.getFilter);

// GET /api/filters/category/:categoryName - Get filters by category
router.get('/category/:categoryName', filterController.getFiltersByCategory);

// GET /api/filters/meta/categories - Get filter categories
router.get('/meta/categories', filterController.getFilterCategories);

// GET /api/filters/stats - Get filter statistics
router.get('/stats', filterController.getFilterStats);

// POST /api/filters - Create a new Filter
router.post('/', filterController.createFilter);

// POST /api/filters/bulk - Bulk create Filters
router.post('/bulk', filterController.createFilters);

// PUT /api/filters/:id - Update Filter
router.put('/:id', filterController.updateFilter);

// DELETE /api/filters/:id - Delete Filter
router.delete('/:id', filterController.deleteFilter);

// DELETE /api/filters/bulk - Bulk delete Filters
router.delete('/bulk', filterController.deleteFilters);

// PATCH /api/filters/:id/toggle - Activate/Deactivate Filter
router.patch('/:id/toggle', filterController.toggleFilter);

module.exports = router;