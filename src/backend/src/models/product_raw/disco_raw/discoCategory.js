const mongoose = require('mongoose');

const categorySchema = new mongoose.Schema({
  _id: { type: String, required: true }, // Usar string personalizado como ID
  name: { type: String, required: true, unique: true }, // Nombre interno único
  displayName: { type: String }, // Nombre para mostrar (opcional, usar name si no existe)
  slug: { type: String, unique: true }, // Slug para URLs amigables
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
categorySchema.index({ url: 1 });
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

// Usar la conexión específica de disco
const { disco } = global.databaseConnections || {};

// Si no hay conexión global, crear una temporal (para desarrollo/testing)
let Category;
if (disco) {
  Category = disco.model('Category', categorySchema);
} else {
  // Fallback para desarrollo - usar conexión por defecto
  console.warn('⚠️  Disco connection not available, using default connection for Category model');
  Category = mongoose.model('Category', categorySchema);
}

module.exports = Category;