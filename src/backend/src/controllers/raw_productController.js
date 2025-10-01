// Controllers para modelos de productos (processed database)
const Product = require('../models/product/Product');
const Category = require('../models/product/Category');
const Subcategory = require('../models/product/Subcategory');
const ProductType = require('../models/product/ProductType');
const Offer = require('../models/product/Offer');
const Filter = require('../models/product/Filter');
const PriceHistory = require('../models/product/PriceHistory');

// ==================== PRODUCT CONTROLLERS ====================

// Get all products with filters
exports.getProducts = async (req, res) => {
  try {
    const {
      page = 1,
      limit = 20,
      category,
      subcategory,
      supermarket,
      minPrice,
      maxPrice,
      search,
      sort = 'name'
    } = req.query;

    let query = { isAvailable: true };

    // Apply filters
    if (category) query.category = category;
    if (subcategory) query.subcategory = subcategory;
    if (supermarket) query.supermarket = supermarket;
    if (minPrice || maxPrice) {
      query.price = {};
      if (minPrice) query.price.$gte = parseFloat(minPrice);
      if (maxPrice) query.price.$lte = parseFloat(maxPrice);
    }
    if (search) {
      query.$or = [
        { name: { $regex: search, $options: 'i' } },
        { brand: { $regex: search, $options: 'i' } }
      ];
    }

    const options = {
      page: parseInt(page),
      limit: parseInt(limit),
      sort: sort
    };

    const products = await Product.find(query)
      .populate('offers')
      .sort(options.sort)
      .limit(options.limit)
      .skip((options.page - 1) * options.limit);

    const total = await Product.countDocuments(query);

    res.json({
      products,
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

// Get product by ID
exports.getProductById = async (req, res) => {
  try {
    const product = await Product.findById(req.params.id)
      .populate('offers');

    if (!product) {
      return res.status(404).json({ message: 'Product not found' });
    }

    res.json(product);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

// Create new product
exports.createProduct = async (req, res) => {
  try {
    const product = new Product(req.body);
    await product.save();
    res.status(201).json(product);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
};

// Update product
exports.updateProduct = async (req, res) => {
  try {
    const product = await Product.findByIdAndUpdate(
      req.params.id,
      req.body,
      { new: true, runValidators: true }
    );

    if (!product) {
      return res.status(404).json({ message: 'Product not found' });
    }

    res.json(product);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
};

// Delete product
exports.deleteProduct = async (req, res) => {
  try {
    const product = await Product.findByIdAndDelete(req.params.id);

    if (!product) {
      return res.status(404).json({ message: 'Product not found' });
    }

    res.json({ message: 'Product deleted successfully' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

// ==================== CATEGORY CONTROLLERS ====================

// Get all categories
exports.getCategories = async (req, res) => {
  try {
    const categories = await Category.find({ active: true })
      .sort({ priority: -1, name: 1 });

    res.json(categories);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

// Get category by ID
exports.getCategoryById = async (req, res) => {
  try {
    const category = await Category.findById(req.params.id)
      .populate('subcategories');

    if (!category) {
      return res.status(404).json({ message: 'Category not found' });
    }

    res.json(category);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

// Create new category
exports.createCategory = async (req, res) => {
  try {
    const category = new Category(req.body);
    await category.save();
    res.status(201).json(category);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
};

// ==================== SUBCATEGORY CONTROLLERS ====================

// Get all subcategories
exports.getSubcategories = async (req, res) => {
  try {
    const { category } = req.query;
    let query = { active: true };

    if (category) query.category = category;

    const subcategories = await Subcategory.find(query)
      .populate('category')
      .sort({ priority: -1, name: 1 });

    res.json(subcategories);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

// Get subcategory by ID
exports.getSubcategoryById = async (req, res) => {
  try {
    const subcategory = await Subcategory.findById(req.params.id)
      .populate('category');

    if (!subcategory) {
      return res.status(404).json({ message: 'Subcategory not found' });
    }

    res.json(subcategory);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

// ==================== PRODUCT TYPE CONTROLLERS ====================

// Get all product types
exports.getProductTypes = async (req, res) => {
  try {
    const { category, subcategory } = req.query;
    let query = { active: true };

    if (category) query.category = category;
    if (subcategory) query.subcategory = subcategory;

    const productTypes = await ProductType.find(query)
      .populate('category')
      .populate('subcategory')
      .sort({ priority: -1, name: 1 });

    res.json(productTypes);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

// Get product type by ID
exports.getProductTypeById = async (req, res) => {
  try {
    const productType = await ProductType.findById(req.params.id)
      .populate('category')
      .populate('subcategory')
      .populate('products');

    if (!productType) {
      return res.status(404).json({ message: 'Product type not found' });
    }

    res.json(productType);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

// ==================== OFFER CONTROLLERS ====================

// Get all active offers
exports.getOffers = async (req, res) => {
  try {
    const currentDate = new Date();
    const offers = await Offer.find({
      isActive: true,
      startDate: { $lte: currentDate },
      endDate: { $gte: currentDate }
    }).sort({ priority: -1 });

    res.json(offers);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

// Get offer by ID
exports.getOfferById = async (req, res) => {
  try {
    const offer = await Offer.findById(req.params.id);

    if (!offer) {
      return res.status(404).json({ message: 'Offer not found' });
    }

    res.json(offer);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

// ==================== FILTER CONTROLLERS ====================

// Get all filters
exports.getFilters = async (req, res) => {
  try {
    const { category } = req.query;
    let query = { active: true };

    if (category) query.applicableCategories = category;

    const filters = await Filter.find(query)
      .sort({ priority: -1, name: 1 });

    res.json(filters);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

// ==================== PRICE HISTORY CONTROLLERS ====================

// Get price history for a product
exports.getPriceHistory = async (req, res) => {
  try {
    const { productId } = req.params;
    const { limit = 50 } = req.query;

    const priceHistory = await PriceHistory.find({ productId })
      .sort({ scrapedAt: -1 })
      .limit(parseInt(limit));

    res.json(priceHistory);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

// Get price statistics for a product
exports.getPriceStats = async (req, res) => {
  try {
    const { productId } = req.params;

    const stats = await PriceHistory.getPriceStats(productId);

    res.json(stats);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};