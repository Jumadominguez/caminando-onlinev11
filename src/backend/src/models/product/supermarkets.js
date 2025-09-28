const mongoose = require('mongoose');

const supermarketSchema = new mongoose.Schema({
  _id: { type: String, required: true }, // Usar string personalizado como ID
  name: { type: String, required: true },
  logo: { type: String },
  website: { type: String },

  // Información geográfica y regional
  country: { type: String }, // País (ej: "Argentina")
  language: { type: String }, // Idioma (ej: "es-AR")
  currency: { type: String }, // Moneda (ej: "ARS")
  timezone: { type: String }, // Zona horaria

  // Información técnica de la plataforma
  platform: { type: String }, // Plataforma e-commerce (ej: "VTEX")
  platformVersion: { type: String }, // Versión de la plataforma (ej: "8.179.0")
  theme: { type: String }, // Tema utilizado (ej: "carrefourar.theme")
  themeVersion: { type: String }, // Versión del tema (ej: "81.20.0")
  workspace: { type: String }, // Workspace de VTEX (ej: "master")

  // Información de dominio y configuración
  domain: { type: String }, // Dominio principal (ej: "www.carrefour.com.ar")
  charset: { type: String }, // Charset utilizado (ej: "utf-8")

  // Sistemas de analytics y tracking
  analytics: {
    googleAnalytics: { type: String }, // ID de Google Analytics (ej: "G-YL72LN8HLQ")
    googleTagManager: [{ type: String }], // IDs de GTM (array)
    facebookPixel: { type: String }, // ID de Facebook Pixel
    dynamicYield: { type: String }, // ID de Dynamic Yield
    activityFlow: { type: Boolean }, // Si usa Activity Flow
    relyApi: { type: String } // ID de Rely API
  },

  // Componentes principales utilizados
  components: [{
    name: { type: String }, // Nombre del componente (ej: "MegaMenu")
    version: { type: String } // Versión del componente
  }],

  // Información de regionalización
  regionalization: {
    enabled: { type: Boolean, default: false },
    regions: [{ type: String }],
    defaultRegion: { type: String }
  },

  // Metadatos adicionales de la homepage
  homepageMetadata: {
    title: { type: String },
    description: { type: String },
    keywords: [{ type: String }],
    ogImage: { type: String },
    favicon: { type: String }
  },

  // Estados y timestamps
  active: { type: Boolean, default: true },
  lastScraped: { type: Date }, // Último scraping de productos
  lastHomepageScraped: { type: Date }, // Último scraping de homepage
  createdAt: { type: Date, default: Date.now },
  updatedAt: { type: Date, default: Date.now }
});

// Índices para optimización
supermarketSchema.index({ active: 1, country: 1 });
supermarketSchema.index({ platform: 1 });
supermarketSchema.index({ 'analytics.googleAnalytics': 1 });

// Middleware para actualizar updatedAt
supermarketSchema.pre('save', function(next) {
  this.updatedAt = new Date();
  next();
});

module.exports = mongoose.model('Supermarket', supermarketSchema);