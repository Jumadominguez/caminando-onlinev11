# Desglose de Archivo:### Información Básica
| Campo | Tipo | Requerido | Descripción | Ejemplo |
|-------|------|-----------|-------------|---------|
| `_id` | ObjectId | Auto | ID generado por MongoDB | `ObjectId("507f1f77bcf86cd799439011")` |
| `name` | String | Sí | Nombre interno | `"leche-entera"` |
| `slug` | String | Sí | Slug para URLs amigables | `"leche-entera"` |
| `url` | String | Auto | URL completa generada | `"/productos/lacteos/leches/leche-entera"` |
| `displayName` | String | No | Nombre para mostrar | `"Leche Entera"` |
| `description` | String | No | Descripción del tipo | `"Leche de vaca entera pasteurizada"` |

### Relaciones Jerárquicas
| Campo | Tipo | Requerido | Descripción | Ejemplo |
|-------|------|-----------|-------------|---------|
| `category` | String | Sí | ID de la categoría padre | `"lacteos"` |
| `subcategory` | String | Sí | ID de la subcategoría padre | `"leches"` |
| `products` | Array[ObjectId] | No | Productos que pertenecen a este tipo | `[ObjectId("507f1f77bcf86cd799439011")]` |s

## Propósito
Este archivo define el modelo de datos para tipos específicos de productos en la plataforma de comparación de precios. Los tipos de producto representan el tercer y más granular nivel de organización jerárquica.

## Relaciones
- **Categorías**: Referencia a la colección `categories` como categoría padre
- **Subcategorías**: Referencia a la colección `subcategories` como subcategoría padre
- **Productos**: Referenciado por el campo `productType` en la colección `products`
- **Filtros**: Referencia a la colección `filters` para filtros aplicables
- **API**: Expuesto a través de endpoints REST para filtrado y navegación detallada

## Recreación
1. Crear archivo en `src/backend/src/models/ProductType.js`
2. Importar mongoose: `const mongoose = require('mongoose');`
3. Definir schema con campos de tipo de producto y jerarquía completa
4. Agregar índices para optimización de consultas
5. Implementar middleware para timestamps automáticos
6. Exportar modelo: `module.exports = mongoose.model('ProductType', productTypeSchema);`

## Campos del Modelo

### Información Básica
| Campo | Tipo | Requerido | Descripción | Ejemplo |
|-------|------|-----------|-------------|---------|
| `_id` | String | Sí | ID personalizado único | `"leche-entera"` |
| `name` | String | Sí | Nombre interno | `"leche-entera"` |
| `slug` | String | Sí | Slug para URLs amigables | `"leche-entera"` |
| `displayName` | String | No | Nombre para mostrar | `"Leche Entera"` |
| `description` | String | No | Descripción del tipo | `"Leche de vaca entera pasteurizada"` |

### Relaciones Jerárquicas
| Campo | Tipo | Requerido | Descripción | Ejemplo |
|-------|------|-----------|-------------|---------|
| `category` | String | Sí | ID de la categoría padre | `"lacteos"` |
| `subcategory` | String | Sí | ID de la subcategoría padre | `"leches"` |

### Información de Presentación
| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `icon` | String | Icono o emoji | `"🥛"` |
| `color` | String | Color para UI | `"#FFC107"` |

### Configuración y Estado
| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `priority` | Number | Orden dentro de la subcategoría | `1` |
| `active` | Boolean | Si está activo | `true` |
| `featured` | Boolean | Si es tipo destacado | `true` |

### Filtros Aplicables
| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `filters` | Array | Filtros aplicables a este tipo | `["organico", "light", "sin_lactosa"]` |

### Metadatos Estadísticos y Características
| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `metadata.productCount` | Number | Cantidad de productos | `85` |
| `metadata.lastUpdated` | Date | Última actualización | `2024-01-15T10:30:00Z` |
| `metadata.averagePrice` | Number | Precio promedio | `65.40` |
| `metadata.priceRange.min` | Number | Precio mínimo | `45.00` |
| `metadata.priceRange.max` | Number | Precio máximo | `120.00` |
| `metadata.commonBrands` | Array | Marcas comunes | `["La Serenísima", "Sancor"]` |
| `metadata.averageWeight` | Number | Peso promedio | `1.0` |
| `metadata.commonUnits` | Array | Unidades comunes | `["lt", "ml"]` |

### Timestamps
| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `createdAt` | Date | Fecha de creación | `2024-01-01T00:00:00Z` |
| `updatedAt` | Date | Fecha de actualización | `2024-01-15T10:30:00Z` |

## Índices de Base de Datos

```javascript
// Índices para optimización de consultas
productTypeSchema.index({ category: 1, subcategory: 1, active: 1, priority: -1 }); // Jerarquía completa
productTypeSchema.index({ name: 1 }); // Búsqueda por nombre
productTypeSchema.index({ slug: 1 }); // Índice único para slugs
productTypeSchema.index({ url: 1 }); // Índice único para URLs
productTypeSchema.index({ active: 1 }); // Tipos activos
productTypeSchema.index({ filters: 1 }); // Búsqueda por filtros
productTypeSchema.index({ products: 1 }); // Consultas de productos asociados
```

## Validaciones y Restricciones

