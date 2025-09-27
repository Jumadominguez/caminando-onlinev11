# Desglose de Archivo: Product.js

## Propósito
Este archivo define el modelo de datos para productos en la plataforma de comparación de precios. Los productos representan el nivel más granular de información, conteniendo precios, características y relaciones jerárquicas.

## Relaciones
- **Supermercados**: Referencia a la colección `supermarkets` por ID
- **Categorías**: Referencia a la colección `categories` por ID
- **Subcategorías**: Referencia a la colección `subcategories` por ID
- **Tipos de Producto**: Referencia a la colección `producttypes` por ID
- **Ofertas**: Referencia a la colección `offers` por array de IDs
- **Filtros**: Array de strings con filtros aplicables
- **API**: Expuesto a través de endpoints REST para comparación de precios

## Recreación
1. Crear archivo en `src/backend/src/models/Product.js`
2. Importar mongoose: `const mongoose = require('mongoose');`
3. Definir schema con campos de producto, precios y jerarquía completa
4. Agregar validaciones personalizadas y middleware automático
5. Implementar métodos de instancia para cálculos de precio
6. Agregar índices únicos y compuestos para optimización
7. Exportar modelo: `module.exports = mongoose.model('Product', productSchema);`

## Validaciones y Restricciones
27 de septiembre de 2025

## Feature Asociada
Product Model Enhancement - Mejora completa del modelo de productos con validaciones, middleware automático, métodos de instancia y índices únicos para mayor robustez y funcionalidad.

## Commit Relacionado
[FEAT-002] Agregar validaciones, middleware y métodos al modelo Products de Campos
- **price**: Debe ser un número positivo (≥ 0)
- **listPrice**: Debe ser un número positivo (≥ 0) si se especifica
- **discount**: Debe estar entre 0 y 100 (%)
- **quantity**: Debe ser un número positivo (≥ 0) si se especifica
- **ean**: Debe tener exactamente 13 dígitos numéricos si se especifica
- **weight**: Debe ser un número positivo (≥ 0) si se especifica
- **pricePerKilo**: Debe ser un número positivo (≥ 0) si se especifica
- **pricePerLitre**: Debe ser un número positivo (≥ 0) si se especifica

### Índices Únicos
- **ean**: Índice único (sparse) para evitar EANs duplicados
- **sku**: Índice único (sparse) para evitar SKUs duplicados

## Métodos de Instancia

### getFinalPrice()
```javascript
// Calcula el precio final aplicando el descuento
const finalPrice = product.getFinalPrice(); // Retorna precio con descuento aplicado
```

### hasFilters(...filters)
```javascript
// Verifica si el producto tiene todos los filtros especificados
const hasOrganic = product.hasFilters('organico'); // true/false
const hasMultiple = product.hasFilters('organico', 'sin-lactosa'); // true si tiene ambos
```

### getFormattedPrice()
```javascript
// Retorna el precio formateado como string
const formatted = product.getFormattedPrice(); // "$150.50"
```

### isOnSale()
```javascript
// Verifica si el producto está en oferta (tiene descuento y precio menor al de lista)
const onSale = product.isOnSale(); // true/false
```

## Métodos Estáticos

### findByFilters(filters)
```javascript
// Busca productos que tengan al menos uno de los filtros especificados y estén disponibles
const products = await Product.findByFilters(['organico', 'sin-lactosa']);
```

## Middleware Automático

### Actualización de updatedAt
```javascript
// Se ejecuta automáticamente antes de guardar cualquier cambio
productSchema.pre('save', function(next) {
  this.updatedAt = new Date();
  next();
});
```

## Ejemplo de Documento Completomparación de precios. El modelo captura toda la información relevante de productos extraídos de diferentes supermercados, incluyendo precios, categorías, disponibilidad y filtros aplicables.

## Relaciones
- **Supermercados**: Referenciado por la colección `supermarkets` a través del campo `supermarket`
- **Categorías**: Referenciado por la colección `categories` para organización jerárquica
- **Subcategorías**: Referenciado por la colección `subcategories` para clasificación detallada
- **API**: Expuesto a través de endpoints REST para consultas y comparaciones de productos

## Recreación
1. Crear archivo en `src/backend/src/models/Product.js`
2. Importar mongoose: `const mongoose = require('mongoose');`
3. Definir schema con campos de producto y filtros
4. Agregar índices para optimización de consultas
5. Exportar modelo: `module.exports = mongoose.model('Product', productSchema);`

