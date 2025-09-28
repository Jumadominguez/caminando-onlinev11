# Arquitectura de Base de Datos - Caminando Online V4

## Información General

**Proyect## 👤 Colección: users **[Base: admin]**

**Propósito## 📂 Colección: categories **[Base: caminando_online_db]**

**Propósito**: Categorías principales de productos (primer nivel jerárquico). Gestiona usuarios registrados ## 🛍️ Colección: orders **[Base: operations_db]**

**Propósito**: Gestión completa de pedidos realizados por usuarios, incluyendo estado, productos, pagos y envíos.la plataforma Caminando Online, incluyendo autenticación, preferencias y datos de compras.: Caminando Online - Plataforma de Comparación de Precios
**Base de Datos**: MongoDB
**Arquitectura**: Multi-database (8 bases de datos separadas)
**Framework ODM**: Mongoose v8.x
**Fecha**: Septiembre 2025

## 📊 Visión General de la Arquitectura

La arquitectura de base de datos está diseñada con **8 bases de datos separadas** siguiendo una estrategia de separación por propósito y origen de datos. Combina bases de datos raw (datos crudos de scraping) con bases procesadas (datos normalizados para el frontend).

### 🗄️ Estructura Multi-Database

#### **Bases de Administración y Operaciones:**

#### 1. **`admin`** - Base de Datos de Administración
**Propósito**: Gestión de usuarios, autenticación y sesiones
**Conexión**: `mongodb://localhost:27017/admin`
```
admin
├── users (Usuarios registrados de la plataforma)
├── user_addresses (Direcciones de entrega)
├── user_sessions (Sesiones activas de autenticación)
└── carts (Carritos de compra de usuarios)
```

#### 2. **`operations_db`** - Base de Datos Operativa
**Propósito**: Datos transaccionales, logs y configuración del sistema
**Conexión**: `mongodb://localhost:27017/operations_db`
```
operations_db
├── orders (Pedidos de usuarios)
├── price_history (Historial de precios)
├── notifications (Notificaciones del sistema)
├── api_logs (Logs de llamadas a APIs externas)
└── system_settings (Configuraciones del sistema)
```

#### **Base Procesada (Frontend):**

#### 3. **`caminando_online_db`** - Base de Datos Procesada
**Propósito**: Datos normalizados y combinados para el frontend
**Conexión**: `mongodb://localhost:27017/caminando_online_db`
**Características**: Datos unificados de todos los supermercados, categorías normalizadas
```
caminando_online_db
├── supermarkets (Homepage data de supermercados)
├── categories (Categorías principales normalizadas)
├── subcategories (Subcategorías normalizadas)
├── producttypes (Tipos específicos de producto normalizados)
├── products (Productos individuales unificados)
├── filters (Sistema de filtros)
└── offers (Ofertas y promociones)
```

#### **Bases Raw (Scraping por Supermercado):**

#### 4. **`carrefour`** - Datos Raw Carrefour
**Propósito**: Datos crudos extraídos del sitio web de Carrefour
**Conexión**: `mongodb://localhost:27017/carrefour`
```
carrefour
├── supermarket (Metadata del sitio)
├── categories (Categorías como aparecen en Carrefour)
├── subcategories (Subcategorías originales)
├── producttypes (Tipos de producto sin normalizar)
├── products (Productos con estructura original)
├── offers (Ofertas específicas de Carrefour)
└── filters (Filtros del sitio)
```

#### 5. **`dia`** - Datos Raw Dia
**Propósito**: Datos crudos extraídos del sitio web de Dia
**Conexión**: `mongodb://localhost:27017/dia`
```
dia
├── supermarket (Metadata del sitio)
├── categories (Categorías como aparecen en Dia)
├── subcategories (Subcategorías originales)
├── producttypes (Tipos de producto sin normalizar)
├── products (Productos con estructura original)
├── offers (Ofertas específicas de Dia)
└── filters (Filtros del sitio)
```

#### 6. **`jumbo`** - Datos Raw Jumbo
**Propósito**: Datos crudos extraídos del sitio web de Jumbo
**Conexión**: `mongodb://localhost:27017/jumbo`
```
jumbo
├── supermarket (Metadata del sitio)
├── categories (Categorías como aparecen en Jumbo)
├── subcategories (Subcategorías originales)
├── producttypes (Tipos de producto sin normalizar)
├── products (Productos con estructura original)
├── offers (Ofertas específicas de Jumbo)
└── filters (Filtros del sitio)
```

