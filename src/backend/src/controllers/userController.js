// Controllers para modelos de usuario (admin database)
const User = require('../models/user/User');
const UserAddress = require('../models/user/UserAddress');
const UserSession = require('../models/user/UserSession');
const Cart = require('../models/user/Cart');

// ==================== USER CONTROLLERS ====================

// Get all users
exports.getUsers = async (req, res) => {
  try {
    const users = await User.find()
      .select('-password') // Exclude password from response
      .sort({ createdAt: -1 });

    res.json(users);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

// Get user by ID
exports.getUserById = async (req, res) => {
  try {
    const user = await User.findById(req.params.id)
      .select('-password')
      .populate('addresses');

    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }

    res.json(user);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

// Create new user
exports.createUser = async (req, res) => {
  try {
    const user = new User(req.body);
    await user.save();

    // Remove password from response
    const userResponse = user.toObject();
    delete userResponse.password;

    res.status(201).json(userResponse);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
};

// Update user
exports.updateUser = async (req, res) => {
  try {
    // Don't allow password updates through this endpoint
    delete req.body.password;

    const user = await User.findByIdAndUpdate(
      req.params.id,
      req.body,
      { new: true, runValidators: true }
    ).select('-password');

    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }

    res.json(user);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
};

// Delete user
exports.deleteUser = async (req, res) => {
  try {
    const user = await User.findByIdAndDelete(req.params.id);

    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }

    res.json({ message: 'User deleted successfully' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

// ==================== USER ADDRESS CONTROLLERS ====================

// Get addresses for a user
exports.getUserAddresses = async (req, res) => {
  try {
    const addresses = await UserAddress.find({ userId: req.params.userId })
      .sort({ createdAt: -1 });

    res.json(addresses);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

// Create new address for user
exports.createUserAddress = async (req, res) => {
  try {
    const address = new UserAddress({
      ...req.body,
      userId: req.params.userId
    });

    await address.save();
    res.status(201).json(address);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
};

// Update user address
exports.updateUserAddress = async (req, res) => {
  try {
    const address = await UserAddress.findOneAndUpdate(
      { _id: req.params.addressId, userId: req.params.userId },
      req.body,
      { new: true, runValidators: true }
    );

    if (!address) {
      return res.status(404).json({ message: 'Address not found' });
    }

    res.json(address);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
};

// Delete user address
exports.deleteUserAddress = async (req, res) => {
  try {
    const address = await UserAddress.findOneAndDelete({
      _id: req.params.addressId,
      userId: req.params.userId
    });

    if (!address) {
      return res.status(404).json({ message: 'Address not found' });
    }

    res.json({ message: 'Address deleted successfully' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

// ==================== USER SESSION CONTROLLERS ====================

// Get active sessions for a user
exports.getUserSessions = async (req, res) => {
  try {
    const sessions = await UserSession.find({
      userId: req.params.userId,
      isActive: true
    }).sort({ lastActivity: -1 });

    res.json(sessions);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

// Terminate user session
exports.terminateSession = async (req, res) => {
  try {
    const session = await UserSession.findOneAndUpdate(
      { _id: req.params.sessionId, userId: req.params.userId },
      {
        isActive: false,
        terminatedAt: new Date(),
        terminationReason: req.body.reason || 'manual_termination'
      },
      { new: true }
    );

    if (!session) {
      return res.status(404).json({ message: 'Session not found' });
    }

    res.json({ message: 'Session terminated successfully' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

// ==================== CART CONTROLLERS ====================

// Get user's cart
exports.getUserCart = async (req, res) => {
  try {
    let cart = await Cart.findOne({ userId: req.params.userId })
      .populate('items.productId');

    if (!cart) {
      // Create empty cart if none exists
      cart = new Cart({ userId: req.params.userId, items: [] });
      await cart.save();
    }

    res.json(cart);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

// Add item to cart
exports.addToCart = async (req, res) => {
  try {
    const { productId, quantity, supermarketId } = req.body;

    let cart = await Cart.findOne({ userId: req.params.userId });

    if (!cart) {
      cart = new Cart({ userId: req.params.userId, items: [] });
    }

    // Check if item already exists in cart
    const existingItem = cart.items.find(item =>
      item.productId.toString() === productId &&
      item.supermarketId === supermarketId
    );

    if (existingItem) {
      existingItem.quantity += quantity;
    } else {
      cart.items.push({
        productId,
        quantity,
        supermarketId,
        addedAt: new Date()
      });
    }

    await cart.save();
    await cart.populate('items.productId');

    res.json(cart);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
};

// Update cart item
exports.updateCartItem = async (req, res) => {
  try {
    const { quantity } = req.body;

    const cart = await Cart.findOneAndUpdate(
      {
        userId: req.params.userId,
        'items._id': req.params.itemId
      },
      {
        $set: {
          'items.$.quantity': quantity,
          'items.$.updatedAt': new Date()
        }
      },
      { new: true }
    ).populate('items.productId');

    if (!cart) {
      return res.status(404).json({ message: 'Cart or item not found' });
    }

    res.json(cart);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
};

// Remove item from cart
exports.removeFromCart = async (req, res) => {
  try {
    const cart = await Cart.findOneAndUpdate(
      { userId: req.params.userId },
      {
        $pull: { items: { _id: req.params.itemId } }
      },
      { new: true }
    ).populate('items.productId');

    if (!cart) {
      return res.status(404).json({ message: 'Cart not found' });
    }

    res.json(cart);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

// Clear cart
exports.clearCart = async (req, res) => {
  try {
    const cart = await Cart.findOneAndUpdate(
      { userId: req.params.userId },
      { items: [] },
      { new: true }
    );

    if (!cart) {
      return res.status(404).json({ message: 'Cart not found' });
    }

    res.json({ message: 'Cart cleared successfully' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};