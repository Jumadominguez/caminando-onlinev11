const mongoose = require('mongoose');

const notificationSchema = new mongoose.Schema({
  // Destinatario
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },

  // Tipo de notificación
  type: {
    type: String,
    enum: [
      'price_drop',      // Bajada de precio en producto favorito
      'back_in_stock',   // Producto vuelve a estar disponible
      'offer_available', // Nueva oferta disponible
      'order_status',    // Cambio en estado de pedido
      'promotion',       // Promociones generales
      'system',          // Notificaciones del sistema
      'security',        // Alertas de seguridad
      'marketing'        // Marketing y newsletters
    ],
    required: true
  },

  // Título y contenido
  title: {
    type: String,
    required: true,
    trim: true,
    maxlength: 200
  },
  message: {
    type: String,
    required: true,
    trim: true,
    maxlength: 1000
  },

  // Datos adicionales específicos del tipo
  data: {
    // Para price_drop y back_in_stock
    productId: mongoose.Schema.Types.ObjectId,
    productName: String,
    oldPrice: Number,
    newPrice: Number,
    supermarketId: String,

    // Para order_status
    orderId: mongoose.Schema.Types.ObjectId,
    orderNumber: String,
    oldStatus: String,
    newStatus: String,

    // Para offers
    offerId: mongoose.Schema.Types.ObjectId,
    offerType: String,

    // URLs y acciones
    actionUrl: String,
    actionText: String
  },

  // Estado de la notificación
  isRead: {
    type: Boolean,
    default: false
  },
  readAt: Date,

  // Canales de envío
  channels: [{
    type: {
      type: String,
      enum: ['in_app', 'email', 'push', 'sms'],
      required: true
    },
    sent: {
      type: Boolean,
      default: false
    },
    sentAt: Date,
    error: String
  }],

  // Prioridad
  priority: {
    type: String,
    enum: ['low', 'normal', 'high', 'urgent'],
    default: 'normal'
  },

  // Programación
  scheduledFor: Date, // Para notificaciones programadas
  expiresAt: Date,    // Fecha de expiración

  // Metadata
  source: String,     // Origen de la notificación (sistema, admin, etc.)
  category: String,   // Categoría adicional para agrupación

  // Estadísticas
  clickCount: {
    type: Number,
    default: 0
  },
  lastClickedAt: Date

}, {
  timestamps: true
});

// Índices
notificationSchema.index({ userId: 1, isRead: 1, createdAt: -1 });
notificationSchema.index({ userId: 1, type: 1, createdAt: -1 });
notificationSchema.index({ type: 1, priority: 1, createdAt: -1 });
notificationSchema.index({ scheduledFor: 1 }, { sparse: true });
notificationSchema.index({ expiresAt: 1 }, { expireAfterSeconds: 0 }); // TTL index

// Virtual para verificar si está expirada
notificationSchema.virtual('isExpired').get(function() {
  return this.expiresAt && new Date() > this.expiresAt;
});

// Método para marcar como leída
notificationSchema.methods.markAsRead = function() {
  this.isRead = true;
  this.readAt = new Date();
  return this.save();
};

// Método para registrar click
notificationSchema.methods.registerClick = function() {
  this.clickCount += 1;
  this.lastClickedAt = new Date();
  return this.save();
};

// Método para enviar por canal específico
notificationSchema.methods.sendViaChannel = async function(channelType) {
  const channel = this.channels.find(ch => ch.type === channelType);
  if (!channel) {
    throw new Error(`Channel ${channelType} not configured for this notification`);
  }

  try {
    // Aquí iría la lógica real de envío (email, push, etc.)
    // Por ahora solo marcamos como enviado
    channel.sent = true;
    channel.sentAt = new Date();

    await this.save();
    return { success: true };
  } catch (error) {
    channel.error = error.message;
    await this.save();
    throw error;
  }
};

// Método estático para crear notificación de cambio de precio
notificationSchema.statics.createPriceDropNotification = function(userId, productData) {
  return new this({
    userId,
    type: 'price_drop',
    title: `¡Precio reducido en ${productData.productName}!`,
    message: `El precio bajó de $${productData.oldPrice} a $${productData.newPrice} en ${productData.supermarketName}`,
    data: {
      productId: productData.productId,
      productName: productData.productName,
      oldPrice: productData.oldPrice,
      newPrice: productData.newPrice,
      supermarketId: productData.supermarketId
    },
    priority: 'high',
    channels: [
      { type: 'in_app' },
      { type: 'push' }
    ]
  });
};

// Método estático para crear notificación de estado de pedido
notificationSchema.statics.createOrderStatusNotification = function(userId, orderData) {
  const statusMessages = {
    confirmed: 'Tu pedido ha sido confirmado',
    processing: 'Tu pedido está siendo procesado',
    shipped: 'Tu pedido ha sido enviado',
    delivered: 'Tu pedido ha sido entregado'
  };

  return new this({
    userId,
    type: 'order_status',
    title: 'Actualización de tu pedido',
    message: `${statusMessages[orderData.newStatus]} - Pedido #${orderData.orderNumber}`,
    data: {
      orderId: orderData.orderId,
      orderNumber: orderData.orderNumber,
      oldStatus: orderData.oldStatus,
      newStatus: orderData.newStatus
    },
    priority: orderData.newStatus === 'delivered' ? 'high' : 'normal',
    channels: [
      { type: 'in_app' },
      { type: 'email' }
    ]
  });
};

// Método estático para obtener notificaciones no leídas
notificationSchema.statics.getUnreadCount = function(userId) {
  return this.countDocuments({ userId, isRead: false });
};

// Método estático para limpiar notificaciones expiradas
notificationSchema.statics.cleanupExpired = function() {
  return this.deleteMany({
    expiresAt: { $lt: new Date() }
  });
};

// Usar la conexión específica de operations
const { operations } = global.databaseConnections || {};

// Si no hay conexión global, crear una temporal (para desarrollo/testing)
let Notification;
if (operations) {
  Notification = operations.model('Notification', notificationSchema);
} else {
  // Fallback para desarrollo - usar conexión por defecto
  console.warn('⚠️  Operations connection not available, using default connection for Notification model');
  Notification = mongoose.model('Notification', notificationSchema);
}

module.exports = Notification;