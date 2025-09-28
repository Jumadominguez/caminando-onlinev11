// Controllers para modelos de supermercado (admin database)
const Supermarket = require('../models/supermarket/Supermarket');

// ==================== SUPERMARKET CONTROLLERS ====================

// Get all supermarkets
exports.getSupermarkets = async (req, res) => {
  try {
    const { active = true } = req.query;

    const supermarkets = await Supermarket.find({ active })
      .sort({ name: 1 });

    res.json(supermarkets);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

// Get supermarket by ID
exports.getSupermarketById = async (req, res) => {
  try {
    const supermarket = await Supermarket.findById(req.params.id);

    if (!supermarket) {
      return res.status(404).json({ message: 'Supermarket not found' });
    }

    res.json(supermarket);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

// Get supermarket by code
exports.getSupermarketByCode = async (req, res) => {
  try {
    const supermarket = await Supermarket.findOne({
      code: req.params.code,
      active: true
    });

    if (!supermarket) {
      return res.status(404).json({ message: 'Supermarket not found' });
    }

    res.json(supermarket);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

// Create new supermarket
exports.createSupermarket = async (req, res) => {
  try {
    const supermarket = new Supermarket(req.body);
    await supermarket.save();
    res.status(201).json(supermarket);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
};

// Update supermarket
exports.updateSupermarket = async (req, res) => {
  try {
    const supermarket = await Supermarket.findByIdAndUpdate(
      req.params.id,
      req.body,
      { new: true, runValidators: true }
    );

    if (!supermarket) {
      return res.status(404).json({ message: 'Supermarket not found' });
    }

    res.json(supermarket);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
};

// Delete supermarket (soft delete)
exports.deleteSupermarket = async (req, res) => {
  try {
    const supermarket = await Supermarket.findByIdAndUpdate(
      req.params.id,
      { active: false },
      { new: true }
    );

    if (!supermarket) {
      return res.status(404).json({ message: 'Supermarket not found' });
    }

    res.json({ message: 'Supermarket deactivated successfully' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

// Get supermarkets by country
exports.getSupermarketsByCountry = async (req, res) => {
  try {
    const supermarkets = await Supermarket.find({
      country: req.params.country,
      active: true
    }).sort({ name: 1 });

    res.json(supermarkets);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

// Get supermarket statistics
exports.getSupermarketStats = async (req, res) => {
  try {
    const stats = await Supermarket.aggregate([
      { $match: { active: true } },
      {
        $group: {
          _id: null,
          totalSupermarkets: { $sum: 1 },
          countries: { $addToSet: '$country' },
          totalProducts: { $sum: '$productCount' },
          totalCategories: { $sum: '$categoryCount' },
          averageRating: { $avg: '$rating' }
        }
      },
      {
        $project: {
          totalSupermarkets: 1,
          uniqueCountries: { $size: '$countries' },
          totalProducts: 1,
          totalCategories: 1,
          averageRating: { $round: ['$averageRating', 2] }
        }
      }
    ]);

    res.json(stats[0] || {
      totalSupermarkets: 0,
      uniqueCountries: 0,
      totalProducts: 0,
      totalCategories: 0,
      averageRating: 0
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

// Update supermarket product count
exports.updateProductCount = async (req, res) => {
  try {
    const { productCount } = req.body;

    const supermarket = await Supermarket.findByIdAndUpdate(
      req.params.id,
      {
        productCount,
        lastProductUpdate: new Date()
      },
      { new: true }
    );

    if (!supermarket) {
      return res.status(404).json({ message: 'Supermarket not found' });
    }

    res.json(supermarket);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
};

// Update supermarket category count
exports.updateCategoryCount = async (req, res) => {
  try {
    const { categoryCount } = req.body;

    const supermarket = await Supermarket.findByIdAndUpdate(
      req.params.id,
      {
        categoryCount,
        lastCategoryUpdate: new Date()
      },
      { new: true }
    );

    if (!supermarket) {
      return res.status(404).json({ message: 'Supermarket not found' });
    }

    res.json(supermarket);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
};