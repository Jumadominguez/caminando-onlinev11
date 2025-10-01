const mongoose = require('mongoose');

const supermarketSchema = new mongoose.Schema({
  _id: { type: mongoose.Schema.Types.ObjectId, auto: true }, // ObjectId autogenerado
  code: { type: String, required: true, unique: true }, // Código único como "carrefour"
  name: { type: String, required: true },
  logo: { type: String },
  isoLogo: { type: String }, // Isotipo/logo alternativo
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
    favicon: { type: String },
    robots: { type: String }, // Meta robots directive
    storefront: { type: String }, // Storefront framework
    copyright: { type: String }, // Copyright holder
    author: { type: String } // Content author
  },

  // Políticas y términos legales
  legalInfo: {
    termsAndConditions: { type: String }, // URL de términos y condiciones
    privacyPolicy: { type: String }, // URL de política de privacidad
    consumerDefense: { type: String }, // URL de defensa del consumidor
    cookiePolicy: { type: String } // URL de política de cookies
  },

  // Información de Progressive Web App (PWA)
  pwa: {
    enabled: { type: Boolean, default: false },
    manifest: { type: String }, // URL del manifest.json
    themeColor: { type: String }, // Color del tema (#005BAA)
    icons: [{
      src: { type: String },
      sizes: { type: String },
      type: { type: String }
    }]
  },

  // Información de cookies y consentimiento
  cookieConsent: {
    provider: { type: String }, // Proveedor de gestión de cookies (ej: "OneTrust")
    privacyUrl: { type: String }, // URL de política de privacidad en cookies
    consentRequired: { type: Boolean, default: true }
  },

  // Estados y timestamps
  active: { type: Boolean, default: true },
  lastScraped: { type: Date }, // Último scraping de productos
  lastHomepageScraped: { type: Date } // Último scraping de homepage
}, {
  collection: 'supermarket-info', // Nombre de colección explícito para evitar pluralización
  timestamps: true // Habilita createdAt y updatedAt automáticos
});

// Índices para optimización
supermarketSchema.index({ active: 1, country: 1 });
supermarketSchema.index({ platform: 1 });
supermarketSchema.index({ 'analytics.googleAnalytics': 1 });

// Función para obtener el modelo Supermarket-info (evita registro duplicado)
function getSupermarketInfoModel() {
  // Intentar obtener la conexión carrefour si está disponible
  const carrefourConnection = global.databaseConnections?.carrefour;

  if (carrefourConnection) {
    // Verificar si el modelo ya existe en la conexión carrefour
    try {
      return carrefourConnection.model('SupermarketInfo', null, 'supermarket-info');
    } catch (error) {
      // Si no existe, crearlo con el nombre de colección explícito
      return carrefourConnection.model('SupermarketInfo', supermarketSchema, 'supermarket-info');
    }
  } else {
    // Fallback para desarrollo - usar conexión por defecto
    console.warn('⚠️  Carrefour connection not available, using default connection for Supermarket-info model');
    try {
      return mongoose.model('SupermarketInfo', null, 'supermarket-info');
    } catch (error) {
      return mongoose.model('SupermarketInfo', supermarketSchema, 'supermarket-info');
    }
  }
}

// Exportar la función en lugar del modelo directamente
module.exports = getSupermarketInfoModel;