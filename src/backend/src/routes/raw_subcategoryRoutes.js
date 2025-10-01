const express = require('express');
const router = express.Router();
const subcategoryController = require('../controllers/raw_subcategoryController');

// GET /api/subcategories - Get all Subcategories with filters
router.get('/', (req, res, next) => {
  console.log('GET /api/subcategories called');
  next();
}, subcategoryController.getSubcategories);

// GET /api/subcategories/:id - Get single Subcategory by ID
router.get('/:id', subcategoryController.getSubcategory);

// GET /api/subcategories/slug/:slug - Get Subcategory by slug
router.get('/slug/:slug', subcategoryController.getSubcategoryBySlug);

// GET /api/subcategories/category/:categoryId - Get subcategories by category
router.get('/category/:categoryId', subcategoryController.getSubcategoriesByCategory);

// GET /api/subcategories/stats - Get subcategory statistics
router.get('/stats', subcategoryController.getSubcategoryStats);

// POST /api/subcategories - Create a new Subcategory
router.post('/', subcategoryController.createSubcategory);

// POST /api/subcategories/bulk - Bulk create Subcategories
router.post('/bulk', subcategoryController.createSubcategories);

// PUT /api/subcategories/:id - Update Subcategory
router.put('/:id', subcategoryController.updateSubcategory);

// DELETE /api/subcategories/:id - Delete Subcategory
router.delete('/:id', subcategoryController.deleteSubcategory);

// DELETE /api/subcategories/bulk - Bulk delete Subcategories
router.delete('/bulk', subcategoryController.deleteSubcategories);

module.exports = router;