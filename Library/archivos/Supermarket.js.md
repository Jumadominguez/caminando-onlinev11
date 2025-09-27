# Desglose de Archivo: Supermarket.js

## Propósito
Este archivo define el modelo de datos para supermercados en la plataforma de comparación de precios. El modelo ha sido expandido para capturar información detallada extraíble de las homepages de los supermercados, incluyendo datos técnicos, analíticos y de regionalización.

## Relaciones
- **Productos**: Referenciado por la colección `products` a través del campo `supermarket`
- **Categorías**: Referenciado por la colección `categories` para organización de productos
- **Scraping**: Utilizado por scripts de scraping para determinar qué supermercado procesar
- **API**: Expuesto a través de endpoints REST para gestión de supermercados

## Recreación
1. Crear archivo en `src/backend/src/models/Supermarket.js`
2. Importar mongoose: `const mongoose = require('mongoose');`
3. Definir schema con campos básicos y extendidos
4. Agregar índices para optimización de consultas
5. Implementar middleware para timestamps automáticos
6. Exportar modelo: `module.exports = mongoose.model('Supermarket', supermarketSchema);`

## Campos del Modelo

### Campos Básicos
| Campo | Tipo | Requerido | Descripción | Ejemplo |
|-------|------|-----------|-------------|---------|
| `_id` | String | Sí | ID personalizado del supermercado | `"carrefour"` |
| `name` | String | Sí | Nombre del supermercado | `"Carrefour"` |
| `logo` | String | No | URL del logo | `"https://carrefour.com.ar/logo.png"` |
| `website` | String | No | URL del sitio web | `"https://www.carrefour.com.ar"` |

### Información Geográfica y Regional
| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `country` | String | País del supermercado | `"Argentina"` |
| `language` | String | Idioma y locale | `"es-AR"` |
| `currency` | String | Moneda utilizada | `"ARS"` |
| `timezone` | String | Zona horaria | `"America/Argentina/Buenos_Aires"` |

### Información Técnica de Plataforma
| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `platform` | String | Plataforma e-commerce | `"VTEX"` |
| `platformVersion` | String | Versión de la plataforma | `"8.179.0"` |
| `theme` | String | Tema utilizado | `"carrefourar.theme"` |
| `themeVersion` | String | Versión del tema | `"81.20.0"` |
| `workspace` | String | Workspace de VTEX | `"master"` |

### Información de Dominio y Configuración
| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `domain` | String | Dominio principal | `"www.carrefour.com.ar"` |
| `charset` | String | Charset utilizado | `"utf-8"` |

### Sistemas de Analytics y Tracking
| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `analytics.googleAnalytics` | String | ID de Google Analytics | `"G-YL72LN8HLQ"` |
| `analytics.googleTagManager` | Array | IDs de Google Tag Manager | `["GTM-KVTJW8R", "GTM-WFHW8H9"]` |
| `analytics.facebookPixel` | String | ID de Facebook Pixel | `"383089335651837"` |
| `analytics.dynamicYield` | String | ID de Dynamic Yield | `"2.62.0"` |
| `analytics.activityFlow` | Boolean | Si usa Activity Flow | `true` |
| `analytics.relyApi` | String | ID de Rely API | `"5060"` |

### Componentes Principales
| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `components` | Array | Componentes utilizados | `[{name: "MegaMenu", version: "0-x"}, {name: "Minicart", version: "3-x"}]` |

### Información de Regionalización
| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `regionalization.enabled` | Boolean | Si tiene regionalización | `false` |
| `regionalization.regions` | Array | Regiones disponibles | `["CABA", "GBA"]` |
| `regionalization.defaultRegion` | String | Región por defecto | `"CABA"` |

### Metadatos de Homepage
| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `homepageMetadata.title` | String | Título de la página | `"Carrefour Argentina - Supermercado Online"` |
| `homepageMetadata.description` | String | Descripción meta | `"Comprá online en Carrefour Argentina"` |
| `homepageMetadata.keywords` | Array | Palabras clave | `["supermercado", "compras", "online"]` |
| `homepageMetadata.ogImage` | String | Imagen Open Graph | `"https://carrefour.com.ar/og-image.jpg"` |
| `homepageMetadata.favicon` | String | URL del favicon | `"https://carrefour.com.ar/favicon.ico"` |

