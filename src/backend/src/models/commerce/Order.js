const mongoose = require('mongoose');

const orderSchema = new mongoose.Schema({
  // Referencias principales
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },

  // Información del pedido
  orderNumber: {
    type: String,
    required: true,
    unique: true
  },
  status: {
    type: String,
    enum: ['pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled'],
    default: 'pending'
  },

  // Items del pedido
  items: [{
    productId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'Product',
      required: true
    },
    productName: { type: String, required: true },
    supermarketId: { type: String, required: true },
    quantity: { type: Number, required: true, min: 1 },
    unitPrice: { type: Number, required: true },
    totalPrice: { type: Number, required: true },
    productData: {
      sku: String,
      brand: String,
      image: String
    }
  }],

  // Totales y precios
  subtotal: { type: Number, required: true },
  tax: { type: Number, default: 0 },
  shipping: { type: Number, default: 0 },
  discount: { type: Number, default: 0 },
  total: { type: Number, required: true },

  // Información de envío
  shippingAddress: {
    street: { type: String, required: true },
    number: { type: String, required: true },
    apartment: String,
    city: { type: String, required: true },
    state: { type: String, required: true },
    postalCode: { type: String, required: true },
    country: { type: String, default: 'Argentina' },
    coordinates: {
      lat: Number,
      lng: Number
    }
  },

  // Información de pago
  paymentMethod: {
    type: String,
    enum: ['credit_card', 'debit_card', 'bank_transfer', 'cash_on_delivery'],
    required: true
  },
  paymentStatus: {
    type: String,
    enum: ['pending', 'processing', 'completed', 'failed', 'refunded'],
    default: 'pending'
  },
  paymentId: String, // ID de transacción externa

  // Información de entrega
  deliveryMethod: {
    type: String,
    enum: ['home_delivery', 'pickup_point', 'supermarket_pickup'],
    default: 'home_delivery'
  },
  deliveryDate: Date,
  deliveryTimeSlot: String, // ej: "9:00-12:00"

  // Tracking y notas
  trackingNumber: String,
  notes: String,
  internalNotes: String, // Solo para admin

  // Timestamps
  orderDate: { type: Date, default: Date.now },
  confirmedAt: Date,
  shippedAt: Date,
  deliveredAt: Date,
  cancelledAt: Date,

  // Metadata
  source: {
    type: String,
    enum: ['web', 'mobile', 'api'],
    default: 'web'
  },
  ipAddress: String,
  userAgent: String

}, {
  timestamps: true
});

// Índices para optimizar consultas
orderSchema.index({ userId: 1, createdAt: -1 });
orderSchema.index({ orderNumber: 1 }, { unique: true });
orderSchema.index({ status: 1 });
orderSchema.index({ paymentStatus: 1 });
orderSchema.index({ 'items.supermarketId': 1 });
orderSchema.index({ createdAt: -1 });

// Virtual para calcular total de items
orderSchema.virtual('itemCount').get(function() {
  return this.items.reduce((total, item) => total + item.quantity, 0);
});

// Método para calcular total
orderSchema.methods.calculateTotal = function() {
  this.subtotal = this.items.reduce((total, item) => total + item.totalPrice, 0);
  this.total = this.subtotal + this.tax + this.shipping - this.discount;
  return this.total;
};

// Método para actualizar estado
orderSchema.methods.updateStatus = function(newStatus, notes = '') {
  this.status = newStatus;

  // Actualizar timestamps según estado
  const now = new Date();
  switch (newStatus) {
    case 'confirmed':
      this.confirmedAt = now;
      break;
    case 'shipped':
      this.shippedAt = now;
      break;
    case 'delivered':
      this.deliveredAt = now;
      break;
    case 'cancelled':
      this.cancelledAt = now;
      break;
  }

  if (notes) {
    this.notes = notes;
  }

  return this.save();
};

// Usar la conexión específica de operations
const { operations } = global.databaseConnections || {};

// Si no hay conexión global, crear una temporal (para desarrollo/testing)
let Order;
if (operations) {
  Order = operations.model('Order', orderSchema);
} else {
  // Fallback para desarrollo - usar conexión por defecto
  console.warn('⚠️  Operations connection not available, using default connection for Order model');
  Order = mongoose.model('Order', orderSchema);
}

module.exports = Order;