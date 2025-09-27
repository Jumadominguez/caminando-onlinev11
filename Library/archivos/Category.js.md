# Desglose de Archivo: Category.js

## Propósito
Este archivo define el modelo de datos para categorías principales de productos en la plataforma de comparación de precios. Las categorías sirven como la primera nivel de organización jerárquica de productos.

## Relaciones
- **Subcategorías**: Referenciado por la colección `subcategories` como categoría padre
- **Tipos de Producto**: Referenciado indirectamente a través de subcategorías
- **Productos**: Referenciado por el campo `category` en la colección `products`
- **API**: Expuesto a través de endpoints REST para navegación y gestión de categorías

## Recreación
1. Crear archivo en `src/backend/src/models/Category.js`
2. Importar mongoose: `const mongoose = require('mongoose');`
3. Definir schema con campos de categoría y metadatos
4. Agregar índices para optimización de consultas
5. Implementar middleware para timestamps automáticos
6. Exportar modelo: `module.exports = mongoose.model('Category', categorySchema);`

## Campos del Modelo

### Información Básica
| Campo | Tipo | Requerido | Descripción | Ejemplo |
|-------|------|-----------|-------------|---------|
| `_id` | String | Sí | ID personalizado único | `"lacteos"` |
| `name` | String | Sí | Nombre interno único | `"lacteos"` |
| `displayName` | String | No | Nombre para mostrar | `"Lácteos"` |
| `description` | String | No | Descripción de la categoría | `"Productos lácteos y derivados"` |

### Información de Presentación
| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `icon` | String | Icono o emoji | `"🥛"` |
| `color` | String | Color para UI | `"#2196F3"` |
| `image` | String | Imagen de la categoría | `"https://example.com/lacteos.jpg"` |

### Configuración y Estado
| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `priority` | Number | Orden de prioridad | `10` |
| `active` | Boolean | Si está activa | `true` |
| `featured` | Boolean | Si es categoría destacada | `true` |

### Jerarquía (Opcional)
| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `parentCategory` | ObjectId | Categoría padre para jerarquías | `ObjectId(...)` |

### Metadatos Estadísticos
| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `metadata.productCount` | Number | Cantidad total de productos | `1250` |
| `metadata.subcategoryCount` | Number | Cantidad de subcategorías | `8` |
| `metadata.lastUpdated` | Date | Última actualización | `2024-01-15T10:30:00Z` |
| `metadata.averagePrice` | Number | Precio promedio | `85.50` |
| `metadata.priceRange.min` | Number | Precio mínimo | `15.00` |
| `metadata.priceRange.max` | Number | Precio máximo | `250.00` |

### Timestamps
| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `createdAt` | Date | Fecha de creación | `2024-01-01T00:00:00Z` |
| `updatedAt` | Date | Fecha de actualización | `2024-01-15T10:30:00Z` |

## Índices de Base de Datos

```javascript
// Índices para optimización de consultas
categorySchema.index({ active: 1, priority: -1 }); // Categorías activas ordenadas por prioridad
categorySchema.index({ name: 1 }); // Búsqueda por nombre único
categorySchema.index({ featured: 1 }); // Categorías destacadas
```

## Ejemplo de Documento Completo

```json
{
  "_id": "lacteos",
  "name": "lacteos",
  "displayName": "Lácteos",
  "description": "Productos lácteos y derivados",
  "icon": "🥛",
  "color": "#2196F3",
  "image": "https://example.com/lacteos.jpg",
  "priority": 10,
  "active": true,
  "featured": true,
  "metadata": {
    "productCount": 1250,
    "subcategoryCount": 8,
    "lastUpdated": "2024-01-15T10:30:00.000Z",
    "averagePrice": 85.50,
    "priceRange": {
      "min": 15.00,
      "max": 250.00
    }
  },
  "createdAt": "2024-01-01T00:00:00.000Z",
  "updatedAt": "2024-01-15T10:30:00.000Z"
}
```

## Casos de Uso

### 1. Navegación por Categorías
- **Categorías activas ordenadas**: `find({ active: true }).sort({ priority: -1 })`
- **Categorías destacadas**: `find({ featured: true, active: true })`
- **Buscar por nombre**: `findOne({ name: "lacteos" })`

### 2. Gestión de Categorías
- **Crear categoría**: `new Category({ _id: "lacteos", name: "lacteos", displayName: "Lácteos" })`
- **Actualizar metadatos**: `findOneAndUpdate({ name: "lacteos" }, { "metadata.productCount": 1250 })`
- **Desactivar categoría**: `findOneAndUpdate({ name: "lacteos" }, { active: false })`

### 3. Análisis y Reportes
- **Categorías con más productos**: `find({ active: true }).sort({ "metadata.productCount": -1 })`
- **Rango de precios por categoría**: `find({}, { "metadata.priceRange": 1 })`

## Fecha de Incorporación
27 de septiembre de 2025

## Feature Asociada
Hierarchical Product Organization - Sistema jerárquico de organización de productos.

## Commit Relacionado
[FEAT-004] Expandir modelo Category con metadatos y jerarquía</content>
<parameter name="filePath">d:\dev\caminando-onlinev11\Library\archivos\Category.js.md