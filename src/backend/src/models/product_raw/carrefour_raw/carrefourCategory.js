const mongoose = require('mongoose');

const categorySchema = new mongoose.Schema({
  // _id será ObjectId generado automáticamente por MongoDB
  name: { type: String, required: true, unique: true }, // Nombre interno único
  displayName: { type: String }, // Nombre para mostrar (opcional, usar name si no existe)
  slug: { type: String, required: true, unique: true }, // Slug para URLs amigables (identificador único)
  url: { type: String, required: true }, // URL completa de la categoría en el sitio web
  subcategories: [{ type: mongoose.Schema.Types.ObjectId, ref: 'Subcategory' }], // Subcategorías que pertenecen a esta categoría
  active: { type: Boolean, default: true },
  featured: { type: Boolean, default: false }, // Si es categoría destacada
  metadata: {
    productCount: { type: Number, default: 0 }, // Cantidad de productos
    subcategoryCount: { type: Number, default: 0 }, // Cantidad de subcategorías
    lastUpdated: { type: Date } // Última actualización de productos
  },
  createdAt: { type: Date, default: Date.now },
  updatedAt: { type: Date, default: Date.now }
});

// Índices para optimización
categorySchema.index({ active: 1 });
categorySchema.index({ featured: 1 });
categorySchema.index({ subcategories: 1 }); // Índice para consultas de subcategorías

// Middleware para actualizar updatedAt
categorySchema.pre('save', function(next) {
  this.updatedAt = new Date();
  next();
});

// Método para obtener subcategorías asociadas con populate
categorySchema.methods.getSubcategories = function() {
  return this.populate('subcategories');
};

// Método para sincronizar array de subcategorías (útil para mantenimiento)
categorySchema.methods.syncSubcategories = async function() {
  const Subcategory = mongoose.model('Subcategory');
  const subcategories = await Subcategory.find({ category: this._id }).select('_id');
  this.subcategories = subcategories.map(s => s._id);
  return this.save();
};

// Usar la conexión específica de carrefour
const { carrefour } = global.databaseConnections || {};

// Función para obtener el modelo Category (evita registro duplicado)
function getCategoryModel() {
  if (carrefour) {
    // Verificar si el modelo ya existe en la conexión carrefour
    try {
      return carrefour.model('Category');
    } catch (error) {
      // Si no existe, crearlo
      return carrefour.model('Category', categorySchema);
    }
  } else {
    // Fallback para desarrollo - usar conexión por defecto
    console.warn('⚠️  Carrefour connection not available, using default connection for Category model');
    try {
      return mongoose.model('Category');
    } catch (error) {
      return mongoose.model('Category', categorySchema);
    }
  }
}

module.exports = getCategoryModel();