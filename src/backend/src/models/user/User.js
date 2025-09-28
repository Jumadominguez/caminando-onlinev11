const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');

const userSchema = new mongoose.Schema({
  // Información básica del usuario
  email: {
    type: String,
    required: true,
    unique: true,
    lowercase: true,
    trim: true
  },
  username: {
    type: String,
    required: true,
    unique: true,
    trim: true,
    minlength: 3,
    maxlength: 30
  },
  firstName: {
    type: String,
    required: true,
    trim: true,
    maxlength: 50
  },
  lastName: {
    type: String,
    required: true,
    trim: true,
    maxlength: 50
  },

  // Autenticación y seguridad
  password: {
    type: String,
    required: true,
    minlength: 8
  },
  isEmailVerified: {
    type: Boolean,
    default: false
  },
  emailVerificationToken: String,
  emailVerificationExpires: Date,
  passwordResetToken: String,
  passwordResetExpires: Date,

  // Estado de la cuenta
  isActive: {
    type: Boolean,
    default: true
  },
  role: {
    type: String,
    enum: ['user', 'premium', 'admin'],
    default: 'user'
  },
  lastLogin: Date,
  loginCount: {
    type: Number,
    default: 0
  },

  // Información de perfil
  avatar: String,
  phone: {
    type: String,
    trim: true
  },
  dateOfBirth: Date,
  gender: {
    type: String,
    enum: ['male', 'female', 'other', 'prefer-not-to-say']
  },

  // Preferencias del usuario
  preferences: {
    currency: {
      type: String,
      default: 'ARS'
    },
    language: {
      type: String,
      default: 'es-AR'
    },
    notifications: {
      email: { type: Boolean, default: true },
      push: { type: Boolean, default: true },
      promotions: { type: Boolean, default: false }
    },
    supermarkets: [{
      supermarketId: { type: String, ref: 'Supermarket' },
      isFavorite: { type: Boolean, default: false },
      priority: { type: Number, default: 1 }
    }]
  },

  // Datos de compras y favoritos
  favorites: [{
    productId: { type: mongoose.Schema.Types.ObjectId, ref: 'Product' },
    addedAt: { type: Date, default: Date.now }
  }],

  shoppingLists: [{
    name: { type: String, required: true },
    description: String,
    isPublic: { type: Boolean, default: false },
    items: [{
      productId: { type: mongoose.Schema.Types.ObjectId, ref: 'Product' },
      quantity: { type: Number, default: 1 },
      notes: String,
      addedAt: { type: Date, default: Date.now }
    }],
    createdAt: { type: Date, default: Date.now },
    updatedAt: { type: Date, default: Date.now }
  }],

  // Historial de actividad
  searchHistory: [{
    query: { type: String, required: true },
    filters: Object,
    resultsCount: Number,
    timestamp: { type: Date, default: Date.now }
  }],

  // Estadísticas del usuario
  stats: {
    totalSearches: { type: Number, default: 0 },
    totalLists: { type: Number, default: 0 },
    totalFavorites: { type: Number, default: 0 },
    lastActivity: Date
  },

  // Información de ubicación (opcional)
  location: {
    country: String,
    state: String,
    city: String,
    postalCode: String,
    coordinates: {
      lat: Number,
      lng: Number
    }
  }

}, {
  timestamps: true, // createdAt, updatedAt
  toJSON: { virtuals: true },
  toObject: { virtuals: true }
});

// Índices para optimizar consultas
userSchema.index({ email: 1 }, { unique: true });
userSchema.index({ username: 1 }, { unique: true });
userSchema.index({ 'preferences.supermarkets.supermarketId': 1 });
userSchema.index({ 'favorites.productId': 1 });
userSchema.index({ role: 1, isActive: 1 });
userSchema.index({ createdAt: -1 });

// Virtual para nombre completo
userSchema.virtual('fullName').get(function() {
  return `${this.firstName} ${this.lastName}`;
});

// Método para verificar contraseña
userSchema.methods.comparePassword = async function(candidatePassword) {
  return await bcrypt.compare(candidatePassword, this.password);
};

// Método para generar hash de contraseña
userSchema.methods.hashPassword = async function() {
  this.password = await bcrypt.hash(this.password, 12);
};

// Pre-save middleware para hashear contraseña
userSchema.pre('save', async function(next) {
  // Solo hashear si la contraseña fue modificada
  if (!this.isModified('password')) return next();

  try {
    this.password = await bcrypt.hash(this.password, 12);
    next();
  } catch (error) {
    next(error);
  }
});

// Método para limpiar datos sensibles en JSON
userSchema.methods.toJSON = function() {
  const userObject = this.toObject();
  delete userObject.password;
  delete userObject.passwordResetToken;
  delete userObject.passwordResetExpires;
  delete userObject.emailVerificationToken;
  delete userObject.emailVerificationExpires;
  return userObject;
};

// Método para actualizar última actividad
userSchema.methods.updateLastActivity = function() {
  this.lastActivity = new Date();
  this.loginCount += 1;
  return this.save();
};

// Método para agregar producto a favoritos
userSchema.methods.addToFavorites = function(productId) {
  if (!this.favorites.some(fav => fav.productId.equals(productId))) {
    this.favorites.push({ productId });
    this.stats.totalFavorites = this.favorites.length;
  }
  return this.save();
};

// Método para remover producto de favoritos
userSchema.methods.removeFromFavorites = function(productId) {
  this.favorites = this.favorites.filter(fav => !fav.productId.equals(productId));
  this.stats.totalFavorites = this.favorites.length;
  return this.save();
};

// Método para verificar si un producto está en favoritos
userSchema.methods.isFavorite = function(productId) {
  return this.favorites.some(fav => fav.productId.equals(productId));
};

// Método estático para encontrar usuario por email o username
userSchema.statics.findByEmailOrUsername = function(identifier) {
  return this.findOne({
    $or: [
      { email: identifier.toLowerCase() },
      { username: identifier }
    ]
  });
};

// Usar la conexión específica de admin
const { admin } = global.databaseConnections || {};

// Si no hay conexión global, crear una temporal (para desarrollo/testing)
let User;
if (admin) {
  User = admin.model('User', userSchema);
} else {
  // Fallback para desarrollo - usar conexión por defecto
  console.warn('⚠️  Admin connection not available, using default connection for User model');
  User = mongoose.model('User', userSchema);
}

module.exports = User;