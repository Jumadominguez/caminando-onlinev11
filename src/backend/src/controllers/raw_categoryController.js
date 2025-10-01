// Controller for Category model in carrefour_raw database
const Category = require('../models/product_raw/carrefour_raw/carrefourCategory');

// ==================== CATEGORY CONTROLLERS ====================

// Get all Categories with filters
exports.getCategories = async (req, res) => {
  try {
    console.log('getCategories called');
    const {
      page = 1,
      limit = 20,
      active = true,
      featured,
      search,
      sort = 'createdAt'
    } = req.query;

    let query = {};

    // Apply filters
    if (active !== undefined) query.active = active === 'true';
    if (featured !== undefined) query.featured = featured === 'true';
    if (search) {
      query.$or = [
        { name: { $regex: search, $options: 'i' } },
        { displayName: { $regex: search, $options: 'i' } },
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

    const categories = await Category.find(query)
      .sort(options.sort)
      .limit(options.limit)
      .skip((options.page - 1) * options.limit)
      .populate('subcategories', 'name slug active');

    const total = await Category.countDocuments(query);

    res.json({
      categories,
      pagination: {
        page: options.page,
        limit: options.limit,
        total,
        pages: Math.ceil(total / options.limit)
      }
    });
  } catch (error) {
    console.error('Error in getCategories:', error);
    res.status(500).json({ error: error.message });
  }
};

// Get single Category by ID
exports.getCategory = async (req, res) => {
  try {
    const { id } = req.params;
    console.log('getCategory called with id:', id);

    const category = await Category.findById(id).populate('subcategories', 'name slug active');
    if (!category) {
      return res.status(404).json({ error: 'Category not found' });
    }

    res.json({ category });
  } catch (error) {
    console.error('Error in getCategory:', error);
    res.status(500).json({ error: error.message });
  }
};

// Get Category by slug
exports.getCategoryBySlug = async (req, res) => {
  try {
    const { slug } = req.params;
    console.log('getCategoryBySlug called with slug:', slug);

    const category = await Category.findOne({ slug, active: true }).populate('subcategories', 'name slug active');
    if (!category) {
      return res.status(404).json({ error: 'Category not found' });
    }

    res.json({ category });
  } catch (error) {
    console.error('Error in getCategoryBySlug:', error);
    res.status(500).json({ error: error.message });
  }
};

// Create new Category
exports.createCategory = async (req, res) => {
  try {
    console.log('createCategory called with body:', req.body);
    const categoryData = req.body;

    const category = new Category(categoryData);
    await category.save();

    res.status(201).json({ category });
  } catch (error) {
    console.error('Error in createCategory:', error);
    if (error.code === 11000) {
      res.status(400).json({ error: 'Category with this name or slug already exists' });
    } else {
      res.status(500).json({ error: error.message });
    }
  }
};

// Create multiple Categories (bulk)
exports.createCategories = async (req, res) => {
  try {
    console.log('createCategories called with body:', req.body);
    const categoriesData = req.body;

    if (!Array.isArray(categoriesData)) {
      return res.status(400).json({ error: 'Body must be an array of categories' });
    }

    const categories = await Category.insertMany(categoriesData);

    res.status(201).json({ categories, count: categories.length });
  } catch (error) {
    console.error('Error in createCategories:', error);
    res.status(500).json({ error: error.message });
  }
};

// Update Category
exports.updateCategory = async (req, res) => {
  try {
    const { id } = req.params;
    const updateData = req.body;
    console.log('updateCategory called with id:', id, 'data:', updateData);

    const category = await Category.findByIdAndUpdate(
      id,
      updateData,
      { new: true, runValidators: true }
    ).populate('subcategories', 'name slug active');

    if (!category) {
      return res.status(404).json({ error: 'Category not found' });
    }

    res.json({ category });
  } catch (error) {
    console.error('Error in updateCategory:', error);
    if (error.code === 11000) {
      res.status(400).json({ error: 'Category with this name or slug already exists' });
    } else {
      res.status(500).json({ error: error.message });
    }
  }
};

// Delete Category
exports.deleteCategory = async (req, res) => {
  try {
    const { id } = req.params;
    console.log('deleteCategory called with id:', id);

    const category = await Category.findByIdAndDelete(id);
    if (!category) {
      return res.status(404).json({ error: 'Category not found' });
    }

    res.json({ message: 'Category deleted successfully', category });
  } catch (error) {
    console.error('Error in deleteCategory:', error);
    res.status(500).json({ error: error.message });
  }
};

// Delete multiple Categories
exports.deleteCategories = async (req, res) => {
  try {
    const { ids } = req.body;
    console.log('deleteCategories called with ids:', ids);

    if (!Array.isArray(ids)) {
      return res.status(400).json({ error: 'Body must contain an array of ids' });
    }

    const result = await Category.deleteMany({ _id: { $in: ids } });

    res.json({
      message: `${result.deletedCount} categories deleted successfully`,
      deletedCount: result.deletedCount
    });
  } catch (error) {
    console.error('Error in deleteCategories:', error);
    res.status(500).json({ error: error.message });
  }
};

// Sync subcategories for a category
exports.syncSubcategories = async (req, res) => {
  try {
    const { id } = req.params;
    console.log('syncSubcategories called with id:', id);

    const category = await Category.findById(id);
    if (!category) {
      return res.status(404).json({ error: 'Category not found' });
    }

    await category.syncSubcategories();
    await category.populate('subcategories', 'name slug active');

    res.json({ category });
  } catch (error) {
    console.error('Error in syncSubcategories:', error);
    res.status(500).json({ error: error.message });
  }
};

// Get category statistics
exports.getCategoryStats = async (req, res) => {
  try {
    console.log('getCategoryStats called');

    const stats = await Category.aggregate([
      {
        $group: {
          _id: null,
          totalCategories: { $sum: 1 },
          activeCategories: { $sum: { $cond: ['$active', 1, 0] } },
          featuredCategories: { $sum: { $cond: ['$featured', 1, 0] } },
          totalSubcategories: { $sum: { $size: '$subcategories' } }
        }
      }
    ]);

    res.json({ stats: stats[0] || {} });
  } catch (error) {
    console.error('Error in getCategoryStats:', error);
    res.status(500).json({ error: error.message });
  }
};