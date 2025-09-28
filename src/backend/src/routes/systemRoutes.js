const express = require('express');
const router = express.Router();
const systemController = require('../controllers/systemController');

// API Log routes
router.get('/logs', systemController.getApiLogs);
router.get('/logs/stats', systemController.getApiStats);

// Notification routes
router.get('/users/:userId/notifications', systemController.getUserNotifications);
router.post('/notifications', systemController.createNotification);
router.put('/users/:userId/notifications/:id/read', systemController.markNotificationAsRead);
router.put('/users/:userId/notifications/read-all', systemController.markAllNotificationsAsRead);
router.delete('/users/:userId/notifications/:id', systemController.deleteNotification);
router.get('/users/:userId/notifications/unread-count', systemController.getUnreadCount);

// System Settings routes
router.get('/settings', systemController.getSystemSettings);
router.get('/settings/:key', systemController.getSystemSetting);
router.get('/settings/category/:category', systemController.getSettingsByCategory);
router.post('/settings', systemController.setSystemSetting);
router.put('/settings/:key', systemController.updateSystemSetting);
router.delete('/settings/:key', systemController.deleteSystemSetting);
router.get('/settings/:key/value', systemController.getTypedSettingValue);

module.exports = router;