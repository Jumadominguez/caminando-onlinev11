const mongoose = require('mongoose');

const subcategorySchema = new mongoose.Schema({
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
  category: { type: String, ref: 'Category', required: true }, // Referencia a categoría padre
  priority: { type: Number, default: 0 }, // Orden dentro de la categoría
  active: { type: Boolean, default: true },
  featured: { type: Boolean, default: false }, // Si es subcategoría destacada
  metadata: {
    productCount: { type: Number, default: 0 }, // Cantidad de productos
    productTypeCount: { type: Number, default: 0 }, // Cantidad de tipos de producto
    lastUpdated: { type: Date }, // Última actualización de productos
    prevExtracted: { type: Boolean, default: false } // Si se extrajeron subcategorías anteriormente
  },
  createdAt: { type: Date, default: Date.now },
  updatedAt: { type: Date, default: Date.now }
});

// Índices para optimización
subcategorySchema.index({ category: 1, active: 1, priority: -1 });
subcategorySchema.index({ name: 1 });
subcategorySchema.index({ active: 1 });

// Middleware para actualizar updatedAt
subcategorySchema.pre('save', function(next) {
  this.updatedAt = new Date();
  
  // Generar slug automáticamente si no existe
  if (!this.slug && this.name) {
    this.slug = this.generateSlug(this.name);
  }
  
  // Generar URL completa automáticamente
  if (this.category && this.slug) {
    this.url = `/productos/${this.category}/${this.slug}`;
  }
  
  next();
});

// Método para generar slug desde un string
subcategorySchema.methods.generateSlug = function(text) {
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
subcategorySchema.methods.getUrl = function() {
  // Retornar URL almacenada si existe, sino calcularla
  return this.url || `/productos/${this.category}/${this.slug}`;
};

// Método estático para buscar por slug
subcategorySchema.statics.findBySlug = function(slug) {
  return this.findOne({ slug: slug, active: true });
};

// Método estático para buscar por URL completa
subcategorySchema.statics.findByUrl = function(url) {
  return this.findOne({ url: url, active: true });
};

// Usar la conexión específica de disco
const { disco } = global.databaseConnections || {};

// Si no hay conexión global, crear una temporal (para desarrollo/testing)
let Subcategory;
if (disco) {
  Subcategory = disco.model('Subcategory', subcategorySchema);
} else {
  // Fallback para desarrollo - usar conexión por defecto
  console.warn('⚠️  Disco connection not available, using default connection for Subcategory model');
  Subcategory = mongoose.model('Subcategory', subcategorySchema);
}

module.exports = Subcategory;