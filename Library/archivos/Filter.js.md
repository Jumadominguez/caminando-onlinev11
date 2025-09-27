# Desglose de Archivo: Filter.js

## Propósito
Este archivo define el modelo de datos para filtros aplicables a productos en la plataforma de comparación de precios. El modelo permite gestionar un catálogo centralizado de filtros, categorizarlos y definir sus características para una experiencia de filtrado avanzada.

## Relaciones
- **Productos**: Referenciado por el campo `filters` en la colección `products`
- **Categorías**: Referenciado por el campo `applicableCategories` para determinar dónde aplicar filtros
- **API**: Expuesto a través de endpoints REST para gestión de filtros y aplicación en búsquedas

## Recreación
1. Crear archivo en `src/backend/src/models/Filter.js`
2. Importar mongoose: `const mongoose = require('mongoose');`
3. Definir schema con campos de filtro y validaciones
4. Agregar índices para optimización de consultas
5. Implementar middleware para timestamps automáticos
6. Exportar modelo: `module.exports = mongoose.model('Filter', filterSchema);`

## Campos del Modelo

### Información Básica
| Campo | Tipo | Requerido | Descripción | Ejemplo |
|-------|------|-----------|-------------|---------|
| `name` | String | Sí | Nombre interno del filtro (único) | `"organico"` |
| `displayName` | String | Sí | Nombre para mostrar al usuario | `"Producto Orgánico"` |
| `category` | String | Sí | Categoría del filtro | `"caracteristicas"` |
| `type` | String | No | Tipo de filtro | `"multiselect"` |

### Configuración del Filtro
| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `values` | Array | Valores posibles para select/multiselect | `["sí", "no"]` |
| `minValue` | Number | Valor mínimo para rangos | `0` |
| `maxValue` | Number | Valor máximo para rangos | `100` |
| `unit` | String | Unidad para rangos | `"kg"` |

### Información de Presentación
| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `description` | String | Descripción detallada | `"Productos certificados orgánicos"` |
| `icon` | String | Icono o emoji | `"🌱"` |
| `color` | String | Color para UI | `"#4CAF50"` |
| `priority` | Number | Prioridad de ordenamiento | `10` |

### Estado y Aplicabilidad
| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `active` | Boolean | Si el filtro está activo | `true` |
| `applicableCategories` | Array | Categorías donde aplica | `["Lácteos", "Frutas"]` |

### Timestamps
| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `createdAt` | Date | Fecha de creación | `2024-01-01T00:00:00Z` |
| `updatedAt` | Date | Fecha de última actualización | `2024-01-15T10:30:00Z` |

## Tipos de Filtros

### 1. Select
- **Descripción**: Selección única de un valor
- **Ejemplo**: Tipo de leche (entera, descremada, semi-descremada)
- **Configuración**: `type: "select"`, `values: ["entera", "descremada", "semi"]`

### 2. Multiselect
- **Descripción**: Selección múltiple de valores
- **Ejemplo**: Características del producto (orgánico, sin TACC, light)
- **Configuración**: `type: "multiselect"`, `values: ["organico", "sin_tacc", "light"]`

### 3. Range
- **Descripción**: Rango numérico con valores mínimo/máximo
- **Ejemplo**: Precio por kilo ($50 - $200)
- **Configuración**: `type: "range"`, `minValue: 50`, `maxValue: 200`, `unit: "$"`

### 4. Boolean
- **Descripción**: Filtro verdadero/falso
- **Ejemplo**: Producto en oferta (sí/no)
- **Configuración**: `type: "boolean"`

## Categorías de Filtros

### Características del Producto
- `caracteristicas`: Orgánico, sin TACC, light, etc.
- `origen`: Nacional, importado, regional
- `marca`: Por marca específica

### Información Nutricional
- `nutricion`: Bajo en sodio, alto en fibra, etc.
- `alergenos`: Sin gluten, sin lactosa, etc.

### Información Comercial
- `ofertas`: En oferta, con descuento
- `disponibilidad`: En stock, disponible para delivery

### Información Técnica
- `empaque`: Por tamaño, formato
- `conservacion`: Refrigerado, ambiente, congelado

## Índices de Base de Datos

```javascript
// Índices para optimización de consultas
filterSchema.index({ category: 1, active: 1 }); // Filtros por categoría y estado
filterSchema.index({ name: 1 }); // Búsqueda por nombre único
filterSchema.index({ applicableCategories: 1 }); // Filtros aplicables a categorías
filterSchema.index({ priority: -1 }); // Ordenamiento por prioridad
```

## Ejemplo de Documento Completo

```json
{
  "name": "organico",
  "displayName": "Producto Orgánico",
  "category": "caracteristicas",
  "type": "boolean",
  "description": "Productos certificados como orgánicos",
  "icon": "🌱",
  "color": "#4CAF50",
  "priority": 10,
  "active": true,
  "applicableCategories": ["Frutas", "Verduras", "Lácteos"],
  "createdAt": "2024-01-01T00:00:00.000Z",
  "updatedAt": "2024-01-15T10:30:00.000Z"
}
```

## Casos de Uso

### 1. Gestión de Filtros
- **Crear filtro**: `new Filter({ name: "organico", displayName: "Producto Orgánico", ... })`
- **Actualizar filtro**: `findOneAndUpdate({ name: "organico" }, { priority: 15 })`
- **Desactivar filtro**: `findOneAndUpdate({ name: "organico" }, { active: false })`

### 2. Consultas de Filtrado
- **Filtros activos por categoría**: `find({ active: true, applicableCategories: "Lácteos" })`
- **Filtros por tipo**: `find({ type: "multiselect" })`
- **Filtros ordenados por prioridad**: `find({ active: true }).sort({ priority: -1 })`

### 3. Aplicación en Productos
- **Productos con filtro específico**: `find({ filters: "organico" })`
- **Productos con múltiples filtros**: `find({ filters: { $in: ["organico", "sin_lactosa"] } })`

### 4. Mantenimiento
- **Filtros obsoletos**: `find({ updatedAt: { $lt: new Date(Date.now() - 365*24*60*60*1000) } })`
- **Filtros por categoría**: `distinct("category")`

## Consideraciones de Implementación

### Validaciones
- Nombres únicos para evitar conflictos
- Categorías predefinidas para consistencia
- Validación de rangos para filtros de tipo "range"

### Rendimiento
- Índices estratégicos para consultas frecuentes
- Cache de filtros activos para UI
- Paginación en listados grandes

### Integración con Productos
- Sincronización entre colección `filters` y campo `filters` en `products`
- Validación de que productos solo usen filtros existentes y aplicables
- Actualización automática de productos cuando se modifica un filtro

## Fecha de Incorporación
27 de septiembre de 2025

## Feature Asociada
Advanced Filtering System - Sistema de filtros avanzados para productos con gestión centralizada.

## Commit Relacionado
[FEAT-003] Crear modelo Filter para gestión centralizada de filtros</content>
<parameter name="filePath">d:\dev\caminando-onlinev11\Library\archivos\Filter.js.md