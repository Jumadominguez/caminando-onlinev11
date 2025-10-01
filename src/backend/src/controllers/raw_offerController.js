// Controller for Offer model in carrefour_raw database
const Offer = require('../models/product_raw/carrefour_raw/carrefourOffer');

// ==================== OFFER CONTROLLERS ====================

// Get all Offers with filters
exports.getOffers = async (req, res) => {
  try {
    console.log('getOffers called');
    const {
      page = 1,
      limit = 20,
      supermarket,
      type,
      isActive = true,
      search,
      sort = 'priority'
    } = req.query;

    let query = {};

    // Apply filters
    if (supermarket) query.supermarket = supermarket;
    if (type) query.type = type;
    if (isActive !== undefined) query.isActive = isActive === 'true';
    if (search) {
      query.$or = [
        { title: { $regex: search, $options: 'i' } },
        { description: { $regex: search, $options: 'i' } },
        { badge: { $regex: search, $options: 'i' } }
      ];
    }

    const options = {
      page: parseInt(page),
      limit: parseInt(limit),
      sort: sort.startsWith('-') ? sort : `-${sort}`
    };

    console.log('Query:', query);
    console.log('Options:', options);

    const offers = await Offer.find(query)
      .sort(options.sort)
      .limit(options.limit)
      .skip((options.page - 1) * options.limit);

    const total = await Offer.countDocuments(query);

    res.json({
      offers,
      pagination: {
        page: options.page,
        limit: options.limit,
        total,
        pages: Math.ceil(total / options.limit)
      }
    });
  } catch (error) {
    console.error('Error in getOffers:', error);
    res.status(500).json({ error: error.message });
  }
};

// Get single Offer by ID
exports.getOffer = async (req, res) => {
  try {
    const { id } = req.params;
    console.log('getOffer called with id:', id);

    const offer = await Offer.findById(id);
    if (!offer) {
      return res.status(404).json({ error: 'Offer not found' });
    }

    res.json({ offer });
  } catch (error) {
    console.error('Error in getOffer:', error);
    res.status(500).json({ error: error.message });
  }
};

// Get active offers
exports.getActiveOffers = async (req, res) => {
  try {
    console.log('getActiveOffers called');

    const now = new Date();
    const offers = await Offer.find({
      isActive: true,
      startDate: { $lte: now },
      endDate: { $gte: now }
    }).sort('priority');

    res.json({ offers });
  } catch (error) {
    console.error('Error in getActiveOffers:', error);
    res.status(500).json({ error: error.message });
  }
};

// Get offers by supermarket
exports.getOffersBySupermarket = async (req, res) => {
  try {
    const { supermarketId } = req.params;
    console.log('getOffersBySupermarket called with supermarketId:', supermarketId);

    const offers = await Offer.find({
      supermarket: supermarketId,
      isActive: true
    }).sort('priority');

    res.json({ offers });
  } catch (error) {
    console.error('Error in getOffersBySupermarket:', error);
    res.status(500).json({ error: error.message });
  }
};

// Create new Offer
exports.createOffer = async (req, res) => {
  try {
    console.log('createOffer called with body:', req.body);
    const offerData = req.body;

    const offer = new Offer(offerData);
    await offer.save();

    res.status(201).json({ offer });
  } catch (error) {
    console.error('Error in createOffer:', error);
    res.status(500).json({ error: error.message });
  }
};

// Create multiple Offers (bulk)
exports.createOffers = async (req, res) => {
  try {
    console.log('createOffers called with body:', req.body);
    const offersData = req.body;

    if (!Array.isArray(offersData)) {
      return res.status(400).json({ error: 'Body must be an array of offers' });
    }

    const offers = await Offer.insertMany(offersData);

    res.status(201).json({ offers, count: offers.length });
  } catch (error) {
    console.error('Error in createOffers:', error);
    res.status(500).json({ error: error.message });
  }
};

// Update Offer
exports.updateOffer = async (req, res) => {
  try {
    const { id } = req.params;
    const updateData = req.body;
    console.log('updateOffer called with id:', id, 'data:', updateData);

    const offer = await Offer.findByIdAndUpdate(
      id,
      updateData,
      { new: true, runValidators: true }
    );

    if (!offer) {
      return res.status(404).json({ error: 'Offer not found' });
    }

    res.json({ offer });
  } catch (error) {
    console.error('Error in updateOffer:', error);
    res.status(500).json({ error: error.message });
  }
};

// Delete Offer
exports.deleteOffer = async (req, res) => {
  try {
    const { id } = req.params;
    console.log('deleteOffer called with id:', id);

    const offer = await Offer.findByIdAndDelete(id);
    if (!offer) {
      return res.status(404).json({ error: 'Offer not found' });
    }

    res.json({ message: 'Offer deleted successfully', offer });
  } catch (error) {
    console.error('Error in deleteOffer:', error);
    res.status(500).json({ error: error.message });
  }
};

// Delete multiple Offers
exports.deleteOffers = async (req, res) => {
  try {
    const { ids } = req.body;
    console.log('deleteOffers called with ids:', ids);

    if (!Array.isArray(ids)) {
      return res.status(400).json({ error: 'Body must contain an array of ids' });
    }

    const result = await Offer.deleteMany({ _id: { $in: ids } });

    res.json({
      message: `${result.deletedCount} offers deleted successfully`,
      deletedCount: result.deletedCount
    });
  } catch (error) {
    console.error('Error in deleteOffers:', error);
    res.status(500).json({ error: error.message });
  }
};

// Get offer statistics
exports.getOfferStats = async (req, res) => {
  try {
    console.log('getOfferStats called');

    const stats = await Offer.aggregate([
      {
        $group: {
          _id: null,
          totalOffers: { $sum: 1 },
          activeOffers: { $sum: { $cond: ['$isActive', 1, 0] } },
          supermarkets: { $addToSet: '$supermarket' },
          types: { $addToSet: '$type' },
          totalUsage: { $sum: '$currentUsage' },
          totalSavings: { $sum: '$metadata.totalSavings' }
        }
      },
      {
        $project: {
          totalOffers: 1,
          activeOffers: 1,
          uniqueSupermarketsCount: { $size: '$supermarkets' },
          uniqueTypesCount: { $size: '$types' },
          totalUsage: 1,
          totalSavings: 1
        }
      }
    ]);

    res.json({ stats: stats[0] || {} });
  } catch (error) {
    console.error('Error in getOfferStats:', error);
    res.status(500).json({ error: error.message });
  }
};

// Activate/Deactivate Offer
exports.toggleOffer = async (req, res) => {
  try {
    const { id } = req.params;
    console.log('toggleOffer called with id:', id);

    const offer = await Offer.findById(id);
    if (!offer) {
      return res.status(404).json({ error: 'Offer not found' });
    }

    offer.isActive = !offer.isActive;
    await offer.save();

    res.json({ offer });
  } catch (error) {
    console.error('Error in toggleOffer:', error);
    res.status(500).json({ error: error.message });
  }
};

// Check if offer is valid
exports.validateOffer = async (req, res) => {
  try {
    const { id } = req.params;
    console.log('validateOffer called with id:', id);

    const offer = await Offer.findById(id);
    if (!offer) {
      return res.status(404).json({ error: 'Offer not found' });
    }

    const isValid = offer.isValid();
    res.json({ offer, isValid });
  } catch (error) {
    console.error('Error in validateOffer:', error);
    res.status(500).json({ error: error.message });
  }
};