#### 7. **`vea`** - Datos Raw Vea
**Propósito**: Datos crudos extraídos del sitio web de Vea
**Conexión**: `mongodb://localhost:27017/vea`
```
vea
├── supermarket (Metadata del sitio)
├── categories (Categorías como aparecen en Vea)
├── subcategories (Subcategorías originales)
├── producttypes (Tipos de producto sin normalizar)
├── products (Productos con estructura original)
├── offers (Ofertas específicas de Vea)
└── filters (Filtros del sitio)
```

#### 8. **`disco`** - Datos Raw Disco
**Propósito**: Datos crudos extraídos del sitio web de Disco
**Conexión**: `mongodb://localhost:27017/disco`
```
disco
├── supermarket (Metadata del sitio)
├── categories (Categorías como aparecen en Disco)
├── subcategories (Subcategorías originales)
├── producttypes (Tipos de producto sin normalizar)
├── products (Productos con estructura original)
├── offers (Ofertas específicas de Disco)
└── filters (Filtros del sitio)
```

## 💡 Ventajas de la Arquitectura Multi-Database

### Separación por Propósito y Origen
- **`admin`**: Datos críticos de usuarios (alta seguridad, backup frecuente)
- **`operations_db`**: Datos operativos (logs, transacciones, configuración)
- **`caminando_online_db`**: Datos procesados/normalizados para frontend
- **`carrefour/dia/jumbo/vea/disco`**: Datos raw por supermercado (aislamiento de scraping)

### Beneficios Técnicos
- **Escalabilidad**: Cada supermercado puede procesarse independientemente
- **Mantenimiento**: Cambios en un sitio no afectan otros
- **Flexibilidad**: Fácil agregar nuevos supermercados
- **Consistencia**: Frontend siempre ve datos unificados
- **Debugging**: Comparación fácil entre datos raw y procesados

### Estrategias de Backup
- **`admin`**: Backup diario completo (datos críticos)
- **`operations_db`**: Backup semanal con retención limitada
- **`caminando_online_db`**: Backup semanal (datos maestros)
- **Bases raw**: Backup opcional o regeneración desde scraping

### Flujo de Procesamiento de Datos
1. **Scraping** → Datos raw en bases individuales por supermercado
2. **ETL/Normalización** → Combinar y limpiar datos
3. **Almacenamiento** → Datos unificados en `caminando_online_db`
4. **Frontend** → Consume datos consistentes y normalizados

## 🏪 Colección: supermarkets **[Base: caminando_online_db]**

**Propósito**: Almacena datos extraídos de las páginas principales de supermercados para scraping y metadata.

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `_id` | String | Sí | ID personalizado único (ej: "carrefour") |
| `name` | String | Sí | Nombre del supermercado |
| `baseUrl` | String | Sí | URL base para scraping |
| `logo` | String | No | URL del logo |
| `country` | String | No | País de operación |
| `currency` | String | No | Moneda utilizada |
| `active` | Boolean | No | Si está activo para scraping |
| `lastScraped` | Date | No | Última vez que se scrapeo |
| `scrapeConfig` | Object | No | Configuración específica de scraping |

**Índices**:
- `{ active: 1 }`
- `{ name: 1 }`

## � Colección: users

**Propósito**: Gestiona usuarios registrados de la plataforma Caminando Online, incluyendo autenticación, preferencias y datos de compras.

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `email` | String | Sí | Email único del usuario (lowercase) |
| `username` | String | Sí | Nombre de usuario único (3-30 caracteres) |
| `firstName` | String | Sí | Nombre del usuario |
| `lastName` | String | Sí | Apellido del usuario |
| `password` | String | Sí | Hash de contraseña (bcrypt) |
| `isEmailVerified` | Boolean | No | Si el email está verificado |
| `emailVerificationToken` | String | No | Token para verificación de email |
| `emailVerificationExpires` | Date | No | Expiración del token de verificación |
| `passwordResetToken` | String | No | Token para reset de contraseña |
| `passwordResetExpires` | Date | No | Expiración del token de reset |
| `isActive` | Boolean | No | Si la cuenta está activa |
| `role` | String | No | Rol del usuario (user, premium, admin) |
| `lastLogin` | Date | No | Último login del usuario |
| `loginCount` | Number | No | Número total de logins |
| `avatar` | String | No | URL del avatar del usuario |
| `phone` | String | No | Número de teléfono |
| `dateOfBirth` | Date | No | Fecha de nacimiento |
| `gender` | String | No | Género del usuario |
| `preferences.currency` | String | No | Moneda preferida (default: ARS) |
| `preferences.language` | String | No | Idioma preferido (default: es-AR) |
| `preferences.notifications` | Object | No | Configuración de notificaciones |
| `preferences.supermarkets` | Array | No | Supermercados favoritos del usuario |
| `favorites` | Array | No | Productos favoritos del usuario |
| `shoppingLists` | Array | No | Listas de compras del usuario |
| `searchHistory` | Array | No | Historial de búsquedas |
| `stats` | Object | No | Estadísticas del usuario |
| `location` | Object | No | Información de ubicación |

