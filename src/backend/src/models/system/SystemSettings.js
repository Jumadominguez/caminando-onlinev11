const mongoose = require('mongoose');

const systemSettingsSchema = new mongoose.Schema({
  // Identificador único de la configuración
  key: {
    type: String,
    required: true,
    unique: true,
    trim: true
  },

  // Valor de la configuración (puede ser cualquier tipo)
  value: mongoose.Schema.Types.Mixed,

  // Tipo de dato para validación
  type: {
    type: String,
    enum: ['string', 'number', 'boolean', 'object', 'array'],
    required: true
  },

  // Categoría para organización
  category: {
    type: String,
    enum: [
      'general',
      'scraping',
      'api',
      'security',
      'notifications',
      'payment',
      'shipping',
      'performance',
      'maintenance'
    ],
    default: 'general'
  },

  // Descripción de la configuración
  description: {
    type: String,
    trim: true
  },

  // Valor por defecto
  defaultValue: mongoose.Schema.Types.Mixed,

  // Validación
  validation: {
    required: { type: Boolean, default: false },
    min: Number,
    max: Number,
    pattern: String,
    enum: [String] // Valores permitidos
  },

  // Control de acceso
  isPublic: {
    type: Boolean,
    default: false
  },
  requiresRestart: {
    type: Boolean,
    default: false
  },

  // Metadata
  lastModifiedBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User'
  },
  tags: [String],

  // Control de versiones
  version: {
    type: Number,
    default: 1
  },
  previousValue: mongoose.Schema.Types.Mixed,

  // Estado
  isActive: {
    type: Boolean,
    default: true
  }

}, {
  timestamps: true
});

// Índices
systemSettingsSchema.index({ key: 1 }, { unique: true });
systemSettingsSchema.index({ category: 1, isActive: 1 });
systemSettingsSchema.index({ isPublic: 1 });
systemSettingsSchema.index({ tags: 1 });

// Método para validar valor según las reglas
systemSettingsSchema.methods.validateValue = function(value) {
  const validation = this.validation;

  if (validation.required && (value === null || value === undefined)) {
    throw new Error(`Setting ${this.key} is required`);
  }

  if (typeof value !== this.type) {
    throw new Error(`Setting ${this.key} must be of type ${this.type}`);
  }

  if (this.type === 'number') {
    if (validation.min !== undefined && value < validation.min) {
      throw new Error(`Setting ${this.key} must be at least ${validation.min}`);
    }
    if (validation.max !== undefined && value > validation.max) {
      throw new Error(`Setting ${this.key} must be at most ${validation.max}`);
    }
  }

  if (this.type === 'string' && validation.pattern) {
    const regex = new RegExp(validation.pattern);
    if (!regex.test(value)) {
      throw new Error(`Setting ${this.key} does not match required pattern`);
    }
  }

  if (validation.enum && validation.enum.length > 0) {
    if (!validation.enum.includes(value)) {
      throw new Error(`Setting ${this.key} must be one of: ${validation.enum.join(', ')}`);
    }
  }

  return true;
};

// Método para actualizar valor con validación
systemSettingsSchema.methods.updateValue = async function(newValue, modifiedBy = null) {
  // Validar el nuevo valor
  this.validateValue(newValue);

  // Guardar valor anterior
  this.previousValue = this.value;
  this.value = newValue;
  this.version += 1;

  if (modifiedBy) {
    this.lastModifiedBy = modifiedBy;
  }

  return this.save();
};

// Método estático para obtener configuración por clave
systemSettingsSchema.statics.getByKey = function(key) {
  return this.findOne({ key, isActive: true });
};

// Método estático para obtener configuraciones por categoría
systemSettingsSchema.statics.getByCategory = function(category) {
  return this.find({ category, isActive: true }).sort({ key: 1 });
};

// Método estático para obtener configuraciones públicas
systemSettingsSchema.statics.getPublicSettings = function() {
  return this.find({ isPublic: true, isActive: true })
    .select('key value type description')
    .sort({ category: 1, key: 1 });
};

