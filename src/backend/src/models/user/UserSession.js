const mongoose = require('mongoose');

const userSessionSchema = new mongoose.Schema({
  // Referencia al usuario
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },

  // Token de sesión
  sessionToken: {
    type: String,
    required: true,
    unique: true
  },

  // Token de refresh (para JWT)
  refreshToken: {
    type: String,
    unique: true,
    sparse: true // Permite valores null únicos
  },

  // Información del dispositivo
  deviceInfo: {
    userAgent: String,
    ipAddress: String,
    deviceType: {
      type: String,
      enum: ['desktop', 'mobile', 'tablet', 'unknown']
    },
    browser: String,
    os: String,
    platform: String
  },

  // Ubicación geográfica (opcional)
  location: {
    country: String,
    region: String,
    city: String,
    coordinates: {
      lat: Number,
      lng: Number
    }
  },

  // Estado de la sesión
  isActive: {
    type: Boolean,
    default: true
  },
  isRememberMe: {
    type: Boolean,
    default: false
  },

  // Timestamps
  createdAt: {
    type: Date,
    default: Date.now
  },
  lastActivity: {
    type: Date,
    default: Date.now
  },
  expiresAt: Date,

  // Metadata de seguridad
  loginMethod: {
    type: String,
    enum: ['password', 'google', 'facebook', 'apple', 'magic_link'],
    default: 'password'
  },
  riskScore: {
    type: Number,
    min: 0,
    max: 100,
    default: 0
  },

  // Intentos de sesión y bloqueos
  failedAttempts: {
    type: Number,
    default: 0
  },
  lockedUntil: Date,
  lockReason: String

}, {
  timestamps: false // Usamos createdAt manualmente
});

// Índices
userSessionSchema.index({ userId: 1, isActive: 1 });
userSessionSchema.index({ expiresAt: 1 }, { expireAfterSeconds: 0 }); // TTL index
userSessionSchema.index({ lastActivity: -1 });
userSessionSchema.index({ 'deviceInfo.ipAddress': 1 });

// Virtual para verificar si está expirada
userSessionSchema.virtual('isExpired').get(function() {
  return this.expiresAt && new Date() > this.expiresAt;
});

// Virtual para verificar si está bloqueada
userSessionSchema.virtual('isLocked').get(function() {
  return this.lockedUntil && new Date() < this.lockedUntil;
});

// Método para actualizar actividad
userSessionSchema.methods.updateActivity = function(ipAddress = null) {
  this.lastActivity = new Date();
  if (ipAddress) {
    this.deviceInfo.ipAddress = ipAddress;
  }
  return this.save();
};

// Método para extender sesión
userSessionSchema.methods.extend = function(hours = 24) {
  this.expiresAt = new Date(Date.now() + (hours * 60 * 60 * 1000));
  return this.save();
};

// Método para invalidar sesión
userSessionSchema.methods.invalidate = function(reason = 'user_logout') {
  this.isActive = false;
  // Aquí podríamos agregar logging de la razón
  return this.save();
};

// Método para registrar intento fallido
userSessionSchema.methods.recordFailedAttempt = function() {
  this.failedAttempts += 1;

  // Bloquear después de 5 intentos fallidos
  if (this.failedAttempts >= 5) {
    this.lockedUntil = new Date(Date.now() + (15 * 60 * 1000)); // 15 minutos
    this.lockReason = 'too_many_failed_attempts';
  }

  return this.save();
};

// Método para resetear intentos fallidos
userSessionSchema.methods.resetFailedAttempts = function() {
  this.failedAttempts = 0;
  this.lockedUntil = undefined;
  this.lockReason = undefined;
  return this.save();
};

// Método estático para crear nueva sesión
userSessionSchema.statics.createSession = async function(userId, deviceInfo, options = {}) {
  const sessionToken = this.generateSessionToken();
  const refreshToken = options.includeRefresh ? this.generateRefreshToken() : null;

  const expiresAt = new Date(Date.now() + (options.rememberMe ? 30 : 24) * 60 * 60 * 1000);

  const session = new this({
    userId,
    sessionToken,
    refreshToken,
    deviceInfo,
    isRememberMe: options.rememberMe || false,
    expiresAt,
    loginMethod: options.loginMethod || 'password'
  });

  await session.save();
  return session;
};

// Método estático para encontrar sesión por token
userSessionSchema.statics.findByToken = function(token) {
  return this.findOne({
    sessionToken: token,
    isActive: true
  }).populate('userId');
};

// Método estático para invalidar todas las sesiones de un usuario
userSessionSchema.statics.invalidateUserSessions = function(userId, exceptSessionId = null) {
  const query = { userId, isActive: true };
  if (exceptSessionId) {
    query._id = { $ne: exceptSessionId };
  }

  return this.updateMany(query, { isActive: false });
};

// Método estático para limpiar sesiones expiradas
userSessionSchema.statics.cleanupExpired = function() {
  return this.updateMany(
    { expiresAt: { $lt: new Date() } },
    { isActive: false }
  );
};

// Método estático para obtener sesiones activas de un usuario
userSessionSchema.statics.getActiveSessions = function(userId) {
  return this.find({
    userId,
    isActive: true,
    expiresAt: { $gt: new Date() }
  }).sort({ lastActivity: -1 });
};

// Método estático para detectar sesiones sospechosas
userSessionSchema.statics.detectSuspiciousActivity = function(userId, currentIp) {
  // Buscar sesiones recientes desde IPs diferentes
  const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000);

  return this.find({
    userId,
    'deviceInfo.ipAddress': { $ne: currentIp },
    lastActivity: { $gte: oneHourAgo }
  });
};

// Utilidades para generar tokens
userSessionSchema.statics.generateSessionToken = function() {
  return require('crypto').randomBytes(64).toString('hex');
};

userSessionSchema.statics.generateRefreshToken = function() {
  return require('crypto').randomBytes(64).toString('hex');
};

// Usar la conexión específica de admin
const { admin } = global.databaseConnections || {};

// Si no hay conexión global, crear una temporal (para desarrollo/testing)
let UserSession;
if (admin) {
  UserSession = admin.model('UserSession', userSessionSchema);
} else {
  // Fallback para desarrollo - usar conexión por defecto
  console.warn('⚠️  Admin connection not available, using default connection for UserSession model');
  UserSession = mongoose.model('UserSession', userSessionSchema);
}

module.exports = UserSession;