**Índices**:
- `{ email: 1 }` (único)
- `{ username: 1 }` (único)
- `{ "preferences.supermarkets.supermarketId": 1 }`
- `{ "favorites.productId": 1 }`
- `{ role: 1, isActive: 1 }`
- `{ createdAt: -1 }`

**Métodos del Modelo**:
- `comparePassword(candidatePassword)`: Verifica contraseña
- `hashPassword()`: Genera hash de contraseña
- `updateLastActivity()`: Actualiza última actividad
- `addToFavorites(productId)`: Agrega producto a favoritos
- `removeFromFavorites(productId)`: Remueve producto de favoritos
- `isFavorite(productId)`: Verifica si producto está en favoritos

**Métodos Estáticos**:
- `findByEmailOrUsername(identifier)`: Busca usuario por email o username

## �📂 Colección: categories

**Propósito**: Categorías principales de productos (primer nivel jerárquico).

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `_id` | String | Sí | ID personalizado único |
| `name` | String | Sí | Nombre interno único |
| `displayName` | String | No | Nombre para mostrar |
| `description` | String | No | Descripción de la categoría |
| `icon` | String | No | Icono o emoji |
| `color` | String | No | Color para UI |
| `image` | String | No | Imagen de la categoría |
| `subcategories` | Array[ObjectId] | No | Referencias a subcategorías hijas |
| `priority` | Number | No | Orden de prioridad |
| `active` | Boolean | No | Si está activa |
| `featured` | Boolean | No | Si es categoría destacada |
| `parentCategory` | ObjectId | No | Categoría padre (jerarquías) |
| `metadata` | Object | No | Estadísticas y metadatos |

**Índices**:
- `{ active: 1, priority: -1 }`
- `{ name: 1 }`
- `{ featured: 1 }`
- `{ subcategories: 1 }`

## 📁 Colección: subcategories **[Base: caminando_online_db]**

**Propósito**: Subcategorías de productos (segundo nivel jerárquico).

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `_id` | ObjectId | Auto | ID generado por MongoDB |
| `name` | String | Sí | Nombre interno |
| `slug` | String | Sí | Slug para URLs amigables |
| `url` | String | Auto | URL completa generada |
| `displayName` | String | No | Nombre para mostrar |
| `description` | String | No | Descripción de la subcategoría |
| `category` | String | Sí | Referencia a categoría padre |
| `priority` | Number | No | Orden dentro de la categoría |
| `active` | Boolean | No | Si está activa |
| `featured` | Boolean | No | Si es subcategoría destacada |
| `metadata` | Object | No | Estadísticas y metadatos |

**Índices**:
- `{ category: 1, active: 1, priority: -1 }`
- `{ name: 1 }`
- `{ slug: 1 }`
- `{ url: 1 }`
- `{ active: 1 }`

## 🏷️ Colección: producttypes **[Base: caminando_online_db]**

**Propósito**: Tipos específicos de productos (tercer nivel jerárquico, granularidad máxima).

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `_id` | ObjectId | Auto | ID generado por MongoDB |
| `name` | String | Sí | Nombre interno |
| `slug` | String | Sí | Slug para URLs amigables |
| `url` | String | Auto | URL completa generada |
| `displayName` | String | No | Nombre para mostrar |
| `description` | String | No | Descripción del tipo |
| `category` | String | Sí | Referencia a categoría padre |
| `subcategory` | String | Sí | Referencia a subcategoría padre |
| `products` | Array[ObjectId] | No | Productos que pertenecen a este tipo |
| `priority` | Number | No | Orden dentro de la subcategoría |
| `active` | Boolean | No | Si está activo |
| `featured` | Boolean | No | Si es tipo destacado |
| `filters` | Array[String] | No | Filtros aplicables |
| `metadata` | Object | No | Estadísticas y metadatos |

**Índices**:
- `{ category: 1, subcategory: 1, active: 1, priority: -1 }`
- `{ name: 1 }`
- `{ slug: 1 }`
- `{ url: 1 }`
- `{ active: 1 }`
- `{ filters: 1 }`
- `{ products: 1 }`

## 🛒 Colección: products **[Base: caminando_online_db]**

