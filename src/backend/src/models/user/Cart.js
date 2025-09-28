const mongoose = require('mongoose');

const cartSchema = new mongoose.Schema({
  // Usuario (opcional para carritos de invitados)
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User'
  },

  // Session ID para carritos de invitados
  sessionId: {
    type: String,
    required: true,
    unique: true
  },

  // Items del carrito
  items: [{
    productId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'Product',
      required: true
    },
    productName: { type: String, required: true },
    supermarketId: { type: String, required: true },
    quantity: {
      type: Number,
      required: true,
      min: 1,
      default: 1
    },
    unitPrice: { type: Number, required: true },
    totalPrice: { type: Number, required: true },
    productData: {
      sku: String,
      brand: String,
      image: String,
      weight: Number,
      pricePerKilo: Number
    },
    addedAt: { type: Date, default: Date.now },
    updatedAt: { type: Date, default: Date.now }
  }],

  // Totales
  subtotal: { type: Number, default: 0 },
  tax: { type: Number, default: 0 },
  shipping: { type: Number, default: 0 },
  discount: { type: Number, default: 0 },
  total: { type: Number, default: 0 },

  // Información de envío estimada
  estimatedShipping: {
    cost: { type: Number, default: 0 },
    days: { type: Number, default: 1 },
    method: {
      type: String,
      enum: ['standard', 'express', 'same_day'],
      default: 'standard'
    }
  },

  // Cupones y promociones aplicadas
  appliedCoupons: [{
    code: { type: String, required: true },
    discountType: {
      type: String,
      enum: ['percentage', 'fixed'],
      required: true
    },
    discountValue: { type: Number, required: true },
    appliedAt: { type: Date, default: Date.now }
  }],

  // Estado del carrito
  isActive: { type: Boolean, default: true },
  expiresAt: {
    type: Date,
    default: () => new Date(Date.now() + 7 * 24 * 60 * 60 * 1000) // 7 días
  },

  // Metadata
  source: {
    type: String,
    enum: ['web', 'mobile', 'api'],
    default: 'web'
  },
  ipAddress: String,
  userAgent: String,

  // Supermercado principal (para carritos que mezclan productos)
  primarySupermarket: String

}, {
  timestamps: true
});

// Índices
cartSchema.index({ userId: 1, isActive: 1 });
cartSchema.index({ expiresAt: 1 }, { expireAfterSeconds: 0 }); // TTL index
cartSchema.index({ 'items.productId': 1 });
cartSchema.index({ isActive: 1, updatedAt: -1 });

// Virtual para contar items
cartSchema.virtual('itemCount').get(function() {
  return this.items.reduce((total, item) => total + item.quantity, 0);
});

// Virtual para contar productos únicos
cartSchema.virtual('uniqueItemCount').get(function() {
  return this.items.length;
});

// Método para agregar item
cartSchema.methods.addItem = function(productData) {
  const existingItem = this.items.find(item =>
    item.productId.toString() === productData.productId.toString()
  );

  if (existingItem) {
    existingItem.quantity += productData.quantity || 1;
    existingItem.totalPrice = existingItem.quantity * existingItem.unitPrice;
    existingItem.updatedAt = new Date();
  } else {
    this.items.push({
      productId: productData.productId,
      productName: productData.productName,
      supermarketId: productData.supermarketId,
      quantity: productData.quantity || 1,
      unitPrice: productData.unitPrice,
      totalPrice: (productData.quantity || 1) * productData.unitPrice,
      productData: productData.productData || {},
      addedAt: new Date(),
      updatedAt: new Date()
    });
  }

  this.calculateTotals();
  return this.save();
};

// Método para actualizar cantidad
cartSchema.methods.updateItemQuantity = function(productId, quantity) {
  const item = this.items.find(item =>
    item.productId.toString() === productId.toString()
  );

  if (item) {
    if (quantity <= 0) {
      this.items = this.items.filter(item =>
        item.productId.toString() !== productId.toString()
      );
    } else {
      item.quantity = quantity;
      item.totalPrice = item.quantity * item.unitPrice;
      item.updatedAt = new Date();
    }
    this.calculateTotals();
  }

  return this.save();
};

// Método para remover item
cartSchema.methods.removeItem = function(productId) {
  this.items = this.items.filter(item =>
    item.productId.toString() !== productId.toString()
  );
  this.calculateTotals();
  return this.save();
};

// Método para calcular totales
cartSchema.methods.calculateTotals = function() {
  this.subtotal = this.items.reduce((total, item) => total + item.totalPrice, 0);
  this.total = this.subtotal + this.tax + this.shipping - this.discount;
  return this.total;
};

// Método para vaciar carrito
cartSchema.methods.clear = function() {
  this.items = [];
  this.subtotal = 0;
  this.total = 0;
  this.appliedCoupons = [];
  return this.save();
};

// Método para aplicar cupón
cartSchema.methods.applyCoupon = function(couponData) {
  // Verificar si el cupón ya está aplicado
  const existingCoupon = this.appliedCoupons.find(coupon => coupon.code === couponData.code);
  if (existingCoupon) {
    throw new Error('Coupon already applied');
  }

  this.appliedCoupons.push({
    code: couponData.code,
    discountType: couponData.discountType,
    discountValue: couponData.discountValue,
    appliedAt: new Date()
  });

  this.calculateTotals();
  return this.save();
};

// Método para remover cupón
cartSchema.methods.removeCoupon = function(couponCode) {
  this.appliedCoupons = this.appliedCoupons.filter(coupon => coupon.code !== couponCode);
  this.calculateTotals();
  return this.save();
};

// Método estático para encontrar o crear carrito por sessionId
cartSchema.statics.findOrCreateBySessionId = async function(sessionId, userId = null) {
  let cart = await this.findOne({ sessionId, isActive: true });

  if (!cart) {
    cart = new this({
      sessionId,
      userId,
      items: [],
      isActive: true
    });
    await cart.save();
  }

  return cart;
};

// Usar la conexión específica de admin
const { admin } = global.databaseConnections || {};

// Si no hay conexión global, crear una temporal (para desarrollo/testing)
let Cart;
if (admin) {
  Cart = admin.model('Cart', cartSchema);
} else {
  // Fallback para desarrollo - usar conexión por defecto
  console.warn('⚠️  Admin connection not available, using default connection for Cart model');
  Cart = mongoose.model('Cart', cartSchema);
}

module.exports = Cart;