// Método estático para inicializar configuraciones por defecto
systemSettingsSchema.statics.initializeDefaults = async function() {
  const defaultSettings = [
    // Configuraciones generales
    {
      key: 'app.name',
      value: 'Caminando Online',
      type: 'string',
      category: 'general',
      description: 'Nombre de la aplicación',
      defaultValue: 'Caminando Online',
      validation: { required: true }
    },
    {
      key: 'app.version',
      value: '1.0.0',
      type: 'string',
      category: 'general',
      description: 'Versión actual de la aplicación',
      defaultValue: '1.0.0'
    },
    {
      key: 'app.environment',
      value: 'development',
      type: 'string',
      category: 'general',
      description: 'Entorno de ejecución',
      defaultValue: 'development',
      validation: { enum: ['development', 'staging', 'production'] }
    },

    // Configuraciones de scraping
    {
      key: 'scraping.enabled',
      value: true,
      type: 'boolean',
      category: 'scraping',
      description: 'Habilitar scraping automático',
      defaultValue: true
    },
    {
      key: 'scraping.interval',
      value: 3600000, // 1 hora en ms
      type: 'number',
      category: 'scraping',
      description: 'Intervalo entre ejecuciones de scraping (ms)',
      defaultValue: 3600000,
      validation: { min: 60000 } // mínimo 1 minuto
    },
    {
      key: 'scraping.timeout',
      value: 30000,
      type: 'number',
      category: 'scraping',
      description: 'Timeout para requests de scraping (ms)',
      defaultValue: 30000,
      validation: { min: 5000, max: 120000 }
    },
    {
      key: 'scraping.maxRetries',
      value: 3,
      type: 'number',
      category: 'scraping',
      description: 'Número máximo de reintentos por request',
      defaultValue: 3,
      validation: { min: 0, max: 10 }
    },

    // Configuraciones de API
    {
      key: 'api.rateLimit.windowMs',
      value: 900000, // 15 minutos
      type: 'number',
      category: 'api',
      description: 'Ventana de tiempo para rate limiting (ms)',
      defaultValue: 900000
    },
    {
      key: 'api.rateLimit.max',
      value: 100,
      type: 'number',
      category: 'api',
      description: 'Número máximo de requests por ventana',
      defaultValue: 100,
      validation: { min: 1 }
    },

    // Configuraciones de seguridad
    {
      key: 'security.jwt.expiresIn',
      value: '24h',
      type: 'string',
      category: 'security',
      description: 'Tiempo de expiración de JWT',
      defaultValue: '24h'
    },
    {
      key: 'security.password.minLength',
      value: 8,
      type: 'number',
      category: 'security',
      description: 'Longitud mínima de contraseña',
      defaultValue: 8,
      validation: { min: 6, max: 128 }
    },

    // Configuraciones de notificaciones
    {
      key: 'notifications.email.enabled',
      value: true,
      type: 'boolean',
      category: 'notifications',
      description: 'Habilitar envío de emails',
      defaultValue: true
    },
    {
      key: 'notifications.push.enabled',
      value: true,
      type: 'boolean',
      category: 'notifications',
      description: 'Habilitar notificaciones push',
      defaultValue: true
    },

    // Configuraciones de performance
    {
      key: 'performance.cache.enabled',
      value: true,
      type: 'boolean',
      category: 'performance',
      description: 'Habilitar cache de respuestas',
      defaultValue: true
    },
    {
      key: 'performance.cache.ttl',
      value: 300, // 5 minutos
      type: 'number',
      category: 'performance',
      description: 'Tiempo de vida del cache (segundos)',
      defaultValue: 300,
      validation: { min: 60 }
    }
  ];

  const results = [];
  for (const setting of defaultSettings) {
    try {
      const existing = await this.findOne({ key: setting.key });
      if (!existing) {
        const newSetting = new this(setting);
        await newSetting.save();
        results.push({ key: setting.key, status: 'created' });
      } else {
        results.push({ key: setting.key, status: 'exists' });
      }
    } catch (error) {
      results.push({ key: setting.key, status: 'error', error: error.message });
    }
  }

  return results;
};

// Método para obtener valor tipado
systemSettingsSchema.methods.getTypedValue = function() {
  switch (this.type) {
    case 'number':
      return Number(this.value);
    case 'boolean':
      return Boolean(this.value);
    case 'string':
      return String(this.value);
    case 'object':
    case 'array':
      return this.value;
    default:
      return this.value;
  }
};

// Usar la conexión específica de operations
const { operations } = global.databaseConnections || {};

// Si no hay conexión global, crear una temporal (para desarrollo/testing)
let SystemSettings;
if (operations) {
  SystemSettings = operations.model('SystemSettings', systemSettingsSchema);
} else {
  // Fallback para desarrollo - usar conexión por defecto
  console.warn('⚠️  Operations connection not available, using default connection for SystemSettings model');
  SystemSettings = mongoose.model('SystemSettings', systemSettingsSchema);
}

module.exports = SystemSettings;