**Propósito**: Productos individuales con información de precios y características.

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `_id` | ObjectId | Auto | ID generado por MongoDB |
| `name` | String | Sí | Nombre del producto |
| `description` | String | No | Descripción detallada |
| `supermarket` | String | Sí | Referencia al supermercado |
| `category` | String | Sí | Referencia a categoría |
| `subcategory` | String | Sí | Referencia a subcategoría |
| `productType` | String | Sí | Referencia al tipo de producto |
| `ean` | String | No | Código EAN-13 |
| `sku` | String | No | SKU del producto |
| `brand` | String | No | Marca del producto |
| `price` | Number | Sí | Precio actual |
| `listPrice` | Number | No | Precio de lista (antes de descuento) |
| `discount` | Number | No | Porcentaje de descuento |
| `offers` | Array[ObjectId] | No | Ofertas aplicables al producto |
| `filters` | Array[String] | No | Filtros que aplica el producto |
| `weight` | Number | No | Peso en gramos |
| `pricePerKilo` | Number | No | Precio por kilo |
| `quantity` | Number | No | Cantidad en stock |
| `pricePerLitre` | Number | No | Precio por litro |
| `image` | String | No | URL de imagen del producto |
| `active` | Boolean | No | Si está disponible |
| `lastUpdated` | Date | Auto | Última actualización |

**Índices**:
- `{ supermarket: 1, category: 1, subcategory: 1, productType: 1 }`
- `{ ean: 1 }` (único, sparse)
- `{ sku: 1 }` (único, sparse)
- `{ price: 1 }`
- `{ active: 1 }`
- `{ filters: 1 }`

## 🔍 Colección: filters **[Base: caminando_online_db]**

**Propósito**: Sistema centralizado de filtros para búsqueda y categorización avanzada.

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `_id` | String | Sí | ID personalizado único |
| `name` | String | Sí | Nombre interno único |
| `displayName` | String | Sí | Nombre para mostrar |
| `type` | String | Sí | Tipo de filtro (select, checkbox, range) |
| `category` | String | No | Categoría a la que aplica |
| `values` | Array | No | Valores posibles (para select) |
| `min` | Number | No | Valor mínimo (para range) |
| `max` | Number | No | Valor máximo (para range) |
| `unit` | String | No | Unidad de medida |
| `priority` | Number | No | Orden de aparición |
| `active` | Boolean | No | Si está activo |

**Índices**:
- `{ category: 1, active: 1, priority: -1 }`
- `{ name: 1 }`
- `{ type: 1 }`
- `{ active: 1 }`

## 🎯 Colección: offers **[Base: caminando_online_db]**

**Propósito**: Gestión de ofertas y promociones aplicables a productos.

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `_id` | String | Sí | ID personalizado único |
| `name` | String | Sí | Nombre de la oferta |
| `description` | String | No | Descripción detallada |
| `type` | String | Sí | Tipo (percentage, fixed, buy_get) |
| `value` | Number | Sí | Valor del descuento |
| `conditions` | Object | No | Condiciones de aplicación |
| `supermarkets` | Array[String] | No | Supermercados donde aplica |
| `categories` | Array[String] | No | Categorías donde aplica |
| `products` | Array[ObjectId] | No | Productos específicos |
| `startDate` | Date | No | Fecha de inicio |
| `endDate` | Date | No | Fecha de fin |
| `active` | Boolean | No | Si está activa |
| `priority` | Number | No | Prioridad de aplicación |

**Índices**:
- `{ active: 1, startDate: 1, endDate: 1 }`
- `{ type: 1 }`
- `{ supermarkets: 1 }`
- `{ categories: 1 }`
- `{ products: 1 }`

## � Colección: orders

**Propósito**: Gestión completa de pedidos realizados por usuarios, incluyendo estado, productos, pagos y envíos.

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `userId` | ObjectId | Sí | Referencia al usuario |
| `orderNumber` | String | Sí | Número único del pedido |
| `status` | String | No | Estado (pending, confirmed, shipped, delivered) |
| `items` | Array | Sí | Items del pedido con cantidades y precios |
| `subtotal` | Number | Sí | Subtotal antes de impuestos |
| `tax` | Number | No | Impuestos aplicados |
| `shipping` | Number | No | Costo de envío |
| `discount` | Number | No | Descuentos aplicados |
| `total` | Number | Sí | Total final del pedido |
| `shippingAddress` | Object | Sí | Dirección de entrega |
| `paymentMethod` | String | Sí | Método de pago |
| `paymentStatus` | String | No | Estado del pago |
| `deliveryMethod` | String | No | Método de entrega |
| `trackingNumber` | String | No | Número de seguimiento |
| `orderDate` | Date | Auto | Fecha del pedido |
| `deliveredAt` | Date | No | Fecha de entrega |

**Índices**:
- `{ userId: 1, createdAt: -1 }`
- `{ orderNumber: 1 }` (único)
- `{ status: 1 }`
- `{ paymentStatus: 1 }`

## 🛒 Colección: carts **[Base: admin]**

