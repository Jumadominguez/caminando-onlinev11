const mongoose = require('mongoose');

const offerSchema = new mongoose.Schema({
  _id: { type: String, required: true }, // ID personalizado único
  title: { type: String, required: true }, // Título de la oferta
  description: { type: String }, // Descripción detallada
  type: {
    type: String,
    enum: ['percentage', 'fixed', 'buy_get', 'free_shipping', 'bundle', 'flash_sale'],
    required: true
  }, // Tipo de oferta

  // Configuración del descuento
  discount: {
    percentage: { type: Number }, // Porcentaje de descuento (ej: 20 para 20%)
    fixedAmount: { type: Number }, // Monto fijo de descuento (ej: 50 para $50 off)
    buyQuantity: { type: Number }, // Cantidad a comprar (para 2x1, 3x2)
    getQuantity: { type: Number }, // Cantidad gratis (para 2x1, 3x2)
    minimumPurchase: { type: Number } // Compra mínima para aplicar descuento
  },

  // Alcance de la oferta
  supermarket: { type: String, ref: 'Supermarket', required: true }, // Supermercado que ofrece
  applicableProducts: [{ type: String }], // IDs de productos específicos (vacío = todos)
  applicableCategories: [{ type: String }], // Categorías aplicables
  applicableSubcategories: [{ type: String }], // Subcategorías aplicables
  applicableProductTypes: [{ type: String }], // Tipos de producto aplicables

  // Vigencia temporal
  startDate: { type: Date, required: true },
  endDate: { type: Date, required: true },
  isActive: { type: Boolean, default: true },

  // Restricciones y límites
  usageLimit: { type: Number }, // Límite total de usos
  userLimit: { type: Number }, // Límite por usuario
  currentUsage: { type: Number, default: 0 }, // Usos actuales
  minimumQuantity: { type: Number, default: 1 }, // Cantidad mínima para aplicar

  // Información adicional
  terms: { type: String }, // Términos y condiciones
  image: { type: String }, // Imagen promocional
  badge: { type: String }, // Texto del badge (ej: "20% OFF")
  badgeColor: { type: String, default: '#FF5722' }, // Color del badge
  priority: { type: Number, default: 0 }, // Prioridad de ordenamiento

  // Metadatos
  metadata: {
    totalSavings: { type: Number, default: 0 }, // Ahorro total generado
    uniqueUsers: { type: Number, default: 0 }, // Usuarios únicos que usaron
    averageOrderValue: { type: Number }, // Valor promedio de órdenes con oferta
    conversionRate: { type: Number } // Tasa de conversión
  },

  // Sistema de códigos (opcional)
  couponCode: { type: String }, // Código de cupón
  autoApply: { type: Boolean, default: false }, // Si se aplica automáticamente

  createdAt: { type: Date, default: Date.now },
  updatedAt: { type: Date, default: Date.now }
});

// Índices para optimización
offerSchema.index({ supermarket: 1, isActive: 1, endDate: -1 });
offerSchema.index({ type: 1, isActive: 1 });
offerSchema.index({ applicableProducts: 1 });
offerSchema.index({ startDate: 1, endDate: 1 });
offerSchema.index({ couponCode: 1 });

// Middleware para actualizar updatedAt
offerSchema.pre('save', function(next) {
  this.updatedAt = new Date();
  next();
});

// Método para verificar si la oferta está vigente
offerSchema.methods.isValid = function() {
  const now = new Date();
  return this.isActive &&
         now >= this.startDate &&
         now <= this.endDate &&
         (!this.usageLimit || this.currentUsage < this.usageLimit);
};

// Método para verificar si aplica a un producto
offerSchema.methods.appliesToProduct = function(productId, category, subcategory, productType) {
  // Si hay productos específicos listados, verificar si el producto está incluido
  if (this.applicableProducts.length > 0) {
    return this.applicableProducts.includes(productId);
  }

  // Si no hay productos específicos, verificar categorías
  if (this.applicableCategories.length > 0 && !this.applicableCategories.includes(category)) {
    return false;
  }

  if (this.applicableSubcategories.length > 0 && !this.applicableSubcategories.includes(subcategory)) {
    return false;
  }

  if (this.applicableProductTypes.length > 0 && !this.applicableProductTypes.includes(productType)) {
    return false;
  }

  return true;
};

// Usar la conexión específica de dia
const { dia } = global.databaseConnections || {};

// Si no hay conexión global, crear una temporal (para desarrollo/testing)
let Offer;
if (dia) {
  Offer = dia.model('Offer', offerSchema);
} else {
  // Fallback para desarrollo - usar conexión por defecto
  console.warn('⚠️  Dia connection not available, using default connection for Offer model');
  Offer = mongoose.model('Offer', offerSchema);
}

module.exports = Offer;