### Estados y Timestamps
| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `active` | Boolean | Si el supermercado está activo | `true` |
| `lastScraped` | Date | Último scraping de productos | `2024-01-15T10:30:00Z` |
| `lastHomepageScraped` | Date | Último scraping de homepage | `2024-01-15T09:00:00Z` |
| `createdAt` | Date | Fecha de creación | `2024-01-01T00:00:00Z` |
| `updatedAt` | Date | Fecha de última actualización | `2024-01-15T10:30:00Z` |

## Índices de Base de Datos

```javascript
supermarketSchema.index({ active: 1, country: 1 }); // Para consultas activas por país
supermarketSchema.index({ platform: 1 }); // Para consultas por plataforma
supermarketSchema.index({ 'analytics.googleAnalytics': 1 }); // Para consultas por GA ID
```

## Ejemplo de Documento Completo

```json
{
  "_id": "carrefour",
  "name": "Carrefour",
  "logo": "https://carrefour.com.ar/logo.png",
  "website": "https://www.carrefour.com.ar",
  "country": "Argentina",
  "language": "es-AR",
  "currency": "ARS",
  "platform": "VTEX",
  "platformVersion": "8.179.0",
  "theme": "carrefourar.theme",
  "themeVersion": "81.20.0",
  "workspace": "master",
  "domain": "www.carrefour.com.ar",
  "charset": "utf-8",
  "analytics": {
    "googleAnalytics": "G-YL72LN8HLQ",
    "googleTagManager": ["GTM-KVTJW8R", "GTM-WFHW8H9"],
    "facebookPixel": "383089335651837",
    "dynamicYield": "2.62.0",
    "activityFlow": true,
    "relyApi": "5060"
  },
  "components": [
    {"name": "MegaMenu", "version": "0-x"},
    {"name": "Minicart", "version": "3-x"},
    {"name": "SearchBar", "version": "3-x"}
  ],
  "regionalization": {
    "enabled": false,
    "regions": [],
    "defaultRegion": ""
  },
  "homepageMetadata": {
    "title": "Carrefour Argentina - Supermercado Online",
    "description": "Comprá online en Carrefour Argentina. Encontrá ofertas, promociones y delivery a domicilio.",
    "keywords": ["supermercado", "compras", "online", "delivery"],
    "ogImage": "https://carrefour.com.ar/og-image.jpg",
    "favicon": "https://carrefour.com.ar/favicon.ico"
  },
  "active": true,
  "lastScraped": "2024-01-15T10:30:00.000Z",
  "lastHomepageScraped": "2024-01-15T09:00:00.000Z",
  "createdAt": "2024-01-01T00:00:00.000Z",
  "updatedAt": "2024-01-15T10:30:00.000Z"
}
```

## Middleware Implementado

### Actualización Automática de Timestamps
```javascript
supermarketSchema.pre('save', function(next) {
  this.updatedAt = new Date();
  next();
});
```

## Casos de Uso

### 1. Scraping de Productos
- Verificar si supermercado está activo: `find({ active: true })`
- Obtener configuración regional: `findOne({ _id: "carrefour" }).regionalization`

### 2. Análisis de Plataformas
- Contar supermercados por plataforma: `aggregate([{ $group: { _id: "$platform", count: { $sum: 1 } } }])`
- Encontrar supermercados con VTEX: `find({ platform: "VTEX" })`

### 3. Gestión de Analytics
- Obtener IDs de Google Analytics: `find({}, { "analytics.googleAnalytics": 1 })`
- Supermercados con Facebook Pixel: `find({ "analytics.facebookPixel": { $exists: true } })`

### 4. Monitoreo de Scraping
- Supermercados que necesitan re-scraping: `find({ lastHomepageScraped: { $lt: new Date(Date.now() - 24*60*60*1000) } })`

## Fecha de Incorporación
15 de enero de 2024

## Feature Asociada
Homepage Metadata Extraction - Expansión del modelo de supermercados para capturar información técnica y analítica de las plataformas e-commerce.

## Commit Relacionado
[FEAT-001] Expandir modelo Supermarket con datos de homepage</content>
<parameter name="filePath">d:\dev\caminando-onlinev11\Library\archivos\Supermarket.js.md