**Propósito**: Carritos de compra temporales y persistentes para usuarios registrados y visitantes.

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `userId` | ObjectId | No | Usuario propietario (null para invitados) |
| `sessionId` | String | Sí | ID de sesión único |
| `items` | Array | No | Items en el carrito |
| `subtotal` | Number | Auto | Subtotal calculado |
| `total` | Number | Auto | Total con impuestos y envío |
| `appliedCoupons` | Array | No | Cupones aplicados |
| `isActive` | Boolean | Auto | Si el carrito está activo |
| `expiresAt` | Date | Auto | Fecha de expiración |

**Índices**:
- `{ userId: 1, isActive: 1 }`
- `{ sessionId: 1 }` (único)
- `{ expiresAt: 1 }` (TTL)

## 📈 Colección: price_history **[Base: operations_db]**

**Propósito**: Historial completo de precios para tracking de cambios y análisis de tendencias.

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `productId` | ObjectId | Sí | Producto referenciado |
| `supermarketId` | String | Sí | Supermercado fuente |
| `price` | Number | Sí | Precio registrado |
| `listPrice` | Number | No | Precio de lista |
| `discount` | Number | No | Porcentaje de descuento |
| `scrapedAt` | Date | Sí | Fecha del scraping |
| `isAvailable` | Boolean | Auto | Disponibilidad del producto |
| `isOnOffer` | Boolean | Auto | Si estaba en oferta |

**Índices**:
- `{ productId: 1, scrapedAt: -1 }`
- `{ supermarketId: 1, scrapedAt: -1 }`
- `{ scrapedAt: -1 }`

## 📍 Colección: user_addresses **[Base: admin]**

**Propósito**: Gestión de direcciones de entrega y facturación de usuarios.

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `userId` | ObjectId | Sí | Usuario propietario |
| `type` | String | Auto | Tipo (home, work, other) |
| `name` | String | Sí | Nombre personalizado |
| `street` | String | Sí | Calle y número |
| `city` | String | Sí | Ciudad |
| `state` | String | Sí | Provincia/Estado |
| `postalCode` | String | Sí | Código postal |
| `country` | String | Auto | País |
| `isDefault` | Boolean | Auto | Dirección por defecto |
| `isActive` | Boolean | Auto | Dirección activa |

**Índices**:
- `{ userId: 1, isActive: 1 }`
- `{ userId: 1, isDefault: 1 }`

## 🔔 Colección: notifications **[Base: operations_db]**

**Propósito**: Sistema de notificaciones para usuarios (precio reducido, ofertas, estados de pedido).

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `userId` | ObjectId | Sí | Usuario destinatario |
| `type` | String | Sí | Tipo de notificación |
| `title` | String | Sí | Título de la notificación |
| `message` | String | Sí | Contenido del mensaje |
| `data` | Object | No | Datos específicos del tipo |
| `isRead` | Boolean | Auto | Si fue leída |
| `channels` | Array | No | Canales de envío (email, push) |
| `priority` | String | Auto | Prioridad (low, normal, high) |

**Índices**:
- `{ userId: 1, isRead: 1, createdAt: -1 }`
- `{ type: 1, priority: 1, createdAt: -1 }`

## 🔐 Colección: user_sessions **[Base: admin]**

**Propósito**: Gestión de sesiones activas de usuarios para autenticación y seguridad.

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `userId` | ObjectId | Sí | Usuario de la sesión |
| `sessionToken` | String | Sí | Token único de sesión |
| `refreshToken` | String | No | Token para refresh |
| `deviceInfo` | Object | Sí | Información del dispositivo |
| `isActive` | Boolean | Auto | Sesión activa |
| `expiresAt` | Date | Auto | Fecha de expiración |
| `lastActivity` | Date | Auto | Última actividad |

**Índices**:
- `{ userId: 1, isActive: 1 }`
- `{ sessionToken: 1 }` (único)
- `{ expiresAt: 1 }` (TTL)

## 📊 Colección: api_logs **[Base: operations_db]**

**Propósito**: Logging completo de llamadas a APIs externas para monitoreo y debugging.

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `method` | String | Sí | Método HTTP |
| `url` | String | Sí | URL llamada |
| `statusCode` | Number | No | Código de respuesta |
| `responseTime` | Number | No | Tiempo de respuesta |
| `apiType` | String | Sí | Tipo de API (scraping, payment) |
| `success` | Boolean | Auto | Si fue exitosa |
| `error` | Object | No | Información de error |
| `timestamp` | Date | Auto | Fecha de la llamada |

**Índices**:
- `{ apiType: 1, timestamp: -1 }`
- `{ timestamp: 1 }` (TTL - 30 días)

## ⚙️ Colección: system_settings **[Base: operations_db]**

