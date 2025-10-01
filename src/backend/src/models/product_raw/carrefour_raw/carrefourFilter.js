const mongoose = require('mongoose');

const filterSchema = new mongoose.Schema({
  name: { type: String, required: true, unique: true }, // Nombre del filtro (ej: "orgánico")
  displayName: { type: String, required: true }, // Nombre para mostrar (ej: "Producto Orgánico")
  category: { type: String, required: true }, // Categoría del filtro (ej: "tipo", "origen", "características")
  type: {
    type: String,
    enum: ['select', 'multiselect', 'range', 'boolean'],
    default: 'multiselect'
  }, // Tipo de filtro
  values: [{ type: String }], // Valores posibles (para select/multiselect)
  minValue: { type: Number }, // Valor mínimo (para range)
  maxValue: { type: Number }, // Valor máximo (para range)
  unit: { type: String }, // Unidad (para range, ej: "kg", "lt", "$")
  description: { type: String }, // Descripción del filtro
  icon: { type: String }, // Icono o emoji para el filtro
  color: { type: String }, // Color para UI
  priority: { type: Number, default: 0 }, // Prioridad de ordenamiento
  active: { type: Boolean, default: true }, // Si el filtro está activo
  applicableCategories: [{ type: String }], // Categorías de productos donde aplica
  createdAt: { type: Date, default: Date.now },
  updatedAt: { type: Date, default: Date.now }
});

// Índices para optimización
filterSchema.index({ category: 1, active: 1 });
filterSchema.index({ applicableCategories: 1 });
filterSchema.index({ priority: -1 });

// Middleware para actualizar updatedAt
filterSchema.pre('save', function(next) {
  this.updatedAt = new Date();
  next();
});

// Usar la conexión específica de carrefour
const { carrefour } = global.databaseConnections || {};

// Función para obtener el modelo Filter (evita registro duplicado)
function getFilterModel() {
  if (carrefour) {
    // Verificar si el modelo ya existe en la conexión carrefour
    try {
      return carrefour.model('Filter');
    } catch (error) {
      // Si no existe, crearlo
      return carrefour.model('Filter', filterSchema);
    }
  } else {
    // Fallback para desarrollo - usar conexión por defecto
    console.warn('⚠️  Carrefour connection not available, using default connection for Filter model');
    try {
      return mongoose.model('Filter');
    } catch (error) {
      return mongoose.model('Filter', filterSchema);
    }
  }
}

module.exports = getFilterModel();