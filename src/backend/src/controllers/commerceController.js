// Controllers para modelos de comercio (operations database)
const Order = require('../models/commerce/Order');

// ==================== ORDER CONTROLLERS ====================

// Get all orders
exports.getOrders = async (req, res) => {
  try {
    const {
      page = 1,
      limit = 20,
      userId,
      status,
      supermarketId,
      startDate,
      endDate
    } = req.query;

    let query = {};

    // Apply filters
    if (userId) query.userId = userId;
    if (status) query.status = status;
    if (supermarketId) {
      query['items.supermarketId'] = supermarketId;
    }
    if (startDate || endDate) {
      query.createdAt = {};
      if (startDate) query.createdAt.$gte = new Date(startDate);
      if (endDate) query.createdAt.$lte = new Date(endDate);
    }

    const options = {
      page: parseInt(page),
      limit: parseInt(limit),
      sort: { createdAt: -1 },
      populate: [
        { path: 'userId', select: 'name email' },
        { path: 'items.productId', select: 'name image price' }
      ]
    };

    const orders = await Order.find(query)
      .populate(options.populate)
      .sort(options.sort)
      .limit(options.limit)
      .skip((options.page - 1) * options.limit);

    const total = await Order.countDocuments(query);

    res.json({
      orders,
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

// Get order by ID
exports.getOrderById = async (req, res) => {
  try {
    const order = await Order.findById(req.params.id)
      .populate('userId', 'name email phone')
      .populate('items.productId', 'name image price unit');

    if (!order) {
      return res.status(404).json({ message: 'Order not found' });
    }

    res.json(order);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

// Get orders for a specific user
exports.getUserOrders = async (req, res) => {
  try {
    const { page = 1, limit = 10 } = req.query;

    const options = {
      page: parseInt(page),
      limit: parseInt(limit),
      sort: { createdAt: -1 },
      populate: [
        { path: 'items.productId', select: 'name image price unit' }
      ]
    };

    const orders = await Order.find({ userId: req.params.userId })
      .populate(options.populate)
      .sort(options.sort)
      .limit(options.limit)
      .skip((options.page - 1) * options.limit);

    const total = await Order.countDocuments({ userId: req.params.userId });

    res.json({
      orders,
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

// Create new order
exports.createOrder = async (req, res) => {
  try {
    const order = new Order(req.body);
    await order.save();

    // Populate the created order
    await order.populate('userId', 'name email');
    await order.populate('items.productId', 'name image price unit');

    res.status(201).json(order);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
};

// Update order status
exports.updateOrderStatus = async (req, res) => {
  try {
    const { status, notes } = req.body;

    const order = await Order.findByIdAndUpdate(
      req.params.id,
      { status },
      { new: true, runValidators: true }
    );

    if (!order) {
      return res.status(404).json({ message: 'Order not found' });
    }

    // Add status change to history
    await order.addStatusChange(status, notes);

    // Populate and return updated order
    await order.populate('userId', 'name email');
    await order.populate('items.productId', 'name image price unit');

    res.json(order);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
};

// Cancel order
exports.cancelOrder = async (req, res) => {
  try {
    const { cancellationReason } = req.body;

    const order = await Order.findById(req.params.id);

    if (!order) {
      return res.status(404).json({ message: 'Order not found' });
    }

    if (['delivered', 'cancelled'].includes(order.status)) {
      return res.status(400).json({
        message: `Cannot cancel order with status: ${order.status}`
      });
    }

    await order.addStatusChange('cancelled', cancellationReason);

    res.json({ message: 'Order cancelled successfully' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

// Get order statistics
exports.getOrderStats = async (req, res) => {
  try {
    const { startDate, endDate } = req.query;

    let matchStage = {};
    if (startDate || endDate) {
      matchStage.createdAt = {};
      if (startDate) matchStage.createdAt.$gte = new Date(startDate);
      if (endDate) matchStage.createdAt.$lte = new Date(endDate);
    }

    const stats = await Order.aggregate([
      { $match: matchStage },
      {
        $group: {
          _id: null,
          totalOrders: { $sum: 1 },
          totalRevenue: { $sum: '$total' },
          averageOrderValue: { $avg: '$total' },
          ordersByStatus: {
            $push: '$status'
          }
        }
      },
      {
        $project: {
          totalOrders: 1,
          totalRevenue: { $round: ['$totalRevenue', 2] },
          averageOrderValue: { $round: ['$averageOrderValue', 2] },
          statusBreakdown: {
            $reduce: {
              input: '$ordersByStatus',
              initialValue: {},
              in: {
                $mergeObjects: [
                  '$$value',
                  {
                    $cond: {
                      if: { $ne: ['$$this', null] },
                      then: { [$$this]: { $add: [{ $getField: { field: $$this, input: '$$value' } }, 1] } },
                      else: {}
                    }
                  }
                ]
              }
            }
          }
        }
      }
    ]);

    res.json(stats[0] || {
      totalOrders: 0,
      totalRevenue: 0,
      averageOrderValue: 0,
      statusBreakdown: {}
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};