**Propósito**: Configuraciones dinámicas del sistema para personalización sin redeploy.

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `key` | String | Sí | Clave única de configuración |
| `value` | Mixed | Sí | Valor de la configuración |
| `type` | String | Sí | Tipo de dato (string, number, boolean) |
| `category` | String | Auto | Categoría (general, scraping, api) |
| `description` | String | No | Descripción de la configuración |
| `defaultValue` | Mixed | No | Valor por defecto |
| `isPublic` | Boolean | Auto | Si es configuración pública |

**Índices**:
- `{ key: 1 }` (único)
- `{ category: 1, isActive: 1 }`

## �🔗 Relaciones y Flujo de Datos

### Jerarquía de Productos
```
Category (1) → Subcategory (N)
Subcategory (1) → ProductType (N)
ProductType (1) → Product (N)
```

### Relaciones Bidireccionales
- `Category.subcategories` ↔ `Subcategory.category`
- `ProductType.products` ↔ `Product.productType`
- `Product.offers` ↔ `Offer.products`

### Flujo de Scraping
1. **Supermarket** → Define fuente de datos
2. **Category/Subcategory/ProductType** → Estructura jerárquica
3. **Product** → Datos individuales con precios
4. **Filter/Offer** → Enriquecen la información

## 📈 Estrategia de Índices

### Índices Compuestos
- **Navegación jerárquica**: `{ category: 1, subcategory: 1, productType: 1 }`
- **Búsqueda por supermercado**: `{ supermarket: 1, active: 1 }`
- **Ordenamiento**: `{ priority: -1, active: 1 }`

### Índices Únicos
- **Identificadores únicos**: `ean`, `sku`, `slug`, `url`
- **Nombres únicos**: `name` en categorías y filtros

### Índices de Rendimiento
- **Precios**: `{ price: 1 }`, `{ pricePerKilo: 1 }`
- **Filtros**: `{ filters: 1 }`, `{ active: 1 }`

## 🔄 Operaciones de Mantenimiento

### Sincronización de Arrays
```javascript
// Sincronizar subcategorías en categorías
await category.syncSubcategories();

// Sincronizar productos en tipos de producto
await productType.syncProducts();
```

### Actualización de Metadatos
```javascript
// Actualizar estadísticas de categorías
await Category.updateMetadata();

// Actualizar estadísticas de subcategorías
await Subcategory.updateMetadata();
```

## 🛡️ Validaciones y Constraints

### Validaciones de Esquema
- **Precios**: Valores positivos, descuentos 0-100%
- **EAN**: Formato válido de 13 dígitos
- **URLs/Slugs**: Formatos válidos, únicos
- **Fechas**: Rangos lógicos de vigencia

### Constraints de Integridad
- **Referencias**: Validación de existencia de documentos referenciados
- **Jerarquía**: Consistencia en relaciones padre-hijo
- **Estados**: Lógica de activación/desactivación

## 📊 Consultas Comunes Optimizadas

### Navegación por Categorías
```javascript
// Categorías activas con subcategorías populadas
Category.find({ active: true })
  .populate('subcategories')
  .sort({ priority: -1 });
```

### Búsqueda de Productos
```javascript
// Productos por jerarquía completa
Product.find({
  category: 'lacteos',
  subcategory: 'leches',
  active: true
}).sort({ price: 1 });
```

### Aplicación de Filtros
```javascript
// Productos con filtros específicos
Product.find({
  filters: { $in: ['organico', 'sin-lactosa'] },
  active: true
});
```

## 🚀 Escalabilidad y Rendimiento

### Estrategias de Optimización
- **Paginación**: Para listados grandes
- **Caching**: Para categorías y filtros estáticos
- **Agregaciones**: Para estadísticas complejas
- **Sharding**: Por supermercado para distribución

### Monitoreo
- **Queries lentas**: Logging de operaciones >100ms
- **Uso de índices**: Análisis de query execution
- **Tamaño de colecciones**: Monitoreo de crecimiento

## 🔧 Scripts de Inicialización

### Datos Base Requeridos
```javascript
// Categorías principales
const categories = [
  { _id: 'lacteos', name: 'lacteos', displayName: 'Lácteos' },
  { _id: 'carnes', name: 'carnes', displayName: 'Carnes' },
  // ...
];

// Supermercados
const supermarkets = [
  { _id: 'carrefour', name: 'Carrefour', baseUrl: 'https://www.carrefour.com.ar' },
  // ...
];
```

### Secuencia de Creación
1. **Supermarkets** → Base para scraping
2. **Categories** → Estructura principal
3. **Subcategories** → Segundo nivel
4. **ProductTypes** → Granularidad máxima
5. **Filters** → Sistema de búsqueda
6. **Offers** → Promociones

