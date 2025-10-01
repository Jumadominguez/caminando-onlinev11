// Controller for PriceHistory model in carrefour_raw database
const PriceHistory = require('../models/product_raw/carrefour_raw/carrefourPriceHistory');

// ==================== PRICE HISTORY CONTROLLERS ====================

// Get all PriceHistory entries with filters
exports.getPriceHistories = async (req, res) => {
  try {
    console.log('getPriceHistories called');
    const {
      page = 1,
      limit = 20,
      productId,
      supermarketId,
      category,
      brand,
      startDate,
      endDate,
      isOnOffer,
      sort = 'scrapedAt'
    } = req.query;

    let query = {};

    // Apply filters
    if (productId) query.productId = productId;
    if (supermarketId) query.supermarketId = supermarketId;
    if (category) query['productData.category'] = category;
    if (brand) query['productData.brand'] = brand;
    if (isOnOffer !== undefined) query.isOnOffer = isOnOffer === 'true';
    if (startDate || endDate) {
      query.scrapedAt = {};
      if (startDate) query.scrapedAt.$gte = new Date(startDate);
      if (endDate) query.scrapedAt.$lte = new Date(endDate);
    }

    const options = {
      page: parseInt(page),
      limit: parseInt(limit),
      sort: sort.startsWith('-') ? sort : `-${sort}`
    };

    console.log('Query:', query);
    console.log('Options:', options);

    const priceHistories = await PriceHistory.find(query)
      .sort(options.sort)
      .limit(options.limit)
      .skip((options.page - 1) * options.limit)
      .populate('productId', 'name brand category');

    const total = await PriceHistory.countDocuments(query);

    res.json({
      priceHistories,
      pagination: {
        page: options.page,
        limit: options.limit,
        total,
        pages: Math.ceil(total / options.limit)
      }
    });
  } catch (error) {
    console.error('Error in getPriceHistories:', error);
    res.status(500).json({ error: error.message });
  }
};

// Get single PriceHistory by ID
exports.getPriceHistory = async (req, res) => {
  try {
    const { id } = req.params;
    console.log('getPriceHistory called with id:', id);

    const priceHistory = await PriceHistory.findById(id).populate('productId', 'name brand category');
    if (!priceHistory) {
      return res.status(404).json({ error: 'Price history not found' });
    }

    res.json({ priceHistory });
  } catch (error) {
    console.error('Error in getPriceHistory:', error);
    res.status(500).json({ error: error.message });
  }
};

// Get price history for a specific product
exports.getProductPriceHistory = async (req, res) => {
  try {
    const { productId } = req.params;
    const { limit = 50, supermarketId } = req.query;
    console.log('getProductPriceHistory called with productId:', productId);

    const priceHistories = await PriceHistory.getPriceHistory(productId, supermarketId, parseInt(limit));

    res.json({ priceHistories });
  } catch (error) {
    console.error('Error in getProductPriceHistory:', error);
    res.status(500).json({ error: error.message });
  }
};

// Get latest price for a product
exports.getLatestPrice = async (req, res) => {
  try {
    const { productId } = req.params;
    const { supermarketId } = req.query;
    console.log('getLatestPrice called with productId:', productId);

    const latestPrice = await PriceHistory.getLatestPrice(productId, supermarketId);

    if (!latestPrice) {
      return res.status(404).json({ error: 'No price history found for this product' });
    }

    res.json({ latestPrice });
  } catch (error) {
    console.error('Error in getLatestPrice:', error);
    res.status(500).json({ error: error.message });
  }
};

// Create new PriceHistory entry
exports.createPriceHistory = async (req, res) => {
  try {
    console.log('createPriceHistory called with body:', req.body);
    const priceHistoryData = req.body;

    const priceHistory = new PriceHistory(priceHistoryData);
    await priceHistory.save();

    await priceHistory.populate('productId', 'name brand category');

    res.status(201).json({ priceHistory });
  } catch (error) {
    console.error('Error in createPriceHistory:', error);
    res.status(500).json({ error: error.message });
  }
};

