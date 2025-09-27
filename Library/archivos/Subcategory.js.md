# Desglose de Archivo: Subcategory.js

## Propósito
Este archivo define el modelo de datos para subcategorías de productos en la plataforma de comparación de precios. Las subcategorías representan el segundo nivel de organización jerárquica, perteneciendo a categorías principales.

## Relaciones
- **Categorías**: Referencia a la colección `categories` como categoría padre
- **Tipos de Producto**: Referenciado por la colección `producttypes` como subcategoría padre
- **Productos**: Referenciado por el campo `subcategory` en la colección `products`
- **API**: Expuesto a través de endpoints REST para navegación jerárquica

## Recreación
1. Crear archivo en `src/backend/src/models/Subcategory.js`
2. Importar mongoose: `const mongoose = require('mongoose');`
3. Definir schema con campos de subcategoría y referencias
4. Agregar índices para optimización de consultas
5. Implementar middleware para timestamps automáticos
6. Exportar modelo: `module.exports = mongoose.model('Subcategory', subcategorySchema);`

## Campos del Modelo

### Información Básica
| Campo | Tipo | Requerido | Descripción | Ejemplo |
|-------|------|-----------|-------------|---------|
| `_id` | ObjectId | Automático | ID único generado por MongoDB | `507f1f77bcf86cd799439011` |
| `name` | String | Sí | Nombre interno | `"leches"` |
| `slug` | String | Sí | Slug para URLs amigables | `"leches"` |
| `url` | String | Auto | URL completa generada | `"/productos/lacteos/leches"` |
| `displayName` | String | No | Nombre para mostrar | `"Leches"` |
| `description` | String | No | Descripción de la subcategoría | `"Variedad de leches y derivados lácteos"` |

### Relaciones Jerárquicas
| Campo | Tipo | Requerido | Descripción | Ejemplo |
|-------|------|-----------|-------------|---------|
| `category` | String | Sí | ID de la categoría padre | `"lacteos"` |

### Información de Presentación
| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `icon` | String | Icono o emoji | `"🥛"` |
| `color` | String | Color para UI | `"#4CAF50"` |
| `image` | String | Imagen de la subcategoría | `"https://example.com/leches.jpg"` |

### Configuración y Estado
| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `priority` | Number | Orden dentro de la categoría | `5` |
| `active` | Boolean | Si está activa | `true` |
| `featured` | Boolean | Si es subcategoría destacada | `false` |

### Metadatos Estadísticos
| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `metadata.productCount` | Number | Cantidad total de productos | `450` |
| `metadata.productTypeCount` | Number | Cantidad de tipos de producto | `12` |
| `metadata.lastUpdated` | Date | Última actualización | `2024-01-15T10:30:00Z` |
| `metadata.averagePrice` | Number | Precio promedio | `75.30` |
| `metadata.priceRange.min` | Number | Precio mínimo | `25.00` |
| `metadata.priceRange.max` | Number | Precio máximo | `180.00` |

### Timestamps
| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `createdAt` | Date | Fecha de creación | `2024-01-01T00:00:00Z` |
| `updatedAt` | Date | Fecha de actualización | `2024-01-15T10:30:00Z` |

## Índices de Base de Datos

```javascript
// Índices para optimización de consultas
subcategorySchema.index({ category: 1, active: 1, priority: -1 }); // Subcategorías por categoría, ordenadas
subcategorySchema.index({ name: 1 }); // Búsqueda por nombre
subcategorySchema.index({ slug: 1 }); // Índice único para slugs
subcategorySchema.index({ url: 1 }); // Índice único para URLs
subcategorySchema.index({ active: 1 }); // Subcategorías activas
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
const slug = subcategory.generateSlug("Leches y Derivados"); // "leches-y-derivados"
```

### getUrl()
```javascript
// Retorna la URL completa para la subcategoría
const url = subcategory.getUrl(); // "/productos/lacteos/leches"
```

## Métodos Estáticos

### findBySlug(slug)
```javascript
// Busca una subcategoría por su slug
const subcategory = await Subcategory.findBySlug("leches");
```

### findByUrl(url)
```javascript
// Busca una subcategoría por su URL completa
const subcategory = await Subcategory.findByUrl("/productos/lacteos/leches");
```

## Middleware Automático

### Generación de Slug y URL
```javascript
// Se ejecuta automáticamente antes de guardar
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
```

## Ejemplo de Documento Completo

```json
{
  "_id": "507f1f77bcf86cd799439011",
  "name": "leches",
  "slug": "leches",
  "url": "/productos/lacteos/leches",
  "displayName": "Leches",
  "description": "Variedad de leches pasteurizadas y especializadas",
  "category": "lacteos",
  "icon": "🥛",
  "color": "#4CAF50",
  "image": "https://example.com/leches.jpg",
  "priority": 5,
  "active": true,
  "featured": false,
  "metadata": {
    "productCount": 450,
    "productTypeCount": 12,
    "lastUpdated": "2024-01-15T10:30:00.000Z",
    "averagePrice": 75.30,
    "priceRange": {
      "min": 25.00,
      "max": 180.00
    }
  },
  "createdAt": "2024-01-01T00:00:00.000Z",
  "updatedAt": "2024-01-15T10:30:00.000Z"
}
```

## Casos de Uso

### 1. Navegación Jerárquica
- **Subcategorías de una categoría**: `find({ category: "lacteos", active: true }).sort({ priority: -1 })`
- **Buscar subcategoría específica**: `findOne({ name: "leches", active: true })`

### 2. Gestión de Subcategorías
- **Crear subcategoría**: `new Subcategory({ name: "leches", category: "lacteos" })`
- **Actualizar metadatos**: `findOneAndUpdate({ name: "leches" }, { "metadata.productCount": 450 })`
- **Reordenar prioridades**: `findOneAndUpdate({ name: "leches" }, { priority: 3 })`

### 3. Análisis por Subcategoría
- **Subcategorías más populares**: `find({ active: true }).sort({ "metadata.productCount": -1 })`
- **Precios por subcategoría**: `aggregate([{ $group: { _id: "$category", avgPrice: { $avg: "$metadata.averagePrice" } } }])`

### 4. Mantenimiento
- **Subcategorías sin productos**: `find({ "metadata.productCount": 0, active: true })`
- **Actualización masiva de metadatos**: `updateMany({}, [{ $set: { "metadata.lastUpdated": new Date() } }])`

## Consideraciones de Integridad

### Validación de Relaciones
- Verificar que la categoría padre existe antes de crear subcategoría
- Mantener consistencia en actualizaciones de metadatos
- Validar jerarquía antes de operaciones de eliminación

### Rendimiento
- Consultas siempre filtradas por categoría para optimización
- Cache de subcategorías activas por categoría
- Actualización diferida de metadatos estadísticos

## Fecha de Incorporación
27 de septiembre de 2025

## Feature Asociada
Hierarchical Product Organization - Sistema jerárquico de organización de productos.

## Commit Relacionado
[FEAT-005] Crear modelo Subcategory para jerarquía de productos</content>
<parameter name="filePath">d:\dev\caminando-onlinev11\Library\archivos\Subcategory.js.md