## 📋 Checklist de Validación

### Estructural
- [ ] Todas las colecciones tienen esquemas definidos
- [ ] Índices están creados y optimizados
- [ ] Relaciones bidireccionales funcionan
- [ ] Validaciones están implementadas

### Funcional
- [ ] Consultas jerárquicas funcionan
- [ ] Sistema de filtros opera correctamente
- [ ] Ofertas se aplican apropiadamente
- [ ] URLs y slugs se generan correctamente

### Rendimiento
- [ ] Queries usan índices apropiados
- [ ] Paginación está implementada
- [ ] Caching está configurado
- [ ] Monitoreo está activo

---

**Esta arquitectura proporciona una base sólida para la plataforma de comparación de precios, con escalabilidad, rendimiento y mantenibilidad como prioridades principales.**</content>
<parameter name="filePath">d:\dev\caminando-onlinev11\Library\archivos\database-architecture.md




🗄️ Nueva Estructura Recomendada
1. admin (Base de datos de administración)
Propósito: Usuarios, autenticación y sesiones Colecciones:

users - Usuarios registrados
user_addresses - Direcciones de entrega
user_sessions - Sesiones activas
carts - Carritos de compra

2. caminando_online_db (Base de datos maestra)
Propósito: Datos maestros de productos y catálogo Colecciones:

products - Productos individuales
categories - Categorías principales
subcategories - Subcategorías
producttypes - Tipos específicos de producto
supermarkets - Datos de supermercados
filters - Sistema de filtros
offers - Ofertas y promociones

3. operations_db (Base de datos operativa)
Propósito: Datos transaccionales, logs y configuración Colecciones:

orders - Pedidos realizados
price_history - Historial de precios
notifications - Notificaciones del sistema
api_logs - Logs de llamadas a APIs
system_settings - Configuraciones del sistema

## 🔧 Implementación Técnica

### Conexiones de Base de Datos
```javascript
// Conexiones separadas por base de datos
const mongoose = require('mongoose');

// Base admin (usuarios, sesiones)
const adminConnection = mongoose.createConnection('mongodb://localhost:27017/admin', {
  useNewUrlParser: true,
  useUnifiedTopology: true
});

// Base operations (logs, transacciones)
const operationsConnection = mongoose.createConnection('mongodb://localhost:27017/operations_db', {
  useNewUrlParser: true,
  useUnifiedTopology: true
});

// Base procesada (datos normalizados para frontend)
const processedConnection = mongoose.createConnection('mongodb://localhost:27017/caminando_online_db', {
  useNewUrlParser: true,
  useUnifiedTopology: true
});

// Bases raw por supermercado
const carrefourConnection = mongoose.createConnection('mongodb://localhost:27017/carrefour', {
  useNewUrlParser: true,
  useUnifiedTopology: true
});

const diaConnection = mongoose.createConnection('mongodb://localhost:27017/dia', {
  useNewUrlParser: true,
  useUnifiedTopology: true
});

const jumboConnection = mongoose.createConnection('mongodb://localhost:27017/jumbo', {
  useNewUrlParser: true,
  useUnifiedTopology: true
});

const veaConnection = mongoose.createConnection('mongodb://localhost:27017/vea', {
  useNewUrlParser: true,
  useUnifiedTopology: true
});

const discoConnection = mongoose.createConnection('mongodb://localhost:27017/disco', {
  useNewUrlParser: true,
  useUnifiedTopology: true
});
```

### Modelos por Base de Datos
```javascript
// Modelos admin
const User = adminConnection.model('User', userSchema);
const Session = adminConnection.model('Session', sessionSchema);

// Modelos operations
const Transaction = operationsConnection.model('Transaction', transactionSchema);
const Log = operationsConnection.model('Log', logSchema);

// Modelos procesados (frontend)
const Category = processedConnection.model('Category', categorySchema);
const Product = processedConnection.model('Product', productSchema);
const Supermarket = processedConnection.model('Supermarket', supermarketSchema);

// Modelos raw por supermercado (scraping)
const CarrefourProduct = carrefourConnection.model('Product', rawProductSchema);
const DiaProduct = diaConnection.model('Product', rawProductSchema);
const JumboProduct = jumboConnection.model('Product', rawProductSchema);
const VeaProduct = veaConnection.model('Product', rawProductSchema);
const DiscoProduct = discoConnection.model('Product', rawProductSchema);
```

