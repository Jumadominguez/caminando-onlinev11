const express = require('express');
const router = express.Router();
const commerceController = require('../controllers/commerceController');

// Order routes
router.get('/orders', commerceController.getOrders);
router.post('/orders', commerceController.createOrder);
router.get('/orders/:id', commerceController.getOrderById);
router.put('/orders/:id/status', commerceController.updateOrderStatus);
router.put('/orders/:id/cancel', commerceController.cancelOrder);

// User orders routes
router.get('/users/:userId/orders', commerceController.getUserOrders);

// Statistics routes
router.get('/orders/stats', commerceController.getOrderStats);

module.exports = router;