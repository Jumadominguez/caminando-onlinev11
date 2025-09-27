# Desglose de Archivo: Offer.js

## Propósito
Este archivo define el modelo de datos para ofertas y promociones en la plataforma de comparación de precios. Las ofertas permiten gestionar descuentos, promociones especiales y códigos de cupón con reglas flexibles de aplicación.

## Relaciones
- **Supermercados**: Referencia a la colección `supermarkets` como origen de la oferta
- **Productos**: Referencia a productos específicos a través de `applicableProducts`
- **Categorías**: Referencia a categorías aplicables a través de `applicableCategories`
- **API**: Expuesto a través de endpoints REST para gestión de ofertas y aplicación automática

## Recreación
1. Crear archivo en `src/backend/src/models/Offer.js`
2. Importar mongoose: `const mongoose = require('mongoose');`
3. Definir schema con campos de oferta, descuentos y restricciones
4. Agregar índices para optimización de consultas
5. Implementar middleware y métodos de instancia
6. Exportar modelo: `module.exports = mongoose.model('Offer', offerSchema);`

## Campos del Modelo

### Información Básica
| Campo | Tipo | Requerido | Descripción | Ejemplo |
|-------|------|-----------|-------------|---------|
| `_id` | String | Sí | ID personalizado único | `"carrefour-20-off-lacteos"` |
| `title` | String | Sí | Título de la oferta | `"20% OFF en Lácteos"` |
| `description` | String | No | Descripción detallada | `"Descuento del 20% en todos los productos lácteos"` |
| `type` | String | Sí | Tipo de oferta | `"percentage"` |

### Configuración del Descuento
| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `discount.percentage` | Number | Porcentaje de descuento | `20` |
| `discount.fixedAmount` | Number | Monto fijo de descuento | `50` |
| `discount.buyQuantity` | Number | Cantidad a comprar (2x1) | `2` |
| `discount.getQuantity` | Number | Cantidad gratis (2x1) | `1` |
| `discount.minimumPurchase` | Number | Compra mínima requerida | `100` |

### Alcance de Aplicación
| Campo | Tipo | Requerido | Descripción | Ejemplo |
|-------|------|-----------|-------------|---------|
| `supermarket` | String | Sí | ID del supermercado | `"carrefour"` |
| `applicableProducts` | Array | No | IDs de productos específicos | `["leche-entera-1l", "yogur-natural"]` |
| `applicableCategories` | Array | No | Categorías aplicables | `["lacteos", "panaderia"]` |
| `applicableSubcategories` | Array | No | Subcategorías aplicables | `["leches", "yogures"]` |
| `applicableProductTypes` | Array | No | Tipos de producto | `["leche-entera", "yogur-natural"]` |

### Vigencia Temporal
| Campo | Tipo | Requerido | Descripción | Ejemplo |
|-------|------|-----------|-------------|---------|
| `startDate` | Date | Sí | Fecha de inicio | `2024-01-15T00:00:00Z` |
| `endDate` | Date | Sí | Fecha de fin | `2024-01-31T23:59:59Z` |
| `isActive` | Boolean | No | Si está activa | `true` |

### Restricciones y Límites
| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `usageLimit` | Number | Límite total de usos | `1000` |
| `userLimit` | Number | Límite por usuario | `5` |
| `currentUsage` | Number | Usos actuales | `150` |
| `minimumQuantity` | Number | Cantidad mínima | `1` |

### Información de Presentación
| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `terms` | String | Términos y condiciones | `"Válido solo en sucursales..."` |
| `image` | String | Imagen promocional | `"https://carrefour.com/oferta.jpg"` |
| `badge` | String | Texto del badge | `"20% OFF"` |
| `badgeColor` | String | Color del badge | `"#FF5722"` |
| `priority` | Number | Prioridad de ordenamiento | `10` |

### Sistema de Cupones
| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `couponCode` | String | Código de cupón | `"LACTEOS20"` |
| `autoApply` | Boolean | Aplicación automática | `false` |

### Metadatos de Rendimiento
| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `metadata.totalSavings` | Number | Ahorro total generado | `15000.50` |
| `metadata.uniqueUsers` | Number | Usuarios únicos | `450` |
| `metadata.averageOrderValue` | Number | Valor promedio de órdenes | `285.75` |
| `metadata.conversionRate` | Number | Tasa de conversión | `0.15` |

### Timestamps
| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `createdAt` | Date | Fecha de creación | `2024-01-10T10:00:00Z` |
| `updatedAt` | Date | Fecha de actualización | `2024-01-15T14:30:00Z` |

## Tipos de Oferta

### 1. Percentage
- **Descripción**: Descuento porcentual
- **Campos**: `discount.percentage`
- **Ejemplo**: 20% OFF

### 2. Fixed
- **Descripción**: Descuento de monto fijo
- **Campos**: `discount.fixedAmount`
- **Ejemplo**: $50 OFF

### 3. Buy Get
- **Descripción**: Compra X y lleva Y (2x1, 3x2)
- **Campos**: `discount.buyQuantity`, `discount.getQuantity`
- **Ejemplo**: 2x1 en yogures

