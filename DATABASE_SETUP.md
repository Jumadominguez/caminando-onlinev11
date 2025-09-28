# 🚀 Configuración Multi-Database - Caminando Online V4

## 📊 Arquitectura de Base de Datos

Este proyecto implementa una arquitectura **multi-database** con **8 bases de datos separadas** para optimizar el rendimiento, mantenibilidad y escalabilidad de la plataforma de comparación de precios.

### 🗄️ Estructura de Bases de Datos

#### **Bases de Administración y Operaciones:**
- **`admin`** - Usuarios, sesiones, carritos y direcciones
- **`operations_db`** - Pedidos, historial de precios, logs y configuraciones

#### **Base Procesada (Frontend):**
- **`caminando_online_db`** - Datos normalizados y unificados para el frontend

#### **Bases Raw (Scraping por Supermercado):**
- **`carrefour`** - Datos crudos extraídos de Carrefour
- **`dia`** - Datos crudos extraídos de Dia
- **`jumbo`** - Datos crudos extraídos de Jumbo
- **`vea`** - Datos crudos extraídos de Vea
- **`disco`** - Datos crudos extraídos de Disco

## ⚙️ Configuración Inicial

### 1. Instalar Dependencias

```bash
cd src/backend
npm install
```

### 2. Configurar Variables de Entorno

Copia el archivo de ejemplo y configúralo:

```bash
cp .env.example .env
```

Edita el archivo `.env` con tus configuraciones específicas.

### 3. Verificar MongoDB

Asegúrate de que MongoDB esté ejecutándose:

```bash
# Verificar servicio MongoDB
mongod --version

# O verificar proceso en Windows
Get-Process -Name mongod
```

### 4. Inicializar Bases de Datos

Ejecuta el script de inicialización:

```bash
cd src/backend
node scripts/initialize_app_database.js
```

## 🔧 Uso de las Conexiones

### Acceso a Conexiones en el Código

Las conexiones están disponibles globalmente a través de `global.databaseConnections`:

```javascript
// En cualquier archivo del backend
const { admin, operations, processed, carrefour, dia, jumbo, vea, disco } = global.databaseConnections;

// Ejemplo: Acceder a usuarios
const User = admin.model('User', userSchema);

// Ejemplo: Acceder a productos procesados
const Product = processed.model('Product', productSchema);

// Ejemplo: Acceder a datos raw de Carrefour
const CarrefourProduct = carrefour.model('Product', rawProductSchema);
```

### Modelos por Base de Datos

#### Base `admin`:
- `User` - Usuarios registrados
- `UserAddress` - Direcciones de entrega
- `UserSession` - Sesiones activas
- `Cart` - Carritos de compra

#### Base `operations_db`:
- `Order` - Pedidos realizados
- `PriceHistory` - Historial de precios
- `Notification` - Notificaciones del sistema
- `ApiLog` - Logs de llamadas a APIs
- `SystemSetting` - Configuraciones del sistema

#### Base `caminando_online_db`:
- `Supermarket` - Metadatos de supermercados
- `Category` - Categorías principales
- `Subcategory` - Subcategorías
- `ProductType` - Tipos específicos de producto
- `Product` - Productos individuales
- `Filter` - Sistema de filtros
- `Offer` - Ofertas y promociones

#### Bases Raw (`carrefour`, `dia`, `jumbo`, `vea`, `disco`):
- `Supermarket` - Metadatos del sitio
- `Category` - Categorías originales
- `Subcategory` - Subcategorías originales
- `ProductType` - Tipos sin normalizar
- `Product` - Productos con estructura cruda
- `Offer` - Ofertas específicas
- `Filter` - Filtros del sitio

## 🚀 Inicio del Servidor

```bash
# Desde la raíz del proyecto
cd src/backend
npm start
```

El servidor verificará automáticamente todas las conexiones de base de datos al iniciar y mostrará el estado de cada una.

### Salida Esperada

```
🚀 Initializing Caminando Online V4 Server...
📊 Checking database connections...
🔗 admin: MongoDB connected successfully
🔗 operations: MongoDB connected successfully
🔗 processed: MongoDB connected successfully
🔗 carrefour: MongoDB connected successfully
🔗 dia: MongoDB connected successfully
🔗 jumbo: MongoDB connected successfully
🔗 vea: MongoDB connected successfully
🔗 disco: MongoDB connected successfully
📈 Database Status: 8/8 connections successful
🌐 Server running on port 5000
🏗️  Architecture: Multi-database (8 databases)
📊 Connected databases: 8/8
✅ Caminando Online V4 Server started successfully!
```

## 🔍 Verificación de Conexiones

### Verificar Estado de Conexiones

```javascript
// En la consola del servidor (temporal debugging)
const status = await checkConnections();
console.log(status);
```

### Verificar Colecciones

```javascript
// Verificar colecciones en cada base
const adminCollections = await admin.db.listCollections().toArray();
const processedCollections = await processed.db.listCollections().toArray();
console.log('Admin collections:', adminCollections.map(c => c.name));
console.log('Processed collections:', processedCollections.map(c => c.name));
```

## 🛠️ Desarrollo y Debugging

### Agregar Nueva Base de Datos

1. Agregar conexión en `server.js`
2. Configurar variable de entorno en `.env`
3. Actualizar `databaseConnections` object
4. Crear modelos específicos para la nueva base

### Monitoreo de Conexiones

El servidor incluye monitoreo automático de:
- Estado de conexión de cada base
- Manejo de reconexiones automáticas
- Cierre graceful al detener el servidor
- Logging detallado de errores

### Troubleshooting

#### Problema: "Connection failed"
```
❌ carrefour: Connection failed - MongoServerError: connect ECONNREFUSED ::1:27017
```

**Solución:**
1. Verificar que MongoDB esté ejecutándose
2. Verificar la URI de conexión en `.env`
3. Verificar permisos de red/firewall

#### Problema: "Authentication failed"
```
❌ admin: Connection failed - MongoServerError: Authentication failed
```

**Solución:**
1. Verificar credenciales en `.env`
2. Crear usuario en MongoDB si no existe
3. Verificar permisos del usuario

## 📚 Documentación Relacionada

- **`Library/archivos/database-architecture.md`** - Arquitectura completa de base de datos
- **`Library/archivos/models/`** - Documentación detallada de cada modelo
- **`scripts/database/`** - Scripts de inicialización y migración

## 🔒 Seguridad

- Nunca commitear el archivo `.env` (ya está en `.gitignore`)
- Usar credenciales específicas para cada base de datos
- Configurar autenticación en MongoDB para producción
- Implementar rate limiting y validación de inputs

## 🚀 Próximos Pasos

1. **Implementar modelos** - Crear archivos de modelo para cada colección
2. **Desarrollar APIs** - Crear endpoints REST para cada tipo de dato
3. **Implementar scraping** - Scripts para poblar bases raw
4. **Desarrollar ETL** - Procesos de normalización de datos
5. **Testing** - Pruebas unitarias e integración

---

**Versión**: 1.0.0
**Última actualización**: Septiembre 2025
**Estado**: ✅ Implementado y documentado