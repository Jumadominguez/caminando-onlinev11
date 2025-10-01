// Controller for Supermarket-info model in carrefour_raw database
const getSupermarketInfoModel = require('../models/product_raw/carrefour_raw/carrefourSupermarketInfo');

// Controller for Supermarket-info model in dia_raw database
const { getDiaSupermarketInfoModel } = require('../models/product_raw/dia_raw/diaSupermarketInfo');

// Obtener el modelo cuando sea necesario
const getSupermarketInfo = () => getSupermarketInfoModel();

// Obtener el modelo de Dia cuando sea necesario
const getDiaSupermarketInfo = () => getDiaSupermarketInfoModel();

// ==================== SUPERMARKET INFO CONTROLLERS ====================

// Get all SupermarketInfo entries with filters
exports.getSupermarketInfos = async (req, res) => {
  try {
    console.log('getSupermarketInfos called');
    const {
      page = 1,
      limit = 20,
      active = true,
      country,
      platform,
      search,
      sort = 'name'
    } = req.query;

    let query = {};

    // Apply filters
    if (req.query.active !== undefined) {
      query.active = req.query.active === 'true';
    }
    if (country) query.country = country;
    if (platform) query.platform = platform;
    if (search) {
      query.$or = [
        { name: { $regex: search, $options: 'i' } },
        { domain: { $regex: search, $options: 'i' } },
        { platform: { $regex: search, $options: 'i' } }
      ];
    }
    // Add code filter
    if (req.query.code) query.code = req.query.code;

    const options = {
      page: parseInt(page),
      limit: parseInt(limit),
      sort: sort.startsWith('-') ? sort : `-${sort}`
    };

    console.log('Query:', query);
    console.log('Options:', options);

    const model = getSupermarketInfo();
    console.log('Using model:', model.modelName);
    console.log('Model collection:', model.collection.name);
    console.log('Model db:', model.db.name);

    const supermarketInfos = await model.find(query)
      .sort(options.sort)
      .limit(options.limit)
      .skip((options.page - 1) * options.limit);

    const total = await model.countDocuments(query);

    console.log('Found', supermarketInfos.length, 'documents, total:', total);

    res.json({
      supermarketInfos,
      pagination: {
        page: options.page,
        limit: options.limit,
        total,
        pages: Math.ceil(total / options.limit)
      }
    });
  } catch (error) {
    console.error('Error in getSupermarketInfos:', error);
    res.status(500).json({ error: error.message });
  }
};

// Get single SupermarketInfo by ID
exports.getSupermarketInfo = async (req, res) => {
  try {
    const { id } = req.params;
    console.log('getSupermarketInfo called with id:', id);

    const supermarketInfo = await getSupermarketInfo().findById(id);
    if (!supermarketInfo) {
      return res.status(404).json({ error: 'Supermarket info not found' });
    }

    res.json({ supermarketInfo });
  } catch (error) {
    console.error('Error in getSupermarketInfo:', error);
    res.status(500).json({ error: error.message });
  }
};

// Get SupermarketInfo by domain
exports.getSupermarketInfoByDomain = async (req, res) => {
  try {
    const { domain } = req.params;
    console.log('getSupermarketInfoByDomain called with domain:', domain);

    const supermarketInfo = await getSupermarketInfo().findOne({
      domain: domain,
      active: true
    });

    if (!supermarketInfo) {
      return res.status(404).json({ error: 'Supermarket info not found for this domain' });
    }

    res.json({ supermarketInfo });
  } catch (error) {
    console.error('Error in getSupermarketInfoByDomain:', error);
    res.status(500).json({ error: error.message });
  }
};

// Create new SupermarketInfo
exports.createSupermarketInfo = async (req, res) => {
  try {
    console.log('createSupermarketInfo called with body:', req.body);
    const supermarketInfoData = req.body;

    const SupermarketInfoModel = getSupermarketInfo();
    const supermarketInfo = new SupermarketInfoModel(supermarketInfoData);
    await supermarketInfo.save();

    res.status(201).json({ supermarketInfo });
  } catch (error) {
    console.error('Error in createSupermarketInfo:', error);
    res.status(500).json({ error: error.message });
  }
};

