const mongoose = require('mongoose');

const productSchema = new mongoose.Schema({
  name: { type: String, required: true, index: true },
  price: { 
    type: Number, 
    required: true, 
    index: true,
    min: [0, 'El precio debe ser positivo'] 
  }, // Precio de venta
  listPrice: { 
    type: Number,
    min: [0, 'El precio de lista debe ser positivo']
  }, // Precio de lista
  discount: { 
    type: Number, 
    default: 0,
    min: [0, 'El descuento no puede ser negativo'],
    max: [100, 'El descuento no puede exceder 100%']
  }, // Porcentaje de descuento
  supermarket: { type: String, required: true, index: true },
  category: { type: String, required: true, index: true },
  subcategory: { type: String },
  productType: { type: String }, // Tipo de producto filtrado (e.g., 'Leche entera')
  brand: { type: String },
  description: { type: String },
  image: { type: String },
  url: { type: String },
  unit: { type: String }, // kg, lt, unidades, etc.
  isAvailable: { type: Boolean, default: true },
  filters: [{ type: String }], // Array de filtros aplicables al producto (tags)
  offers: [{ type: mongoose.Schema.Types.ObjectId, ref: 'Offer' }], // Ofertas aplicables al producto
  ean: { 
    type: String,
    unique: true,
    sparse: true,
    validate: {
      validator: function(v) {
        // Validación básica de EAN (13 dígitos)
        return !v || /^\d{13}$/.test(v);
      },
      message: 'El EAN debe tener exactamente 13 dígitos'
    }
  }, // Código EAN del producto
  sku: { 
    type: String,
    unique: true,
    sparse: true
  }, // Código SKU del producto
  weight: { 
    type: Number,
    min: [0, 'El peso debe ser positivo']
  }, // Peso del producto en kg
  dimensions: { type: String }, // Dimensiones del producto
  pricePerKilo: { 
    type: Number,
    min: [0, 'El precio por kilo debe ser positivo']
  }, // Precio por kilo del producto
  pricePerLitre: { 
    type: Number,
    min: [0, 'El precio por litro debe ser positivo']
  }, // Precio por litro del producto
  updatedAt: { type: Date, default: Date.now }, // Última actualización
  createdAt: { type: Date, default: Date.now }
});

// Índices compuestos para consultas eficientes
productSchema.index({ category: 1, subcategory: 1 });
productSchema.index({ supermarket: 1, category: 1 });
productSchema.index({ price: 1, category: 1 });
productSchema.index({ productType: 1 }); // Índice para consultas por tipo de producto
productSchema.index({ filters: 1 }); // Índice para consultas por filtros/tags
productSchema.index({ offers: 1 }); // Índice para consultas por ofertas aplicables
productSchema.index({ pricePerKilo: 1 }); // Índice para búsquedas por precio por kilo
productSchema.index({ pricePerLitre: 1 }); // Índice para búsquedas por precio por litro

// Middleware para actualizar updatedAt automáticamente
productSchema.pre('save', function(next) {
  this.updatedAt = new Date();
  next();
});

// Método para calcular el precio final con descuento aplicado
productSchema.methods.getFinalPrice = function() {
  if (this.discount > 0) {
    return this.price * (1 - this.discount / 100);
  }
  return this.price;
};

// Método para verificar si el producto tiene ciertos filtros
productSchema.methods.hasFilters = function(...filters) {
  return filters.every(filter => this.filters.includes(filter));
};

// Método para obtener el precio formateado como string
productSchema.methods.getFormattedPrice = function() {
  return `$${this.price.toFixed(2)}`;
};

// Método para verificar si el producto está en oferta
productSchema.methods.isOnSale = function() {
  return this.discount > 0 && this.listPrice && this.price < this.listPrice;
};

// Método para obtener ofertas activas aplicables (requiere populate)
productSchema.methods.getActiveOffers = function() {
  if (!this.offers || this.offers.length === 0) return [];
  return this.offers.filter(offer => offer.isValid && offer.isValid());
};

// Método estático para buscar productos por filtros
productSchema.statics.findByFilters = function(filters) {
  return this.find({ filters: { $in: filters }, isAvailable: true });
};

// Usar la conexión específica de disco
const { disco } = global.databaseConnections || {};

// Si no hay conexión global, crear una temporal (para desarrollo/testing)
let Product;
if (disco) {
  Product = disco.model('Product', productSchema);
} else {
  // Fallback para desarrollo - usar conexión por defecto
  console.warn('⚠️  Disco connection not available, using default connection for Product model');
  Product = mongoose.model('Product', productSchema);
}

module.exports = Product;