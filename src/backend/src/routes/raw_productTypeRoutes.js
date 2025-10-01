const express = require('express');
const router = express.Router();
const productTypeController = require('../controllers/raw_productTypeController');

// GET /api/producttypes/:supermarket - Get all ProductTypes with filters
router.get('/:supermarket', (req, res, next) => {
  console.log(`GET /api/producttypes/${req.params.supermarket} called`);
  next();
}, productTypeController.getProductTypes);

// GET /api/producttypes/:supermarket/:id - Get single ProductType by ID
router.get('/:supermarket/:id', productTypeController.getProductType);

// GET /api/producttypes/:supermarket/slug/:slug - Get ProductType by slug
router.get('/:supermarket/slug/:slug', productTypeController.getProductTypeBySlug);

// GET /api/producttypes/:supermarket/category/:categoryId/subcategory/:subcategoryId - Get ProductTypes by category and subcategory
router.get('/:supermarket/category/:categoryId/subcategory/:subcategoryId', productTypeController.getProductTypesByCategory);

// POST /api/producttypes/:supermarket - Create a new ProductType
router.post('/:supermarket', productTypeController.createProductType);

// POST /api/producttypes/:supermarket/bulk - Bulk create ProductTypes
router.post('/:supermarket/bulk', productTypeController.bulkCreateProductTypes);

// PUT /api/producttypes/:supermarket/:id - Update ProductType
router.put('/:supermarket/:id', productTypeController.updateProductType);

// DELETE /api/producttypes/:supermarket/:id - Soft delete ProductType (deactivate)
router.delete('/:supermarket/:id', productTypeController.deleteProductType);

// DELETE /api/producttypes/:supermarket/:id/hard - Hard delete ProductType
router.delete('/:supermarket/:id/hard', productTypeController.hardDeleteProductType);

// POST /api/producttypes/:supermarket/:id/sync - Sync products for ProductType
router.post('/:supermarket/:id/sync', productTypeController.syncProducts);

module.exports = router;