### Scripts de Scraping
```javascript
// Ejemplo: Scraper Carrefour
const scrapeCarrefour = async () => {
  const products = await scrapeCarrefourWebsite();
  await CarrefourProduct.insertMany(products);
};

// Ejemplo: Procesamiento ETL
const processProducts = async () => {
  // Leer de bases raw
  const carrefourProducts = await CarrefourProduct.find({});
  const diaProducts = await DiaProduct.find({});
  
  // Normalizar y combinar
  const normalizedProducts = normalizeProducts([...carrefourProducts, ...diaProducts]);
  
  // Guardar en base procesada
  await Product.insertMany(normalizedProducts);
};
```

## 🔄 Flujo de Trabajo

### 1. Scraping de Datos Raw
```javascript
// Paso 1: Ejecutar scrapers por supermercado
const scrapeAllSupermarkets = async () => {
  await Promise.all([
    scrapeCarrefour(),
    scrapeDia(),
    scrapeJumbo(),
    scrapeVea(),
    scrapeDisco()
  ]);
};
```

### 2. Procesamiento ETL
```javascript
// Paso 2: Normalizar y combinar datos
const etlProcess = async () => {
  // Leer datos raw de todas las bases
  const rawData = await readAllRawData();
  
  // Normalizar categorías, productos, precios
  const normalizedData = await normalizeData(rawData);
  
  // Limpiar base procesada
  await clearProcessedDatabase();
  
  // Insertar datos normalizados
  await insertNormalizedData(normalizedData);
};
```

### 3. Validación de Datos
```javascript
// Paso 3: Verificar integridad
const validateData = async () => {
  const stats = await getDatabaseStats();
  
  // Verificar que todas las categorías tienen productos
  // Verificar que precios son válidos
  // Verificar que enlaces funcionan
  
  return validationResults;
};
```

### 4. Actualización del Frontend
```javascript
// Paso 4: Notificar cambios al frontend
const updateFrontend = async () => {
  // Invalidar caches
  await clearFrontendCache();
  
  // Actualizar índices de búsqueda
  await updateSearchIndex();
  
  // Generar sitemap actualizado
  await generateSitemap();
};
```

### 5. Monitoreo y Alertas
```javascript
// Paso 5: Verificar estado del sistema
const monitorSystem = async () => {
  // Verificar conexiones a bases de datos
  // Verificar espacio en disco
  // Verificar rendimiento de queries
  // Enviar alertas si hay problemas
  
  await logSystemHealth();
};
```

### Programación de Tareas
- **Scraping**: Cada 4 horas (diurno), cada 8 horas (nocturno)
- **ETL**: Después de cada scraping completo
- **Validación**: Después de ETL
- **Backup**: Diario para admin, semanal para operations y processed
- **Monitoreo**: Continuo con alertas automáticas

### Recuperación de Errores
- **Falla en scraping**: Reintentar automáticamente, usar datos anteriores si falla
- **Falla en ETL**: Rollback a versión anterior, alertar al equipo
- **Falla en validación**: Corregir datos manualmente o usar backup
- **Falla en actualización**: Mantener versión anterior activa hasta corrección

## 📚 Referencias

### Documentos Relacionados
- **`base-datos.md`**: Guía general de manejo de MongoDB
- **`seguridad.md`**: Protocolos de seguridad para datos sensibles
- **`sandbox.md`**: Entorno de desarrollo y experimentación
- **`puertos.md`**: Asignación de puertos para servicios

### Modelos de Datos
- **`models/user/`**: Esquemas de usuario y autenticación
- **`models/product/`**: Esquemas de productos y categorías
- **`models/commerce/`**: Esquemas de supermercados y operaciones
- **`models/system/`**: Esquemas de configuración y logs

### Scripts de Implementación
- **`scripts/database/`**: Scripts de inicialización y migración
- **`scripts/scraping/`**: Scripts de extracción de datos
- **`scripts/etl/`**: Scripts de procesamiento y normalización

## 🚀 Próximos Pasos

### Implementación Inmediata
1. **Crear conexiones separadas** para las 8 bases de datos
2. **Actualizar modelos existentes** para usar conexiones específicas
3. **Implementar scrapers** para escribir en bases raw por supermercado
4. **Desarrollar proceso ETL** para normalización de datos
5. **Crear sistema de validación** de integridad de datos

### Mejoras Futuras
1. **Sistema de backup automatizado** con estrategias diferenciadas
2. **Monitoreo en tiempo real** del estado de las bases de datos
3. **Optimización de índices** basada en patrones de consulta
4. **Sistema de cache** para mejorar rendimiento del frontend
5. **API de administración** para gestión de bases de datos

### Escalabilidad
1. **Sharding** para bases de datos de alto volumen
2. **Replicación** para alta disponibilidad
3. **Compresión** de datos históricos
4. **Particionamiento** por fecha para datos temporales

---

**Última actualización**: Septiembre 2025
**Versión**: 1.0.0
**Estado**: Documentación completa - Listo para implementación

