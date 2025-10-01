// Generic Controller for ProductType model across all supermarket_raw databases

// Valid supermarkets
const validSupermarkets = ['carrefour', 'dia', 'jumbo', 'vea', 'disco'];

// Helper function to get ProductType model for a supermarket
function getProductTypeModel(supermarket) {
  if (!validSupermarkets.includes(supermarket)) {
    throw new Error('Invalid supermarket');
  }

  const connection = global.databaseConnections[supermarket];
  if (!connection) {
    throw new Error(`Database connection for ${supermarket} not found`);
  }

  const ProductTypeFactory = require(`../models/product_raw/${supermarket}_raw/ProductType`);
  return ProductTypeFactory(connection);
}

// ==================== PRODUCT TYPE CONTROLLERS ====================

// Get all ProductTypes with filters
exports.getProductTypes = async (req, res) => {
  try {
    const { supermarket } = req.params;
    const ProductType = getProductTypeModel(supermarket);

    console.log(`getProductTypes called for ${supermarket}`);
    const {
      page = 1,
      limit = 20,
      category,
      subcategory,
      active = true,
      featured,
      search,
      sort = 'priority'
    } = req.query;

    let query = {};

    // Apply filters
    if (category) query.category = category;
    if (subcategory) query.subcategory = subcategory;
    if (active !== undefined) query.active = active === 'true';
    if (featured !== undefined) query.featured = featured === 'true';
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

    const productTypes = await ProductType.find(query)
      .sort(options.sort)
      .limit(options.limit)
      .skip((options.page - 1) * options.limit)
      .populate('products', 'name price');

    const total = await ProductType.countDocuments(query);

    console.log('Found productTypes:', productTypes.length, 'total:', total);

    res.json({
      productTypes,
      pagination: {
        page: options.page,
        limit: options.limit,
        total,
        pages: Math.ceil(total / options.limit)
      }
    });
  } catch (error) {
    console.error('Error in getProductTypes:', error);
    res.status(500).json({ error: error.message });
  }
};

// Get single ProductType by ID
exports.getProductType = async (req, res) => {
  try {
    const { supermarket } = req.params;
    const ProductType = getProductTypeModel(supermarket);

    const productType = await ProductType.findById(req.params.id)
      .populate('products', 'name price imageUrl');

    if (!productType) {
      return res.status(404).json({ error: 'ProductType not found' });
    }

    res.json(productType);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

// Get ProductType by slug
exports.getProductTypeBySlug = async (req, res) => {
  try {
    const { supermarket } = req.params;
    const ProductType = getProductTypeModel(supermarket);

    const productType = await ProductType.findBySlug(req.params.slug)
      .populate('products', 'name price imageUrl');

    if (!productType) {
      return res.status(404).json({ error: 'ProductType not found' });
    }

    res.json(productType);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

// Create new ProductType
exports.createProductType = async (req, res) => {
  try {
    const { supermarket } = req.params;
    const ProductType = getProductTypeModel(supermarket);

    const productType = new ProductType(req.body);
    await productType.save();
    res.status(201).json(productType);
  } catch (error) {
    if (error.code === 11000) {
      res.status(400).json({ error: 'ProductType with this slug already exists' });
    } else {
      res.status(400).json({ error: error.message });
    }
  }
};

// Update ProductType
exports.updateProductType = async (req, res) => {
  try {
    const { supermarket } = req.params;
    const ProductType = getProductTypeModel(supermarket);

    const productType = await ProductType.findByIdAndUpdate(
      req.params.id,
      req.body,
      { new: true, runValidators: true }
    );

    if (!productType) {
      return res.status(404).json({ error: 'ProductType not found' });
    }

    res.json(productType);
  } catch (error) {
    if (error.code === 11000) {
      res.status(400).json({ error: 'ProductType with this slug already exists' });
    } else {
      res.status(400).json({ error: error.message });
    }
  }
};

// Delete ProductType (soft delete by setting active to false)
exports.deleteProductType = async (req, res) => {
  try {
    const { supermarket } = req.params;
    const ProductType = getProductTypeModel(supermarket);

    const productType = await ProductType.findByIdAndUpdate(
      req.params.id,
      { active: false },
      { new: true }
    );

    if (!productType) {
      return res.status(404).json({ error: 'ProductType not found' });
    }

    res.json({ message: 'ProductType deactivated successfully', productType });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

// Hard delete ProductType
exports.hardDeleteProductType = async (req, res) => {
  try {
    const { supermarket } = req.params;
    const ProductType = getProductTypeModel(supermarket);

    const productType = await ProductType.findByIdAndDelete(req.params.id);

    if (!productType) {
      return res.status(404).json({ error: 'ProductType not found' });
    }

    res.json({ message: 'ProductType deleted successfully' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

// Get ProductTypes by category and subcategory
exports.getProductTypesByCategory = async (req, res) => {
  try {
    const { supermarket } = req.params;
    const ProductType = getProductTypeModel(supermarket);

    const { categoryId, subcategoryId } = req.params;

    const productTypes = await ProductType.find({
      category: categoryId,
      subcategory: subcategoryId,
      active: true
    }).sort('-priority');

    res.json(productTypes);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

// Bulk create ProductTypes
exports.bulkCreateProductTypes = async (req, res) => {
  try {
    const { supermarket } = req.params;
    const ProductType = getProductTypeModel(supermarket);

    const productTypes = req.body.productTypes || req.body;

    if (!Array.isArray(productTypes)) {
      return res.status(400).json({ error: 'productTypes must be an array' });
    }

    const createdProductTypes = await ProductType.insertMany(productTypes);
    res.status(201).json(createdProductTypes);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
};

// Sync products for a ProductType
exports.syncProducts = async (req, res) => {
  try {
    const { supermarket } = req.params;
    const ProductType = getProductTypeModel(supermarket);

    const productType = await ProductType.findById(req.params.id);

    if (!productType) {
      return res.status(404).json({ error: 'ProductType not found' });
    }

    await productType.syncProducts();
    res.json({ message: 'Products synchronized successfully', productType });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};