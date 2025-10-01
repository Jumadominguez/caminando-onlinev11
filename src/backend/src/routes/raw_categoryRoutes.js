const express = require('express');
const router = express.Router();
const categoryController = require('../controllers/raw_categoryController');

// GET /api/categories - Get all Categories with filters
router.get('/', (req, res, next) => {
  console.log('GET /api/categories called');
  next();
}, categoryController.getCategories);

// GET /api/categories/:id - Get single Category by ID
router.get('/:id', categoryController.getCategory);

// GET /api/categories/slug/:slug - Get Category by slug
router.get('/slug/:slug', categoryController.getCategoryBySlug);

// GET /api/categories/stats - Get category statistics
router.get('/stats', categoryController.getCategoryStats);

// POST /api/categories - Create a new Category
router.post('/', categoryController.createCategory);

// POST /api/categories/bulk - Bulk create Categories
router.post('/bulk', categoryController.createCategories);

// PUT /api/categories/:id - Update Category
router.put('/:id', categoryController.updateCategory);

// DELETE /api/categories/:id - Delete Category
router.delete('/:id', categoryController.deleteCategory);

// DELETE /api/categories/bulk - Bulk delete Categories
router.delete('/bulk', categoryController.deleteCategories);

// POST /api/categories/:id/sync - Sync subcategories for Category
router.post('/:id/sync', categoryController.syncSubcategories);

module.exports = router;