## Campos del Modelo

### Información Básica del Producto
| Campo | Tipo | Requerido | Descripción | Ejemplo |
|-------|------|-----------|-------------|---------|
| `_id` | ObjectId | Automático | ID único generado por MongoDB | `507f1f77bcf86cd799439011` |
| `name` | String | Sí | Nombre del producto | `"Leche Entera La Serenísima"` |
| `price` | Number | Sí | Precio actual del producto | `150.50` | `min: 0` |
| `listPrice` | Number | No | Precio de lista (sin descuento) | `180.00` | `min: 0` |
| `discount` | Number | No | Porcentaje de descuento | `15` | `min: 0, max: 100` |
| `brand` | String | No | Marca del producto | `"La Serenísima"` |
| `description` | String | No | Descripción detallada | `"Leche entera pasteurizada"` |

### Información de Ubicación y Categorización
| Campo | Tipo | Requerido | Descripción | Ejemplo |
|-------|------|-----------|-------------|---------|
| `supermarket` | String | Sí | ID del supermercado | `"carrefour"` |
| `category` | String | Sí | Categoría del producto | `"lacteos"` |
| `subcategory` | String | No | Subcategoría del producto | `"leches"` |
| `productType` | String | No | Tipo específico de producto | `"leche-entera"` |

### Información de Cantidad y Unidad
| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `unit` | String | Unidad de medida | `"lt"` |
| `quantity` | Number | Cantidad por unidad | `1` |

### Información de Disponibilidad y Medios
| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `isAvailable` | Boolean | Si el producto está disponible | `true` |
| `image` | String | URL de la imagen del producto | `"https://carrefour.com.ar/imagen.jpg"` |
| `url` | String | URL completa de la página del producto | `"https://carrefour.com.ar/producto/leche-entera"` |

### Información Técnica y Códigos
| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `ean` | String | Código EAN del producto | `"7791234567890"` |
| `sku` | String | Código SKU del producto | `"CAR-LEC-001"` |
| `weight` | Number | Peso del producto en kg | `1.0` |
| `dimensions` | String | Dimensiones del producto | `"10x5x20 cm"` |

### Información de Precios Calculados
| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `pricePerKilo` | Number | Precio por kilo del producto | `450.50` |
| `pricePerLitre` | Number | Precio por litro del producto | `450.50` |

### Filtros y Características
| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `filters` | Array | Array de filtros/tags aplicables | `["orgánico", "sin lactosa", "light"]` |
| `offers` | Array | IDs de ofertas aplicables al producto | `["507f1f77bcf86cd799439011", "507f1f77bcf86cd799439012"]` |

### Timestamps
| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-----------|-------------|---------|
| `createdAt` | Date | Fecha de creación | `2024-01-15T10:00:00Z` |
| `updatedAt` | Date | Fecha de última actualización | `2024-01-20T14:30:00Z` |
| Campo | Tipo | Requerido | Descripción | Ejemplo |
|-------|------|-----------|-------------|---------|
| `supermarket` | String | Sí | ID del supermercado | `"carrefour"` |
| `category` | String | Sí | Categoría principal | `"Lácteos"` |
| `subcategory` | String | No | Subcategoría | `"Leche"` |
| `productType` | String | No | Tipo específico de producto | `"Leche entera"` |

### Información de Cantidad y Unidad
| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `unit` | String | Unidad de medida | `"lt"` |
| `quantity` | Number | Cantidad por unidad | `1` |

### Información de Disponibilidad y Medios
| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `isAvailable` | Boolean | Si el producto está disponible | `true` |
| `image` | String | URL de la imagen del producto | `"https://carrefour.com.ar/imagen.jpg"` |
| `url` | String | URL completa de la página del producto | `"https://carrefour.com.ar/producto/leche-entera"` |

### Filtros y Características
| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `filters` | Array | Array de filtros aplicables | `["orgánico", "sin lactosa", "light"]` |

### Timestamps
| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `lastUpdated` | Date | Última actualización del producto | `2024-01-15T10:30:00Z` |
| `createdAt` | Date | Fecha de creación del registro | `2024-01-01T00:00:00Z` |

## Índices de Base de Datos