// Create multiple PriceHistory entries (bulk)
exports.createPriceHistories = async (req, res) => {
  try {
    console.log('createPriceHistories called with body:', req.body);
    const priceHistoriesData = req.body;

    if (!Array.isArray(priceHistoriesData)) {
      return res.status(400).json({ error: 'Body must be an array of price history entries' });
    }

    const priceHistories = await PriceHistory.insertMany(priceHistoriesData);

    res.status(201).json({ priceHistories, count: priceHistories.length });
  } catch (error) {
    console.error('Error in createPriceHistories:', error);
    res.status(500).json({ error: error.message });
  }
};

// Update PriceHistory
exports.updatePriceHistory = async (req, res) => {
  try {
    const { id } = req.params;
    const updateData = req.body;
    console.log('updatePriceHistory called with id:', id, 'data:', updateData);

    const priceHistory = await PriceHistory.findByIdAndUpdate(
      id,
      updateData,
      { new: true, runValidators: true }
    ).populate('productId', 'name brand category');

    if (!priceHistory) {
      return res.status(404).json({ error: 'Price history not found' });
    }

    res.json({ priceHistory });
  } catch (error) {
    console.error('Error in updatePriceHistory:', error);
    res.status(500).json({ error: error.message });
  }
};

// Delete PriceHistory
exports.deletePriceHistory = async (req, res) => {
  try {
    const { id } = req.params;
    console.log('deletePriceHistory called with id:', id);

    const priceHistory = await PriceHistory.findByIdAndDelete(id);
    if (!priceHistory) {
      return res.status(404).json({ error: 'Price history not found' });
    }

    res.json({ message: 'Price history deleted successfully', priceHistory });
  } catch (error) {
    console.error('Error in deletePriceHistory:', error);
    res.status(500).json({ error: error.message });
  }
};

// Delete multiple PriceHistory entries
exports.deletePriceHistories = async (req, res) => {
  try {
    const { ids } = req.body;
    console.log('deletePriceHistories called with ids:', ids);

    if (!Array.isArray(ids)) {
      return res.status(400).json({ error: 'Body must contain an array of ids' });
    }

    const result = await PriceHistory.deleteMany({ _id: { $in: ids } });

    res.json({
      message: `${result.deletedCount} price history entries deleted successfully`,
      deletedCount: result.deletedCount
    });
  } catch (error) {
    console.error('Error in deletePriceHistories:', error);
    res.status(500).json({ error: error.message });
  }
};

// Get price change statistics
exports.getPriceChangeStats = async (req, res) => {
  try {
    const { hoursBack = 24 } = req.query;
    console.log('getPriceChangeStats called with hoursBack:', hoursBack);

    const changes = await PriceHistory.detectPriceChanges(parseInt(hoursBack));

    res.json({ changes });
  } catch (error) {
    console.error('Error in getPriceChangeStats:', error);
    res.status(500).json({ error: error.message });
  }
};

// Get price statistics for a product
exports.getProductPriceStats = async (req, res) => {
  try {
    const { productId } = req.params;
    const { supermarketId, days = 30 } = req.query;
    console.log('getProductPriceStats called with productId:', productId);

    const stats = await PriceHistory.getPriceStats(productId, supermarketId, parseInt(days));

    res.json({ stats });
  } catch (error) {
    console.error('Error in getProductPriceStats:', error);
    res.status(500).json({ error: error.message });
  }
};

// Get price history statistics
exports.getPriceHistoryStats = async (req, res) => {
  try {
    console.log('getPriceHistoryStats called');

    const stats = await PriceHistory.aggregate([
      {
        $group: {
          _id: null,
          totalEntries: { $sum: 1 },
          uniqueProducts: { $addToSet: '$productId' },
          supermarkets: { $addToSet: '$supermarketId' },
          averagePrice: { $avg: '$price' },
          minPrice: { $min: '$price' },
          maxPrice: { $max: '$price' },
          onOfferCount: { $sum: { $cond: ['$isOnOffer', 1, 0] } }
        }
      },
      {
        $project: {
          totalEntries: 1,
          uniqueProductsCount: { $size: '$uniqueProducts' },
          uniqueSupermarketsCount: { $size: '$supermarkets' },
          averagePrice: { $round: ['$averagePrice', 2] },
          minPrice: 1,
          maxPrice: 1,
          onOfferCount: 1
        }
      }
    ]);

    res.json({ stats: stats[0] || {} });
  } catch (error) {
    console.error('Error in getPriceHistoryStats:', error);
    res.status(500).json({ error: error.message });
  }
};