// Controller for Subcategory model in carrefour_raw database
const Subcategory = require('../models/product_raw/carrefour_raw/carrefourSubcategory');

// ==================== SUBCATEGORY CONTROLLERS ====================

// Get all Subcategories with filters
exports.getSubcategories = async (req, res) => {
  try {
    console.log('getSubcategories called');
    const {
      page = 1,
      limit = 20,
      category,
      active = true,
      featured,
      search,
      sort = 'priority'
    } = req.query;

    let query = {};

    // Apply filters
    if (category) query.category = category;
    if (active !== undefined) query.active = active === 'true';
    if (featured !== undefined) query.featured = featured === 'true';
    if (search) {
      query.$or = [
        { name: { $regex: search, $options: 'i' } },
        { displayName: { $regex: search, $options: 'i' } },
        { description: { $regex: search, $options: 'i' } },
        { slug: { $regex: search, $options: 'i' } }
      ];
    }

    const options = {
      page: parseInt(page),
      limit: parseInt(limit),
      sort: sort.startsWith('-') ? sort : `-${sort}`
    };

    console.log('Query:', query);
    console.log('Options:', options);

    const subcategories = await Subcategory.find(query)
      .sort(options.sort)
      .limit(options.limit)
      .skip((options.page - 1) * options.limit)
      .populate('category', 'name displayName slug');

    const total = await Subcategory.countDocuments(query);

    res.json({
      subcategories,
      pagination: {
        page: options.page,
        limit: options.limit,
        total,
        pages: Math.ceil(total / options.limit)
      }
    });
  } catch (error) {
    console.error('Error in getSubcategories:', error);
    res.status(500).json({ error: error.message });
  }
};

// Get single Subcategory by ID
exports.getSubcategory = async (req, res) => {
  try {
    const { id } = req.params;
    console.log('getSubcategory called with id:', id);

    const subcategory = await Subcategory.findById(id).populate('category', 'name displayName slug');
    if (!subcategory) {
      return res.status(404).json({ error: 'Subcategory not found' });
    }

    res.json({ subcategory });
  } catch (error) {
    console.error('Error in getSubcategory:', error);
    res.status(500).json({ error: error.message });
  }
};

// Get Subcategory by slug
exports.getSubcategoryBySlug = async (req, res) => {
  try {
    const { slug } = req.params;
    console.log('getSubcategoryBySlug called with slug:', slug);

    const subcategory = await Subcategory.findOne({ slug, active: true }).populate('category', 'name displayName slug');
    if (!subcategory) {
      return res.status(404).json({ error: 'Subcategory not found' });
    }

    res.json({ subcategory });
  } catch (error) {
    console.error('Error in getSubcategoryBySlug:', error);
    res.status(500).json({ error: error.message });
  }
};

// Get subcategories by category
exports.getSubcategoriesByCategory = async (req, res) => {
  try {
    const { categoryId } = req.params;
    console.log('getSubcategoriesByCategory called with categoryId:', categoryId);

    const subcategories = await Subcategory.find({
      category: categoryId,
      active: true
    }).sort('priority').populate('category', 'name displayName slug');

    res.json({ subcategories });
  } catch (error) {
    console.error('Error in getSubcategoriesByCategory:', error);
    res.status(500).json({ error: error.message });
  }
};

// Create new Subcategory
exports.createSubcategory = async (req, res) => {
  try {
    console.log('createSubcategory called with body:', req.body);
    const subcategoryData = req.body;

    const subcategory = new Subcategory(subcategoryData);
    await subcategory.save();

    await subcategory.populate('category', 'name displayName slug');

    res.status(201).json({ subcategory });
  } catch (error) {
    console.error('Error in createSubcategory:', error);
    if (error.code === 11000) {
      res.status(400).json({ error: 'Subcategory with this slug already exists' });
    } else {
      res.status(500).json({ error: error.message });
    }
  }
};

// Create multiple Subcategories (bulk)
exports.createSubcategories = async (req, res) => {
  try {
    console.log('createSubcategories called with body:', req.body);
    const subcategoriesData = req.body;

    if (!Array.isArray(subcategoriesData)) {
      return res.status(400).json({ error: 'Body must be an array of subcategories' });
    }

    const subcategories = await Subcategory.insertMany(subcategoriesData);

    res.status(201).json({ subcategories, count: subcategories.length });
  } catch (error) {
    console.error('Error in createSubcategories:', error);
    res.status(500).json({ error: error.message });
  }
};

// Update Subcategory
exports.updateSubcategory = async (req, res) => {
  try {
    const { id } = req.params;
    const updateData = req.body;
    console.log('updateSubcategory called with id:', id, 'data:', updateData);

    const subcategory = await Subcategory.findByIdAndUpdate(
      id,
      updateData,
      { new: true, runValidators: true }
    ).populate('category', 'name displayName slug');

    if (!subcategory) {
      return res.status(404).json({ error: 'Subcategory not found' });
    }

    res.json({ subcategory });
  } catch (error) {
    console.error('Error in updateSubcategory:', error);
    if (error.code === 11000) {
      res.status(400).json({ error: 'Subcategory with this slug already exists' });
    } else {
      res.status(500).json({ error: error.message });
    }
  }
};

// Delete Subcategory
exports.deleteSubcategory = async (req, res) => {
  try {
    const { id } = req.params;
    console.log('deleteSubcategory called with id:', id);

    const subcategory = await Subcategory.findByIdAndDelete(id);
    if (!subcategory) {
      return res.status(404).json({ error: 'Subcategory not found' });
    }

    res.json({ message: 'Subcategory deleted successfully', subcategory });
  } catch (error) {
    console.error('Error in deleteSubcategory:', error);
    res.status(500).json({ error: error.message });
  }
};

// Delete multiple Subcategories
exports.deleteSubcategories = async (req, res) => {
  try {
    const { ids } = req.body;
    console.log('deleteSubcategories called with ids:', ids);

    if (!Array.isArray(ids)) {
      return res.status(400).json({ error: 'Body must contain an array of ids' });
    }

    const result = await Subcategory.deleteMany({ _id: { $in: ids } });

    res.json({
      message: `${result.deletedCount} subcategories deleted successfully`,
      deletedCount: result.deletedCount
    });
  } catch (error) {
    console.error('Error in deleteSubcategories:', error);
    res.status(500).json({ error: error.message });
  }
};

// Get subcategory statistics
exports.getSubcategoryStats = async (req, res) => {
  try {
    console.log('getSubcategoryStats called');

    const stats = await Subcategory.aggregate([
      {
        $group: {
          _id: null,
          totalSubcategories: { $sum: 1 },
          activeSubcategories: { $sum: { $cond: ['$active', 1, 0] } },
          featuredSubcategories: { $sum: { $cond: ['$featured', 1, 0] } },
          categoriesCount: { $addToSet: '$category' }
        }
      },
      {
        $project: {
          totalSubcategories: 1,
          activeSubcategories: 1,
          featuredSubcategories: 1,
          uniqueCategoriesCount: { $size: '$categoriesCount' }
        }
      }
    ]);

    res.json({ stats: stats[0] || {} });
  } catch (error) {
    console.error('Error in getSubcategoryStats:', error);
    res.status(500).json({ error: error.message });
  }
};