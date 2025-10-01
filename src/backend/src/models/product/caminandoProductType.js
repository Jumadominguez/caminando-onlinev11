const mongoose = require('mongoose');

const productTypeSchema = new mongoose.Schema({
  // _id será generado automáticamente por MongoDB como ObjectId
  name: { type: String, required: true }, // Nombre interno
  slug: { 
    type: String, 
    required: true, 
    unique: true,
    lowercase: true,
    trim: true,
    validate: {
      validator: function(v) {
        // Validar formato de slug (solo letras, números, guiones)
        return /^[a-z0-9-]+$/.test(v);
      },
      message: 'El slug debe contener solo letras minúsculas, números y guiones'
    }
  }, // Slug para URLs amigables
  url: { type: String, unique: true }, // URL completa generada automáticamente
  displayName: { type: String }, // Nombre para mostrar (opcional)
  description: { type: String },
  category: { type: String, ref: 'Category', required: true }, // Referencia a categoría
  subcategory: { type: String, ref: 'Subcategory', required: true }, // Referencia a subcategoría
  products: [{ type: mongoose.Schema.Types.ObjectId, ref: 'Product' }], // Productos que pertenecen a este tipo
  priority: { type: Number, default: 0 }, // Orden dentro de la subcategoría
  active: { type: Boolean, default: true },
  featured: { type: Boolean, default: false }, // Si es tipo destacado
  filters: [{ type: String }], // Filtros aplicables a este tipo de producto
  metadata: {
    productCount: { type: Number, default: 0 }, // Cantidad de productos
    lastUpdated: { type: Date }, // Última actualización de productos
    },
  createdAt: { type: Date, default: Date.now },
  updatedAt: { type: Date, default: Date.now }
});

// Índices para optimización
productTypeSchema.index({ category: 1, subcategory: 1, active: 1, priority: -1 });
productTypeSchema.index({ active: 1 });
productTypeSchema.index({ filters: 1 });
productTypeSchema.index({ products: 1 }); // Índice para consultas de productos

// Middleware para actualizar updatedAt
productTypeSchema.pre('save', function(next) {
  this.updatedAt = new Date();
  
  // Generar slug automáticamente si no existe
  if (!this.slug && this.name) {
    this.slug = this.generateSlug(this.name);
  }
  
  // Generar URL completa automáticamente
  if (this.category && this.subcategory && this.slug) {
    this.url = `/productos/${this.category}/${this.subcategory}/${this.slug}`;
  }
  
  next();
});

// Método para generar slug desde un string
productTypeSchema.methods.generateSlug = function(text) {
  return text
    .toString()
    .toLowerCase()
    .trim()
    .replace(/\s+/g, '-')           // Reemplazar espacios con guiones
    .replace(/[^\w\-]+/g, '')       // Remover caracteres especiales
    .replace(/\-\-+/g, '-')         // Reemplazar múltiples guiones con uno
    .replace(/^-+/, '')             // Remover guiones al inicio
    .replace(/-+$/, '');            // Remover guiones al final
};

// Método para obtener URL completa
productTypeSchema.methods.getUrl = function() {
  // Retornar URL almacenada si existe, sino calcularla
  return this.url || `/productos/${this.category}/${this.subcategory}/${this.slug}`;
};

// Método estático para buscar por slug
productTypeSchema.statics.findBySlug = function(slug) {
  return this.findOne({ slug: slug, active: true });
};

// Método estático para buscar por URL completa
productTypeSchema.statics.findByUrl = function(url) {
  return this.findOne({ url: url, active: true });
};

// Método para obtener productos asociados con populate
productTypeSchema.methods.getProducts = function() {
  return this.populate('products');
};

// Método para sincronizar array de productos (útil para mantenimiento)
productTypeSchema.methods.syncProducts = async function() {
  const Product = mongoose.model('Product');
  const products = await Product.find({ productType: this._id }).select('_id');
  this.products = products.map(p => p._id);
  return this.save();
};

// Usar la conexión específica de processed
const { processed } = global.databaseConnections || {};

// Si no hay conexión global, crear una temporal (para desarrollo/testing)
let ProductType;
if (processed) {
  ProductType = processed.model('ProductType', productTypeSchema);
} else {
  // Fallback para desarrollo - usar conexión por defecto
  console.warn('⚠️  Processed connection not available, using default connection for ProductType model');
  ProductType = mongoose.model('ProductType', productTypeSchema);
}

module.exports = ProductType;