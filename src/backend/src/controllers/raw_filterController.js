// Controller for Filter model in carrefour_raw database
const Filter = require('../models/product_raw/carrefour_raw/carrefourFilter');

// ==================== FILTER CONTROLLERS ====================

// Get all Filters with filters
exports.getFilters = async (req, res) => {
  try {
    console.log('getFilters called');
    const {
      page = 1,
      limit = 20,
      category,
      type,
      active = true,
      search,
      sort = 'priority'
    } = req.query;

    let query = {};

    // Apply filters
    if (category) query.category = category;
    if (type) query.type = type;
    if (active !== undefined) query.active = active === 'true';
    if (search) {
      query.$or = [
        { name: { $regex: search, $options: 'i' } },
        { displayName: { $regex: search, $options: 'i' } },
        { description: { $regex: search, $options: 'i' } }
      ];
    }

    const options = {
      page: parseInt(page),
      limit: parseInt(limit),
      sort: sort.startsWith('-') ? sort : `-${sort}`
    };

    console.log('Query:', query);
    console.log('Options:', options);

    const filters = await Filter.find(query)
      .sort(options.sort)
      .limit(options.limit)
      .skip((options.page - 1) * options.limit);

    const total = await Filter.countDocuments(query);

    res.json({
      filters,
      pagination: {
        page: options.page,
        limit: options.limit,
        total,
        pages: Math.ceil(total / options.limit)
      }
    });
  } catch (error) {
    console.error('Error in getFilters:', error);
    res.status(500).json({ error: error.message });
  }
};

// Get single Filter by ID
exports.getFilter = async (req, res) => {
  try {
    const { id } = req.params;
    console.log('getFilter called with id:', id);

    const filter = await Filter.findById(id);
    if (!filter) {
      return res.status(404).json({ error: 'Filter not found' });
    }

    res.json({ filter });
  } catch (error) {
    console.error('Error in getFilter:', error);
    res.status(500).json({ error: error.message });
  }
};

// Get filters by category
exports.getFiltersByCategory = async (req, res) => {
  try {
    const { categoryName } = req.params;
    console.log('getFiltersByCategory called with categoryName:', categoryName);

    const filters = await Filter.find({
      applicableCategories: categoryName,
      active: true
    }).sort('priority');

    res.json({ filters });
  } catch (error) {
    console.error('Error in getFiltersByCategory:', error);
    res.status(500).json({ error: error.message });
  }
};

// Get filter categories
exports.getFilterCategories = async (req, res) => {
  try {
    console.log('getFilterCategories called');

    const categories = await Filter.distinct('category', { active: true });

    res.json({ categories });
  } catch (error) {
    console.error('Error in getFilterCategories:', error);
    res.status(500).json({ error: error.message });
  }
};

// Create new Filter
exports.createFilter = async (req, res) => {
  try {
    console.log('createFilter called with body:', req.body);
    const filterData = req.body;

    const filter = new Filter(filterData);
    await filter.save();

    res.status(201).json({ filter });
  } catch (error) {
    console.error('Error in createFilter:', error);
    if (error.code === 11000) {
      res.status(400).json({ error: 'Filter with this name already exists' });
    } else {
      res.status(500).json({ error: error.message });
    }
  }
};

// Create multiple Filters (bulk)
exports.createFilters = async (req, res) => {
  try {
    console.log('createFilters called with body:', req.body);
    const filtersData = req.body;

    if (!Array.isArray(filtersData)) {
      return res.status(400).json({ error: 'Body must be an array of filters' });
    }

    const filters = await Filter.insertMany(filtersData);

    res.status(201).json({ filters, count: filters.length });
  } catch (error) {
    console.error('Error in createFilters:', error);
    res.status(500).json({ error: error.message });
  }
};

// Update Filter
exports.updateFilter = async (req, res) => {
  try {
    const { id } = req.params;
    const updateData = req.body;
    console.log('updateFilter called with id:', id, 'data:', updateData);

    const filter = await Filter.findByIdAndUpdate(
      id,
      updateData,
      { new: true, runValidators: true }
    );

    if (!filter) {
      return res.status(404).json({ error: 'Filter not found' });
    }

    res.json({ filter });
  } catch (error) {
    console.error('Error in updateFilter:', error);
    if (error.code === 11000) {
      res.status(400).json({ error: 'Filter with this name already exists' });
    } else {
      res.status(500).json({ error: error.message });
    }
  }
};

// Delete Filter
exports.deleteFilter = async (req, res) => {
  try {
    const { id } = req.params;
    console.log('deleteFilter called with id:', id);

    const filter = await Filter.findByIdAndDelete(id);
    if (!filter) {
      return res.status(404).json({ error: 'Filter not found' });
    }

    res.json({ message: 'Filter deleted successfully', filter });
  } catch (error) {
    console.error('Error in deleteFilter:', error);
    res.status(500).json({ error: error.message });
  }
};

// Delete multiple Filters
exports.deleteFilters = async (req, res) => {
  try {
    const { ids } = req.body;
    console.log('deleteFilters called with ids:', ids);

    if (!Array.isArray(ids)) {
      return res.status(400).json({ error: 'Body must contain an array of ids' });
    }

    const result = await Filter.deleteMany({ _id: { $in: ids } });

    res.json({
      message: `${result.deletedCount} filters deleted successfully`,
      deletedCount: result.deletedCount
    });
  } catch (error) {
    console.error('Error in deleteFilters:', error);
    res.status(500).json({ error: error.message });
  }
};

// Get filter statistics
exports.getFilterStats = async (req, res) => {
  try {
    console.log('getFilterStats called');

    const stats = await Filter.aggregate([
      {
        $group: {
          _id: null,
          totalFilters: { $sum: 1 },
          activeFilters: { $sum: { $cond: ['$active', 1, 0] } },
          categories: { $addToSet: '$category' },
          types: { $addToSet: '$type' }
        }
      },
      {
        $project: {
          totalFilters: 1,
          activeFilters: 1,
          uniqueCategoriesCount: { $size: '$categories' },
          uniqueTypesCount: { $size: '$types' }
        }
      }
    ]);

    res.json({ stats: stats[0] || {} });
  } catch (error) {
    console.error('Error in getFilterStats:', error);
    res.status(500).json({ error: error.message });
  }
};

// Activate/Deactivate Filter
exports.toggleFilter = async (req, res) => {
  try {
    const { id } = req.params;
    console.log('toggleFilter called with id:', id);

    const filter = await Filter.findById(id);
    if (!filter) {
      return res.status(404).json({ error: 'Filter not found' });
    }

    filter.active = !filter.active;
    await filter.save();

    res.json({ filter });
  } catch (error) {
    console.error('Error in toggleFilter:', error);
    res.status(500).json({ error: error.message });
  }
};