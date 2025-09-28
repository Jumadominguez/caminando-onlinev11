const mongoose = require('mongoose');

const userAddressSchema = new mongoose.Schema({
  // Referencia al usuario
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },

  // Tipo de dirección
  type: {
    type: String,
    enum: ['home', 'work', 'other'],
    default: 'home'
  },

  // Nombre personalizado de la dirección
  name: {
    type: String,
    required: true,
    trim: true
  },

  // Información de contacto
  contactName: {
    type: String,
    required: true,
    trim: true
  },
  contactPhone: {
    type: String,
    required: true,
    trim: true
  },

  // Dirección completa
  street: {
    type: String,
    required: true,
    trim: true
  },
  number: {
    type: String,
    required: true,
    trim: true
  },
  apartment: {
    type: String,
    trim: true
  },
  floor: {
    type: String,
    trim: true
  },
  neighborhood: {
    type: String,
    trim: true
  },
  city: {
    type: String,
    required: true,
    trim: true
  },
  state: {
    type: String,
    required: true,
    trim: true
  },
  postalCode: {
    type: String,
    required: true,
    trim: true
  },
  country: {
    type: String,
    default: 'Argentina',
    trim: true
  },

  // Coordenadas geográficas
  coordinates: {
    lat: {
      type: Number,
      min: -90,
      max: 90
    },
    lng: {
      type: Number,
      min: -180,
      max: 180
    }
  },

  // Información adicional
  instructions: {
    type: String,
    trim: true,
    maxlength: 500
  }, // Instrucciones especiales para delivery

  // Estado de la dirección
  isDefault: {
    type: Boolean,
    default: false
  },
  isActive: {
    type: Boolean,
    default: true
  },

  // Metadata de uso
  usageCount: {
    type: Number,
    default: 0
  },
  lastUsed: Date,

  // Información de validación
  isValidated: {
    type: Boolean,
    default: false
  },
  validatedAt: Date,
  validationSource: String, // API de validación utilizada

  // Información adicional para envíos
  deliveryZone: String,
  estimatedDeliveryTime: Number, // en minutos
  deliveryFee: Number

}, {
  timestamps: true
});

// Índices
userAddressSchema.index({ userId: 1, isActive: 1 });
userAddressSchema.index({ userId: 1, isDefault: 1 });
userAddressSchema.index({ userId: 1, type: 1 });
userAddressSchema.index({ coordinates: '2dsphere' }); // Para consultas geoespaciales

// Virtual para dirección formateada
userAddressSchema.virtual('formattedAddress').get(function() {
  let address = `${this.street} ${this.number}`;

  if (this.apartment) {
    address += `, ${this.apartment}`;
    if (this.floor) {
      address += ` ${this.floor}`;
    }
  }

  address += `, ${this.neighborhood || this.city}, ${this.state} ${this.postalCode}, ${this.country}`;

  return address;
});

// Método para marcar como usada
userAddressSchema.methods.markAsUsed = function() {
  this.usageCount += 1;
  this.lastUsed = new Date();
  return this.save();
};

// Método para validar dirección
userAddressSchema.methods.validateAddress = function(validationData = {}) {
  this.isValidated = true;
  this.validatedAt = new Date();
  this.validationSource = validationData.source || 'manual';

  if (validationData.coordinates) {
    this.coordinates = validationData.coordinates;
  }

  if (validationData.deliveryZone) {
    this.deliveryZone = validationData.deliveryZone;
  }

  return this.save();
};

// Método estático para obtener dirección por defecto
userAddressSchema.statics.getDefaultAddress = function(userId) {
  return this.findOne({
    userId,
    isDefault: true,
    isActive: true
  });
};

// Método estático para obtener direcciones activas de un usuario
userAddressSchema.statics.getActiveAddresses = function(userId) {
  return this.find({
    userId,
    isActive: true
  }).sort({ isDefault: -1, updatedAt: -1 });
};

// Método para establecer como dirección por defecto
userAddressSchema.methods.setAsDefault = async function() {
  // Primero quitar el flag de default de otras direcciones del usuario
  await this.constructor.updateMany(
    { userId: this.userId, _id: { $ne: this._id } },
    { isDefault: false }
  );

  // Establecer esta como default
  this.isDefault = true;
  return this.save();
};

// Pre-save middleware para asegurar solo una dirección por defecto por usuario
userAddressSchema.pre('save', async function(next) {
  if (this.isDefault && this.isModified('isDefault')) {
    // Si se está marcando como default, quitar el flag de otras direcciones
    await this.constructor.updateMany(
      { userId: this.userId, _id: { $ne: this._id } },
      { isDefault: false }
    );
  }
  next();
});

// Usar la conexión específica de admin
const { admin } = global.databaseConnections || {};

// Si no hay conexión global, crear una temporal (para desarrollo/testing)
let UserAddress;
if (admin) {
  UserAddress = admin.model('UserAddress', userAddressSchema);
} else {
  // Fallback para desarrollo - usar conexión por defecto
  console.warn('⚠️  Admin connection not available, using default connection for UserAddress model');
  UserAddress = mongoose.model('UserAddress', userAddressSchema);
}

module.exports = UserAddress;