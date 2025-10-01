const mongoose = require('mongoose');

const priceHistorySchema = new mongoose.Schema({
  // Referencias
  productId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Product',
    required: true
  },
  supermarketId: {
    type: String,
    required: true
  },

  // Información del producto al momento del precio
  productData: {
    name: { type: String, required: true },
    sku: String,
    brand: String,
    category: String,
    subcategory: String,
    productType: String
  },

  // Datos de precio
  price: {
    type: Number,
    required: true
  },
  listPrice: Number, // Precio de lista si aplica
  discount: Number, // Porcentaje de descuento
  discountAmount: Number, // Monto de descuento

  // Información adicional de precio
  currency: {
    type: String,
    default: 'ARS'
  },
  pricePerUnit: Number, // Precio por unidad de medida
  unit: String, // Unidad (kg, litro, unidad, etc.)

  // Metadatos del scraping
  scrapedAt: {
    type: Date,
    required: true,
    default: Date.now
  },
  scrapeSource: String, // URL específica donde se encontró el precio
  scrapeBatchId: String, // ID del batch de scraping

  // Información de stock/disponibilidad
  isAvailable: {
    type: Boolean,
    default: true
  },
  stockStatus: {
    type: String,
    enum: ['in_stock', 'low_stock', 'out_of_stock', 'discontinued'],
    default: 'in_stock'
  },

  // Información promocional
  isOnOffer: {
    type: Boolean,
    default: false
  },
  offerType: String, // Tipo de oferta (2x1, descuento, etc.)
  offerDescription: String,

  // Metadata adicional
  notes: String, // Notas sobre cambios inusuales
  confidence: {
    type: Number,
    min: 0,
    max: 1,
    default: 1
  } // Confianza en el precio scrapeado (0-1)

}, {
  timestamps: true
});

// Índices para optimizar consultas
priceHistorySchema.index({ productId: 1, scrapedAt: -1 });
priceHistorySchema.index({ supermarketId: 1, scrapedAt: -1 });
priceHistorySchema.index({ scrapedAt: -1 });
priceHistorySchema.index({ 'productData.category': 1, scrapedAt: -1 });
priceHistorySchema.index({ 'productData.brand': 1, scrapedAt: -1 });
priceHistorySchema.index({ isOnOffer: 1, scrapedAt: -1 });

// Virtual para calcular cambio porcentual (requiere comparación con precio anterior)
priceHistorySchema.virtual('priceChangePercent').get(function() {
  // Este virtual se calcula dinámicamente en queries
  return 0;
});

// Método estático para obtener historial de precios de un producto
priceHistorySchema.statics.getPriceHistory = function(productId, supermarketId = null, limit = 50) {
  const query = { productId };
  if (supermarketId) {
    query.supermarketId = supermarketId;
  }

  return this.find(query)
    .sort({ scrapedAt: -1 })
    .limit(limit)
    .populate('productId');
};

// Método estático para obtener último precio conocido
priceHistorySchema.statics.getLatestPrice = function(productId, supermarketId = null) {
  const query = { productId };
  if (supermarketId) {
    query.supermarketId = supermarketId;
  }

  return this.findOne(query).sort({ scrapedAt: -1 });
};

// Método estático para detectar cambios de precio
priceHistorySchema.statics.detectPriceChanges = function(hoursBack = 24) {
  const cutoffDate = new Date(Date.now() - (hoursBack * 60 * 60 * 1000));

  // Aggregate para encontrar productos con cambios recientes
  return this.aggregate([
    {
      $match: {
        scrapedAt: { $gte: cutoffDate }
      }
    },
    {
      $sort: { productId: 1, scrapedAt: -1 }
    },
    {
      $group: {
        _id: '$productId',
        latestPrice: { $first: '$price' },
        previousPrice: { $last: '$price' },
        latestData: { $first: '$$ROOT' },
        priceCount: { $sum: 1 }
      }
    },
    {
      $match: {
        $expr: { $ne: ['$latestPrice', '$previousPrice'] }
      }
    },
    {
      $project: {
        productId: '$_id',
        latestPrice: 1,
        previousPrice: 1,
        changePercent: {
          $multiply: [
            {
              $divide: [
                { $subtract: ['$latestPrice', '$previousPrice'] },
                '$previousPrice'
              ]
            },
            100
          ]
        },
        latestData: 1
      }
    }
  ]);
};

// Método estático para estadísticas de precios
priceHistorySchema.statics.getPriceStats = function(productId, supermarketId = null, days = 30) {
  const cutoffDate = new Date(Date.now() - (days * 24 * 60 * 60 * 1000));

  const matchStage = {
    productId: mongoose.Types.ObjectId(productId),
    scrapedAt: { $gte: cutoffDate }
  };

  if (supermarketId) {
    matchStage.supermarketId = supermarketId;
  }

  return this.aggregate([
    { $match: matchStage },
    {
      $group: {
        _id: null,
        minPrice: { $min: '$price' },
        maxPrice: { $max: '$price' },
        avgPrice: { $avg: '$price' },
        priceCount: { $sum: 1 },
        latestPrice: { $last: '$price' },
        firstPrice: { $first: '$price' }
      }
    }
  ]);
};

// Usar la conexión específica de carrefour
const { carrefour } = global.databaseConnections || {};

// Función para obtener el modelo PriceHistory (evita registro duplicado)
function getPriceHistoryModel() {
  if (carrefour) {
    // Verificar si el modelo ya existe en la conexión carrefour
    try {
      return carrefour.model('PriceHistory');
    } catch (error) {
      // Si no existe, crearlo
      return carrefour.model('PriceHistory', priceHistorySchema);
    }
  } else {
    // Fallback para desarrollo - usar conexión por defecto
    console.warn('⚠️  Carrefour connection not available, using default connection for PriceHistory model');
    try {
      return mongoose.model('PriceHistory');
    } catch (error) {
      return mongoose.model('PriceHistory', priceHistorySchema);
    }
  }
}

module.exports = getPriceHistoryModel();