### Validaciones de Campos
- **slug**: Debe contener solo letras minúsculas, números y guiones
- **slug**: Debe ser único en la colección
- **url**: Debe ser único en la colección

### Índices Únicos
- **slug**: Índice único para URLs amigables
- **url**: Índice único para URLs completas

## Métodos de Instancia

### generateSlug(text)
```javascript
// Genera un slug URL-friendly desde un texto
const slug = productType.generateSlug("Leche Entera La Serenísima"); // "leche-entera-la-serenisima"
```

### getUrl()
```javascript
// Retorna la URL completa para el tipo de producto
const url = productType.getUrl(); // "/productos/lacteos/leches/leche-entera"
```

### getProducts()
```javascript
// Obtiene todos los productos asociados con populate
const productTypeWithProducts = await productType.getProducts();
// Retorna el productType con el array 'products' populado
```

### syncProducts()
```javascript
// Sincroniza el array de productos buscando todos los productos que referencian este tipo
await productType.syncProducts(); // Actualiza this.products con los IDs actuales
```

## Métodos Estáticos

### findBySlug(slug)
```javascript
// Busca un tipo de producto por su slug
const productType = await ProductType.findBySlug("leche-entera");
```

### findByUrl(url)
```javascript
// Busca un tipo de producto por su URL completa
const productType = await ProductType.findByUrl("/productos/lacteos/leches/leche-entera");
```

## Middleware Automático

### Generación de Slug y URL
```javascript
// Se ejecuta automáticamente antes de guardar
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
```

## Ejemplo de Documento Completo

```json
{
  "_id": "507f1f77bcf86cd799439011",
  "name": "leche-entera",
  "slug": "leche-entera",
  "url": "/productos/lacteos/leches/leche-entera",
  "displayName": "Leche Entera",
  "description": "Leche de vaca entera pasteurizada",
  "category": "lacteos",
  "subcategory": "leches",
  "products": [
    "507f1f77bcf86cd799439012",
    "507f1f77bcf86cd799439013"
  ],
  "icon": "🥛",
  "color": "#FFC107",
  "priority": 1,
  "active": true,
  "featured": true,
  "filters": ["organico", "light", "sin_lactosa"],
  "metadata": {
    "productCount": 85,
    "lastUpdated": "2024-01-15T10:30:00.000Z",
    "averagePrice": 65.40,
    "priceRange": {
      "min": 45.00,
      "max": 120.00
    },
    "commonBrands": ["La Serenísima", "Sancor", "Veronica"],
    "averageWeight": 1.0,
    "commonUnits": ["lt", "ml"]
  },
  "createdAt": "2024-01-01T00:00:00.000Z",
  "updatedAt": "2024-01-15T10:30:00.000Z"
}
```

## Casos de Uso

### 1. Navegación por Jerarquía Completa
- **Tipos de una subcategoría**: `find({ subcategory: "leches", active: true }).sort({ priority: -1 })`
- **Tipos de una categoría**: `find({ category: "lacteos", active: true })`
- **Buscar tipo específico**: `findOne({ name: "leche-entera", active: true })`

### 2. Gestión de Tipos de Producto
- **Crear tipo**: `new ProductType({ _id: "leche-entera", name: "leche-entera", slug: "leche-entera", category: "lacteos", subcategory: "leches" })`
- **Actualizar filtros**: `findOneAndUpdate({ name: "leche-entera" }, { $push: { filters: "nueva_marca" } })`
- **Actualizar metadatos**: `findOneAndUpdate({ name: "leche-entera" }, { "metadata.productCount": 85 })`

### 3. Filtrado y Búsqueda Avanzada
- **Tipos con filtro específico**: `find({ filters: "organico", active: true })`
- **Tipos destacados**: `find({ featured: true, active: true })`
- **Análisis de precios**: `aggregate([{ $group: { _id: "$subcategory", avgPrice: { $avg: "$metadata.averagePrice" } } }])`

### 4. Mantenimiento y Actualización
- **Tipos sin productos**: `find({ "metadata.productCount": 0, active: true })`
- **Actualización de estadísticas**: `updateMany({ category: "lacteos" }, [{ $set: { "metadata.lastUpdated": new Date() } }])`
- **Reordenamiento**: `findOneAndUpdate({ name: "leche-entera" }, { priority: 2 })`

## Consideraciones de Integridad

### Validación de Jerarquía
- Verificar que categoría y subcategoría padre existen
- Mantener consistencia en actualizaciones de jerarquía
- Validar filtros existen en colección `filters`

### Rendimiento
- Consultas siempre incluyen filtros de categoría/subcategoría
- Cache de tipos activos por subcategoría
- Actualización batch de metadatos estadísticos

### Integración con Productos
- Sincronización automática de metadatos al agregar productos
- Validación de que productos usan tipos existentes y aplicables
- Actualización de estadísticas cuando cambian productos

## Fecha de Incorporación
27 de septiembre de 2025

## Feature Asociada
Hierarchical Product Organization - Sistema jerárquico de organización de productos.

## Commit Relacionado
[FEAT-006] Crear modelo ProductType para granularidad máxima de productos</content>
<parameter name="filePath">d:\dev\caminando-onlinev11\Library\archivos\ProductType.js.md