### 4. Free Shipping
- **Descripción**: Envío gratis
- **Campos**: `discount.minimumPurchase`
- **Ejemplo**: Envío gratis en compras mayores a $200

### 5. Bundle
- **Descripción**: Descuento en conjunto de productos
- **Campos**: `applicableProducts`, `discount.percentage`
- **Ejemplo**: 15% OFF comprando leche + pan

### 6. Flash Sale
- **Descripción**: Oferta por tiempo limitado
- **Campos**: Vigencia corta, `priority` alta
- **Ejemplo**: 50% OFF por 2 horas

## Índices de Base de Datos

```javascript
// Índices para optimización de consultas
offerSchema.index({ supermarket: 1, isActive: 1, endDate: -1 }); // Ofertas activas por supermercado
offerSchema.index({ type: 1, isActive: 1 }); // Ofertas por tipo
offerSchema.index({ applicableProducts: 1 }); // Búsqueda por productos aplicables
offerSchema.index({ startDate: 1, endDate: 1 }); // Consultas de vigencia
offerSchema.index({ couponCode: 1 }); // Búsqueda por código de cupón
```

## Métodos de Instancia

### isValid()
```javascript
// Verifica si la oferta está vigente y disponible
const isValid = offer.isValid(); // true/false
```

### appliesToProduct(productId, category, subcategory, productType)
```javascript
// Verifica si la oferta aplica a un producto específico
const applies = offer.appliesToProduct("leche-1l", "lacteos", "leches", "leche-entera"); // true/false
```

## Ejemplo de Documento Completo

```json
{
  "_id": "carrefour-20-off-lacteos",
  "title": "20% OFF en Lácteos",
  "description": "Descuento del 20% en todos los productos lácteos",
  "type": "percentage",
  "discount": {
    "percentage": 20
  },
  "supermarket": "carrefour",
  "applicableCategories": ["lacteos"],
  "startDate": "2024-01-15T00:00:00.000Z",
  "endDate": "2024-01-31T23:59:59.000Z",
  "isActive": true,
  "usageLimit": 1000,
  "userLimit": 5,
  "currentUsage": 150,
  "terms": "Válido solo en sucursales participantes",
  "badge": "20% OFF",
  "badgeColor": "#FF5722",
  "priority": 10,
  "metadata": {
    "totalSavings": 15000.50,
    "uniqueUsers": 450,
    "averageOrderValue": 285.75,
    "conversionRate": 0.15
  },
  "createdAt": "2024-01-10T10:00:00.000Z",
  "updatedAt": "2024-01-15T14:30:00.000Z"
}
```

## Casos de Uso

### 1. Gestión de Ofertas
- **Crear oferta**: `new Offer({ _id: "carrefour-20-off", title: "20% OFF", ... })`
- **Actualizar uso**: `findOneAndUpdate({ _id: "carrefour-20-off" }, { $inc: { currentUsage: 1 } })`
- **Desactivar oferta**: `findOneAndUpdate({ _id: "carrefour-20-off" }, { isActive: false })`

### 2. Aplicación de Ofertas
- **Ofertas activas de un supermercado**: `find({ supermarket: "carrefour", isActive: true, startDate: { $lte: new Date() }, endDate: { $gte: new Date() } })`
- **Ofertas aplicables a un producto**: `find({ $or: [{ applicableProducts: "leche-1l" }, { applicableCategories: "lacteos" }] })`
- **Verificar código de cupón**: `findOne({ couponCode: "LACTEOS20", isActive: true })`

### 3. Análisis y Reportes
- **Ofertas más utilizadas**: `find({ isActive: true }).sort({ currentUsage: -1 })`
- **Ahorro total generado**: `aggregate([{ $group: { _id: null, totalSavings: { $sum: "$metadata.totalSavings" } } }])`
- **Ofertas expiradas**: `find({ endDate: { $lt: new Date() }, isActive: true })`

### 4. Mantenimiento
- **Limpiar ofertas expiradas**: `updateMany({ endDate: { $lt: new Date() } }, { isActive: false })`
- **Reset de contadores mensuales**: `updateMany({}, { currentUsage: 0 })`

## Consideraciones de Integridad

### Validación de Reglas
- Verificar que fechas de inicio sean anteriores a fin
- Validar configuración de descuento según tipo
- Asegurar que supermercado existe
- Verificar límites de uso no excedidos

### Rendimiento
- Consultas de ofertas activas optimizadas con índices compuestos
- Cache de ofertas por supermercado
- Actualización diferida de metadatos de rendimiento

### Seguridad
- Validación de códigos de cupón
- Control de uso por usuario
- Auditoría de cambios en ofertas

## Fecha de Incorporación
27 de septiembre de 2025

## Feature Asociada
Promotional System - Sistema de ofertas y promociones para aumentar engagement.

## Commit Relacionado
[FEAT-007] Crear modelo Offer para gestión de promociones y descuentos</content>
<parameter name="filePath">d:\dev\caminando-onlinev11\Library\archivos\Offer.js.md