// Create multiple SupermarketInfo entries (bulk)
exports.createSupermarketInfos = async (req, res) => {
  try {
    console.log('createSupermarketInfos called with body:', req.body);
    const supermarketInfosData = req.body;

    if (!Array.isArray(supermarketInfosData)) {
      return res.status(400).json({ error: 'Body must be an array of supermarket info entries' });
    }

    const supermarketInfos = await getSupermarketInfo().insertMany(supermarketInfosData);

    res.status(201).json({ supermarketInfos, count: supermarketInfos.length });
  } catch (error) {
    console.error('Error in createSupermarketInfos:', error);
    res.status(500).json({ error: error.message });
  }
};

// Update SupermarketInfo
exports.updateSupermarketInfo = async (req, res) => {
  try {
    const { id } = req.params;
    const updateData = req.body;
    console.log('updateSupermarketInfo called with id:', id, 'data:', updateData);

    const supermarketInfo = await getSupermarketInfo().findByIdAndUpdate(
      id,
      updateData,
      { new: true, runValidators: true }
    );

    if (!supermarketInfo) {
      return res.status(404).json({ error: 'Supermarket info not found' });
    }

    res.json({ supermarketInfo });
  } catch (error) {
    console.error('Error in updateSupermarketInfo:', error);
    res.status(500).json({ error: error.message });
  }
};

// Delete SupermarketInfo
exports.deleteSupermarketInfo = async (req, res) => {
  try {
    const { id } = req.params;
    console.log('deleteSupermarketInfo called with id:', id);

    const supermarketInfo = await getSupermarketInfo().findByIdAndDelete(id);
    if (!supermarketInfo) {
      return res.status(404).json({ error: 'Supermarket info not found' });
    }

    res.json({ message: 'Supermarket info deleted successfully', supermarketInfo });
  } catch (error) {
    console.error('Error in deleteSupermarketInfo:', error);
    res.status(500).json({ error: error.message });
  }
};

// Delete multiple SupermarketInfo entries
exports.deleteSupermarketInfos = async (req, res) => {
  try {
    const { ids } = req.body;
    console.log('deleteSupermarketInfos called with ids:', ids);

    if (!Array.isArray(ids)) {
      return res.status(400).json({ error: 'Body must contain an array of ids' });
    }

    const result = await getSupermarketInfo().deleteMany({ _id: { $in: ids } });

    res.json({
      message: `${result.deletedCount} supermarket info entries deleted successfully`,
      deletedCount: result.deletedCount
    });
  } catch (error) {
    console.error('Error in deleteSupermarketInfos:', error);
    res.status(500).json({ error: error.message });
  }
};

// Get supermarket info statistics
exports.getSupermarketInfoStats = async (req, res) => {
  try {
    console.log('getSupermarketInfoStats called');

    const stats = await getSupermarketInfo().aggregate([
      {
        $group: {
          _id: null,
          totalSupermarkets: { $sum: 1 },
          activeSupermarkets: { $sum: { $cond: ['$active', 1, 0] } },
          countries: { $addToSet: '$country' },
          platforms: { $addToSet: '$platform' },
          withPWA: { $sum: { $cond: ['$pwa.enabled', 1, 0] } },
          withRegionalization: { $sum: { $cond: ['$regionalization.enabled', 1, 0] } }
        }
      },
      {
        $project: {
          totalSupermarkets: 1,
          activeSupermarkets: 1,
          uniqueCountriesCount: { $size: '$countries' },
          uniquePlatformsCount: { $size: '$platforms' },
          withPWA: 1,
          withRegionalization: 1
        }
      }
    ]);

    res.json({ stats: stats[0] || {} });
  } catch (error) {
    console.error('Error in getSupermarketInfoStats:', error);
    res.status(500).json({ error: error.message });
  }
};

