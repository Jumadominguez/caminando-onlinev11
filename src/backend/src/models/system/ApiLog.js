const mongoose = require('mongoose');

const apiLogSchema = new mongoose.Schema({
  // Información de la solicitud
  method: {
    type: String,
    enum: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'],
    required: true
  },
  url: {
    type: String,
    required: true
  },
  headers: {
    type: Map,
    of: String
  },

  // Parámetros de la solicitud
  queryParams: {
    type: Map,
    of: String
  },
  body: mongoose.Schema.Types.Mixed, // Para datos POST/PUT

  // Información de respuesta
  statusCode: Number,
  responseTime: Number, // en milisegundos
  responseSize: Number, // en bytes
  responseHeaders: {
    type: Map,
    of: String
  },

  // Información del cliente
  userAgent: String,
  ipAddress: String,
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User'
  },

  // Categorización
  apiType: {
    type: String,
    enum: ['supermarket_scraping', 'payment_gateway', 'shipping_api', 'geocoding', 'validation', 'external_service'],
    required: true
  },
  supermarketId: String, // Si es scraping de supermercado específico
  endpoint: String, // Endpoint específico llamado

  // Estado y resultado
  success: {
    type: Boolean,
    default: false
  },
  error: {
    message: String,
    code: String,
    details: mongoose.Schema.Types.Mixed
  },

  // Metadata de performance
  timestamp: {
    type: Date,
    default: Date.now,
    index: true
  },
  duration: Number, // Duración total en ms
  retryCount: {
    type: Number,
    default: 0
  },

  // Información de rate limiting
  rateLimit: {
    limit: Number,
    remaining: Number,
    resetTime: Date
  },

  // Información adicional
  tags: [String], // Tags para categorización adicional
  correlationId: String, // ID para rastrear requests relacionados
  sessionId: String,

  // Información de debugging
  stackTrace: String,
  requestId: String // ID único de la solicitud

}, {
  timestamps: false // Usamos timestamp manual
});

// Índices para optimizar consultas
apiLogSchema.index({ apiType: 1, timestamp: -1 });
apiLogSchema.index({ supermarketId: 1, timestamp: -1 });
apiLogSchema.index({ userId: 1, timestamp: -1 });
apiLogSchema.index({ success: 1, timestamp: -1 });
apiLogSchema.index({ statusCode: 1, timestamp: -1 });
apiLogSchema.index({ method: 1, apiType: 1, timestamp: -1 });
apiLogSchema.index({ correlationId: 1 });
apiLogSchema.index({ tags: 1 });

// TTL index para limpiar logs antiguos (30 días)
apiLogSchema.index({ timestamp: 1 }, {
  expireAfterSeconds: 30 * 24 * 60 * 60
});

// Método estático para logging de solicitud
apiLogSchema.statics.logRequest = async function(logData) {
  try {
    const log = new this(logData);
    await log.save();
    return log;
  } catch (error) {
    console.error('Error logging API request:', error);
    // No lanzamos error para no interrumpir el flujo principal
  }
};

// Método estático para obtener estadísticas de API
apiLogSchema.statics.getApiStats = function(apiType, hours = 24) {
  const cutoffDate = new Date(Date.now() - (hours * 60 * 60 * 1000));

  return this.aggregate([
    {
      $match: {
        apiType,
        timestamp: { $gte: cutoffDate }
      }
    },
    {
      $group: {
        _id: null,
        totalRequests: { $sum: 1 },
        successfulRequests: {
          $sum: { $cond: ['$success', 1, 0] }
        },
        failedRequests: {
          $sum: { $cond: ['$success', 0, 1] }
        },
        averageResponseTime: { $avg: '$responseTime' },
        totalResponseTime: { $sum: '$responseTime' },
        errorCount: {
          $sum: { $cond: ['$error', 1, 0] }
        }
      }
    },
    {
      $project: {
        totalRequests: 1,
        successfulRequests: 1,
        failedRequests: 1,
        successRate: {
          $multiply: [
            { $divide: ['$successfulRequests', '$totalRequests'] },
            100
          ]
        },
        averageResponseTime: 1,
        totalResponseTime: 1,
        errorCount: 1,
        errorsByCode: {
          $function: {
            body: `
              const errors = this.error || [];
              const grouped = {};
              errors.forEach(err => {
                const code = err.code || 'unknown';
                grouped[code] = (grouped[code] || 0) + 1;
              });
              return grouped;
            `,
            args: ['$error'],
            lang: 'js'
          }
        }
      }
    }
  ]);
};

// Método estático para obtener logs de errores recientes
apiLogSchema.statics.getRecentErrors = function(apiType = null, limit = 50) {
  const matchStage = { success: false };
  if (apiType) {
    matchStage.apiType = apiType;
  }

  return this.find(matchStage)
    .sort({ timestamp: -1 })
    .limit(limit)
    .select('method url statusCode error responseTime timestamp apiType supermarketId');
};

// Método estático para detectar patrones de error
apiLogSchema.statics.detectErrorPatterns = function(hours = 24) {
  const cutoffDate = new Date(Date.now() - (hours * 60 * 60 * 1000));

  return this.aggregate([
    {
      $match: {
        success: false,
        timestamp: { $gte: cutoffDate }
      }
    },
    {
      $group: {
        _id: {
          apiType: '$apiType',
          statusCode: '$statusCode',
          errorCode: '$error.code'
        },
        count: { $sum: 1 },
        lastOccurrence: { $max: '$timestamp' },
        affectedUrls: { $addToSet: '$url' }
      }
    },
    {
      $sort: { count: -1 }
    },
    {
      $limit: 20
    }
  ]);
};

// Método estático para obtener métricas de performance por supermercado
apiLogSchema.statics.getSupermarketPerformance = function(hours = 24) {
  const cutoffDate = new Date(Date.now() - (hours * 60 * 60 * 1000));

  return this.aggregate([
    {
      $match: {
        apiType: 'supermarket_scraping',
        timestamp: { $gte: cutoffDate }
      }
    },
    {
      $group: {
        _id: '$supermarketId',
        totalRequests: { $sum: 1 },
        successfulRequests: {
          $sum: { $cond: ['$success', 1, 0] }
        },
        averageResponseTime: { $avg: '$responseTime' },
        errorRate: {
          $avg: { $cond: ['$success', 0, 1] }
        }
      }
    },
    {
      $project: {
        supermarketId: '$_id',
        totalRequests: 1,
        successfulRequests: 1,
        successRate: {
          $multiply: [
            { $divide: ['$successfulRequests', '$totalRequests'] },
            100
          ]
        },
        averageResponseTime: 1,
        errorRate: {
          $multiply: ['$errorRate', 100]
        }
      }
    },
    {
      $sort: { successRate: -1 }
    }
  ]);
};

// Usar la conexión específica de operations
const { operations } = global.databaseConnections || {};

// Si no hay conexión global, crear una temporal (para desarrollo/testing)
let ApiLog;
if (operations) {
  ApiLog = operations.model('ApiLog', apiLogSchema);
} else {
  // Fallback para desarrollo - usar conexión por defecto
  console.warn('⚠️  Operations connection not available, using default connection for ApiLog model');
  ApiLog = mongoose.model('ApiLog', apiLogSchema);
}

module.exports = ApiLog;