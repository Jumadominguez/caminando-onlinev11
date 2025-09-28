// Controllers para modelos de sistema (operations database)
const ApiLog = require('../models/system/ApiLog');
const Notification = require('../models/system/Notification');
const SystemSettings = require('../models/system/SystemSettings');

// ==================== API LOG CONTROLLERS ====================

// Get API logs with filters
exports.getApiLogs = async (req, res) => {
  try {
    const {
      page = 1,
      limit = 50,
      apiType,
      method,
      statusCode,
      startDate,
      endDate,
      supermarketId
    } = req.query;

    let query = {};

    // Apply filters
    if (apiType) query.apiType = apiType;
    if (method) query.method = method;
    if (statusCode) query.statusCode = parseInt(statusCode);
    if (supermarketId) query.supermarketId = supermarketId;
    if (startDate || endDate) {
      query.timestamp = {};
      if (startDate) query.timestamp.$gte = new Date(startDate);
      if (endDate) query.timestamp.$lte = new Date(endDate);
    }

    const options = {
      page: parseInt(page),
      limit: parseInt(limit),
      sort: { timestamp: -1 }
    };

    const logs = await ApiLog.find(query)
      .sort(options.sort)
      .limit(options.limit)
      .skip((options.page - 1) * options.limit);

    const total = await ApiLog.countDocuments(query);

    res.json({
      logs,
      pagination: {
        page: options.page,
        limit: options.limit,
        total,
        pages: Math.ceil(total / options.limit)
      }
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

// Get API statistics
exports.getApiStats = async (req, res) => {
  try {
    const { startDate, endDate } = req.query;

    let matchStage = {};
    if (startDate || endDate) {
      matchStage.timestamp = {};
      if (startDate) matchStage.timestamp.$gte = new Date(startDate);
      if (endDate) matchStage.timestamp.$lte = new Date(endDate);
    }

    const stats = await ApiLog.getApiStats(matchStage);

    res.json(stats);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

// ==================== NOTIFICATION CONTROLLERS ====================

// Get notifications for a user
exports.getUserNotifications = async (req, res) => {
  try {
    const { page = 1, limit = 20, unreadOnly = false } = req.query;

    let query = { userId: req.params.userId };
    if (unreadOnly === 'true') {
      query.isRead = false;
    }

    const options = {
      page: parseInt(page),
      limit: parseInt(limit),
      sort: { createdAt: -1 }
    };

    const notifications = await Notification.find(query)
      .sort(options.sort)
      .limit(options.limit)
      .skip((options.page - 1) * options.limit);

    const total = await Notification.countDocuments(query);

    res.json({
      notifications,
      pagination: {
        page: options.page,
        limit: options.limit,
        total,
        pages: Math.ceil(total / options.limit)
      }
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

// Create notification
exports.createNotification = async (req, res) => {
  try {
    const notification = new Notification(req.body);
    await notification.save();
    res.status(201).json(notification);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
};

// Mark notification as read
exports.markNotificationAsRead = async (req, res) => {
  try {
    const notification = await Notification.findOneAndUpdate(
      { _id: req.params.id, userId: req.params.userId },
      {
        isRead: true,
        readAt: new Date()
      },
      { new: true }
    );

    if (!notification) {
      return res.status(404).json({ message: 'Notification not found' });
    }

    res.json(notification);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

// Mark all notifications as read for user
exports.markAllNotificationsAsRead = async (req, res) => {
  try {
    const result = await Notification.updateMany(
      { userId: req.params.userId, isRead: false },
      {
        isRead: true,
        readAt: new Date()
      }
    );

    res.json({
      message: `${result.modifiedCount} notifications marked as read`
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

// Delete notification
exports.deleteNotification = async (req, res) => {
  try {
    const notification = await Notification.findOneAndDelete({
      _id: req.params.id,
      userId: req.params.userId
    });

    if (!notification) {
      return res.status(404).json({ message: 'Notification not found' });
    }

    res.json({ message: 'Notification deleted successfully' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

// Get unread notification count
exports.getUnreadCount = async (req, res) => {
  try {
    const count = await Notification.getUnreadCount(req.params.userId);
    res.json({ unreadCount: count });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

// ==================== SYSTEM SETTINGS CONTROLLERS ====================

// Get all system settings
exports.getSystemSettings = async (req, res) => {
  try {
    const settings = await SystemSettings.find()
      .sort({ category: 1, key: 1 });

    res.json(settings);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

// Get system setting by key
exports.getSystemSetting = async (req, res) => {
  try {
    const setting = await SystemSettings.findOne({ key: req.params.key });

    if (!setting) {
      return res.status(404).json({ message: 'System setting not found' });
    }

    res.json(setting);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

// Get settings by category
exports.getSettingsByCategory = async (req, res) => {
  try {
    const settings = await SystemSettings.find({ category: req.params.category })
      .sort({ key: 1 });

    res.json(settings);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

// Create or update system setting
exports.setSystemSetting = async (req, res) => {
  try {
    const { key, value, type, category, description } = req.body;

    const setting = await SystemSettings.findOneAndUpdate(
      { key },
      {
        value,
        type,
        category,
        description,
        updatedAt: new Date()
      },
      {
        new: true,
        upsert: true,
        runValidators: true
      }
    );

    res.json(setting);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
};

// Update system setting
exports.updateSystemSetting = async (req, res) => {
  try {
    const setting = await SystemSettings.findOneAndUpdate(
      { key: req.params.key },
      req.body,
      { new: true, runValidators: true }
    );

    if (!setting) {
      return res.status(404).json({ message: 'System setting not found' });
    }

    res.json(setting);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
};

// Delete system setting
exports.deleteSystemSetting = async (req, res) => {
  try {
    const setting = await SystemSettings.findOneAndDelete({ key: req.params.key });

    if (!setting) {
      return res.status(404).json({ message: 'System setting not found' });
    }

    res.json({ message: 'System setting deleted successfully' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

// Get typed value of setting
exports.getTypedSettingValue = async (req, res) => {
  try {
    const setting = await SystemSettings.findOne({ key: req.params.key });

    if (!setting) {
      return res.status(404).json({ message: 'System setting not found' });
    }

    res.json({
      key: setting.key,
      value: setting.getTypedValue(),
      type: setting.type
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};