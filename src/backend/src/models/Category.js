const mongoose = require('mongoose');

const categorySchema = new mongoose.Schema({
  _id: { type: String, required: true }, // Usar string personalizado como ID
  name: { type: String, required: true, unique: true }, // Nombre interno único
  displayName: { type: String }, // Nombre para mostrar (opcional, usar name si no existe)
  description: { type: String },
  icon: { type: String },
  color: { type: String }, // Color para UI
  image: { type: String }, // Imagen de la categoría
  priority: { type: Number, default: 0 }, // Orden de prioridad
  active: { type: Boolean, default: true },
  featured: { type: Boolean, default: false }, // Si es categoría destacada
  parentCategory: { type: mongoose.Schema.Types.ObjectId, ref: 'Category' }, // Para jerarquías (opcional)
  metadata: {
    productCount: { type: Number, default: 0 }, // Cantidad de productos
    subcategoryCount: { type: Number, default: 0 }, // Cantidad de subcategorías
    lastUpdated: { type: Date }, // Última actualización de productos
    averagePrice: { type: Number }, // Precio promedio
    priceRange: {
      min: { type: Number },
      max: { type: Number }
    }
  },
  createdAt: { type: Date, default: Date.now },
  updatedAt: { type: Date, default: Date.now }
});

// Índices para optimización
categorySchema.index({ active: 1, priority: -1 });
categorySchema.index({ name: 1 });
categorySchema.index({ featured: 1 });

// Middleware para actualizar updatedAt
categorySchema.pre('save', function(next) {
  this.updatedAt = new Date();
  next();
});

module.exports = mongoose.model('Category', categorySchema);