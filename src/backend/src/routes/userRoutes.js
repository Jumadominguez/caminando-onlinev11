const express = require('express');
const router = express.Router();
const userController = require('../controllers/userController');

// User routes
router.get('/users', userController.getUsers);
router.post('/users', userController.createUser);
router.get('/users/:id', userController.getUserById);
router.put('/users/:id', userController.updateUser);
router.delete('/users/:id', userController.deleteUser);

// User Address routes
router.get('/users/:userId/addresses', userController.getUserAddresses);
router.post('/users/:userId/addresses', userController.createUserAddress);
router.put('/users/:userId/addresses/:addressId', userController.updateUserAddress);
router.delete('/users/:userId/addresses/:addressId', userController.deleteUserAddress);

// User Session routes
router.get('/users/:userId/sessions', userController.getUserSessions);
router.put('/users/:userId/sessions/:sessionId/terminate', userController.terminateSession);

// Cart routes
router.get('/users/:userId/cart', userController.getUserCart);
router.post('/users/:userId/cart', userController.addToCart);
router.put('/users/:userId/cart/items/:itemId', userController.updateCartItem);
router.delete('/users/:userId/cart/items/:itemId', userController.removeFromCart);
router.delete('/users/:userId/cart', userController.clearCart);

module.exports = router;