// Activate/Deactivate SupermarketInfo
exports.toggleSupermarketInfo = async (req, res) => {
  try {
    const { id } = req.params;
    console.log('toggleSupermarketInfo called with id:', id);

    const supermarketInfo = await getSupermarketInfo().findById(id);
    if (!supermarketInfo) {
      return res.status(404).json({ error: 'Supermarket info not found' });
    }

    supermarketInfo.active = !supermarketInfo.active;
    await supermarketInfo.save();

    res.json({ supermarketInfo });
  } catch (error) {
    console.error('Error in toggleSupermarketInfo:', error);
    res.status(500).json({ error: error.message });
  }
};

// Update last scraped timestamp
exports.updateLastScraped = async (req, res) => {
  try {
    const { id } = req.params;
    const { type = 'products' } = req.body; // 'products' or 'homepage'
    console.log('updateLastScraped called with id:', id, 'type:', type);

    const supermarketInfo = await getSupermarketInfo().findById(id);
    if (!supermarketInfo) {
      return res.status(404).json({ error: 'Supermarket info not found' });
    }

    const now = new Date();
    if (type === 'homepage') {
      supermarketInfo.lastHomepageScraped = now;
    } else {
      supermarketInfo.lastScraped = now;
    }

    await supermarketInfo.save();

    res.json({ supermarketInfo });
  } catch (error) {
    console.error('Error in updateLastScraped:', error);
    res.status(500).json({ error: error.message });
  }
};

// ==================== DIA SUPERMARKET INFO CONTROLLERS ====================

// Create new Dia SupermarketInfo
exports.createDiaSupermarketInfo = async (req, res) => {
  try {
    console.log('createDiaSupermarketInfo called with body:', req.body);
    const supermarketInfoData = req.body;

    const DiaSupermarketInfoModel = getDiaSupermarketInfo();
    const supermarketInfo = new DiaSupermarketInfoModel(supermarketInfoData);
    await supermarketInfo.save();

    res.status(201).json({ supermarketInfo });
  } catch (error) {
    console.error('Error in createDiaSupermarketInfo:', error);
    res.status(500).json({ error: error.message });
  }
};

// Update Dia SupermarketInfo
exports.updateDiaSupermarketInfo = async (req, res) => {
  try {
    const { id } = req.params;
    const updateData = req.body;
    console.log('updateDiaSupermarketInfo called with id:', id, 'data:', updateData);

    const supermarketInfo = await getDiaSupermarketInfo().findByIdAndUpdate(
      id,
      updateData,
      { new: true, runValidators: true }
    );

    if (!supermarketInfo) {
      return res.status(404).json({ error: 'Dia supermarket info not found' });
    }

    res.json({ supermarketInfo });
  } catch (error) {
    console.error('Error in updateDiaSupermarketInfo:', error);
    res.status(500).json({ error: error.message });
  }
};

// Toggle active status for Dia SupermarketInfo
exports.toggleDiaSupermarketInfo = async (req, res) => {
  try {
    const { id } = req.params;
    console.log('toggleDiaSupermarketInfo called with id:', id);

    const supermarketInfo = await getDiaSupermarketInfo().findById(id);
    if (!supermarketInfo) {
      return res.status(404).json({ error: 'Dia supermarket info not found' });
    }

    supermarketInfo.active = !supermarketInfo.active;
    await supermarketInfo.save();

    res.json({ supermarketInfo });
  } catch (error) {
    console.error('Error in toggleDiaSupermarketInfo:', error);
    res.status(500).json({ error: error.message });
  }
};

// Update last scraped timestamp for Dia SupermarketInfo
exports.updateDiaLastScraped = async (req, res) => {
  try {
    const { id } = req.params;
    const { type = 'products' } = req.body; // 'products' or 'homepage'
    console.log('updateDiaLastScraped called with id:', id, 'type:', type);

    const supermarketInfo = await getDiaSupermarketInfo().findById(id);
    if (!supermarketInfo) {
      return res.status(404).json({ error: 'Dia supermarket info not found' });
    }

    const now = new Date();
    if (type === 'homepage') {
      supermarketInfo.lastHomepageScraped = now;
    } else {
      supermarketInfo.lastScraped = now;
    }

    await supermarketInfo.save();

    res.json({ supermarketInfo });
  } catch (error) {
    console.error('Error in updateDiaLastScraped:', error);
    res.status(500).json({ error: error.message });
  }
};