```javascript
// Índices para optimización de consultas
productSchema.index({ name: 1 }); // Búsqueda por nombre
productSchema.index({ price: 1 }); // Ordenamiento por precio
productSchema.index({ supermarket: 1 }); // Filtrado por supermercado
productSchema.index({ category: 1 }); // Filtrado por categoría
productSchema.index({ category: 1, subcategory: 1 }); // Navegación jerárquica
productSchema.index({ supermarket: 1, category: 1 }); // Productos por supermercado y categoría
productSchema.index({ price: 1, category: 1 }); // Precios por categoría
productSchema.index({ productType: 1 }); // Filtrado por tipo de producto
productSchema.index({ filters: 1 }); // Filtrado por características/tags
productSchema.index({ ean: 1 }); // Búsqueda por EAN
productSchema.index({ sku: 1 }); // Búsqueda por SKU
productSchema.index({ pricePerKilo: 1 }); // Búsqueda por precio por kilo
productSchema.index({ pricePerLitre: 1 }); // Búsqueda por precio por litro
```

## Ejemplo de Documento Completo

```json
{
  "_id": "507f1f77bcf86cd799439011",
  "name": "Leche Entera La Serenísima",
  "price": 150.50,
  "listPrice": 180.00,
  "discount": 15,
  "supermarket": "carrefour",
  "category": "lacteos",
  "subcategory": "leches",
  "brand": "La Serenísima",
  "description": "Leche entera pasteurizada de 1 litro",
  "image": "https://carrefour.com.ar/leche-serenisima.jpg",
  "url": "https://carrefour.com.ar/producto/leche-entera-serenisima",
  "unit": "lt",
  "quantity": 1,
  "isAvailable": true,
  "productType": "leche-entera",
  "filters": ["organico", "sin-lactosa", "light"],
  "offers": ["507f1f77bcf86cd799439011", "507f1f77bcf86cd799439012"],
  "ean": "7791234567890",
  "sku": "CAR-LEC-001",
  "weight": 1.0,
  "dimensions": "10x5x20 cm",
  "pricePerKilo": 150.50,
  "pricePerLitre": 150.50,
  "updatedAt": "2024-01-15T10:30:00.000Z",
  "createdAt": "2024-01-01T00:00:00.000Z"
}
```

## Casos de Uso

### 1. Búsqueda y Filtrado
- **Por nombre**: `find({ name: /leche/i })`
- **Por precio**: `find({ price: { $gte: 100, $lte: 200 } })`
- **Por supermercado**: `find({ supermarket: "carrefour" })`
- **Por categoría**: `find({ category: "lacteos" })`
- **Por filtros**: `find({ filters: { $in: ["organico", "sin-lactosa"] } })`
- **Por EAN**: `find({ ean: "7791234567890" })`
- **Por SKU**: `find({ sku: "CAR-LEC-001" })`

### 2. Comparación de Precios
- **Mismo producto en diferentes supermercados**: `find({ name: /leche serenisima/i })`
- **Productos más baratos por categoría**: `find({ category: "lacteos" }).sort({ price: 1 })`
- **Mejor precio por kilo**: `find({ category: "carnes" }).sort({ pricePerKilo: 1 })`
- **Mejor precio por litro**: `find({ category: "bebidas" }).sort({ pricePerLitre: 1 })`

### 3. Análisis de Disponibilidad
- **Productos disponibles**: `find({ isAvailable: true })`
- **Productos con descuento**: `find({ discount: { $gt: 0 } })`

### 4. Búsqueda por Características Técnicas
- **Por peso**: `find({ weight: { $gte: 1, $lte: 2 } })`
- **Por dimensiones**: `find({ dimensions: /10x5x20/ })`

## Consideraciones de Rendimiento

### Índices Estratégicos
- **Búsqueda por texto**: Índice en `name` para búsquedas rápidas
- **Filtrado compuesto**: Índices compuestos para consultas frecuentes
- **Rango de precios**: Índice en `price` para consultas de rango
- **Filtros múltiples**: Índice en `filters` para arrays

### Optimizaciones
- Usar `lean()` para consultas de solo lectura
- Implementar paginación para resultados grandes
- Cachear consultas frecuentes
- Usar aggregation pipelines para análisis complejos

## Fecha de Incorporación
27 de septiembre de 2025

## Feature Asociada
Product Model Enhancement - Configuración del modelo de productos con ObjectId estándar y campo de filtros para mejor categorización y búsqueda.

## Commit Relacionado
[FEAT-002] Configurar campo _id como ObjectId estándar en modelo Product</content>
<parameter name="filePath">d:\dev\caminando-onlinev11\Library\archivos\Product.js.md