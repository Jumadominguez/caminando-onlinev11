# Instructivo para Manejo de Base de Datos con MongoDB Atlas

Este documento proporciona guías detalladas para el manejo correcto de MongoDB Atlas en proyectos con Vibe Coding. Enfocado en conexiones específicas por dominio, arquitectura modular y registro de cambios para evitar conflictos y mantener escalabilidad. Adaptado a la arquitectura actual con **8 bases de datos separadas** para optimizar rendimiento, mantenibilidad y escalabilidad de la plataforma de comparación de precios.

## Introducción

MongoDB Atlas es la base de datos NoSQL predeterminada para persistencia flexible de datos en la nube. Esta arquitectura implementa una **arquitectura multi-database** con **8 bases de datos separadas** para optimizar el rendimiento, mantenibilidad y escalabilidad de la plataforma de comparación de precios. Los datos se organizan en capas: crudos (de scraping) y procesados (limpios y optimizados).

## Arquitectura de Base de Datos

### Estructura de Bases de Datos
La base de datos se divide en **8 bases de datos separadas** para optimizar el rendimiento y la escalabilidad:

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

### Modelos por Base de Datos

#### Base `admin`:
- `User` - Usuarios registrados
- `UserAddress` - Direcciones de entrega
- `UserSession` - Sesiones activas
- `Cart` - Carritos de compra

#### Base `operations_db`:
- `Order` - Pedidos realizados
- `Notification` - Notificaciones del sistema
- `ApiLog` - Logs de llamadas a APIs
- `SystemSettings` - Configuraciones del sistema

#### Base `caminando_online_db`:
- `Supermarket` - Metadatos de supermercados
- `Category` - Categorías principales
- `Subcategory` - Subcategorías
- `ProductType` - Tipos específicos de producto
- `Product` - Productos individuales
- `Filter` - Sistema de filtros
- `Offer` - Ofertas y promociones
- `PriceHistory` - Historial de precios

#### Bases Raw (`carrefour`, `dia`, `jumbo`, `vea`, `disco`):
- `Supermarket` - Metadatos del sitio
- `Category` - Categorías originales
- `Subcategory` - Subcategorías originales
- `ProductType` - Tipos sin normalizar
- `Product` - Productos con estructura cruda
- `Offer` - Ofertas específicas
- `Filter` - Filtros del sitio

## Normalización y Unificación de Datos

**PENDIENTE DE DEFINIR**: Esta sección se completará cuando se haya extraído y analizado la información de todas las webs de supermercados. Incluirá los criterios específicos para:

- Agrupación de categorías con nombres similares (ej: "carnes", "carnicería", "carnes y pescados" → "Carnes")
- Normalización de subcategorías y tipos de producto
- Estandarización de unidades, medidas y formatos
- Resolución de duplicados y conflictos de datos
- Reglas para mantener consistencia en precios, descuentos y disponibilidad

### Conexiones Específicas
Cada base de datos utiliza una conexión MongoDB Atlas dedicada:
- `admin`: Para usuarios y sesiones → `admin`
- `operations`: Para operaciones y logs → `operations_db`
- `processed`: Para datos procesados → `caminando_online_db`
- `carrefour`: Para datos raw de Carrefour → `carrefour`
- `dia`: Para datos raw de Dia → `dia`
- `jumbo`: Para datos raw de Jumbo → `jumbo`
- `vea`: Para datos raw de Vea → `vea`
- `disco`: Para datos raw de Disco → `disco`

## Conexiones a MongoDB Atlas

### Creación de Conexiones por Dominio
- **Nombres únicos**: Usa nombres específicos por dominio (processed_db, admin_db, operations_db).
- **Variables de Entorno**: Almacena URIs en archivos `.env` con formato Atlas (usa placeholders, nunca credenciales reales):
  ```
  MONGO_ADMIN_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/admin?retryWrites=true&w=majority
  MONGO_OPERATIONS_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/operations_db?retryWrites=true&w=majority
  MONGO_PROCESSED_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/caminando_online_db?retryWrites=true&w=majority
  MONGO_CARREFOUR_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/carrefour?retryWrites=true&w=majority
  MONGO_DIA_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/dia?retryWrites=true&w=majority
  MONGO_JUMBO_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/jumbo?retryWrites=true&w=majority
  MONGO_VEA_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/vea?retryWrites=true&w=majority
  MONGO_DISCO_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/disco?retryWrites=true&w=majority
  ```
- **Configuración Global**: Las conexiones se establecen globalmente en `global.databaseConnections` para acceso desde modelos.

### Seguridad
- Nunca hardcodea credenciales.
- Usa autenticación con usuarios específicos por base de datos.
- Implementa SSL/TLS (incluido en Atlas).
- Rota contraseñas periódicamente.
- Configura IP Whitelist en Atlas (restringe a IPs necesarias).

### Limitaciones de Atlas
- **Bases del sistema**: `local` y `config` no existen en Atlas; ignóralas.
- **Costo**: Monitorea uso gratuito vs pago.

## Estructura de Modelos

### Esquemas Mongoose
- **Campos requeridos**: Define claramente campos obligatorios vs opcionales.
- **Validaciones**: Usa validaciones integradas (min, max, enum) y custom.
- **Índices**: Crea índices en campos frecuentemente consultados para rendimiento.
- **Referencias**: Usa ObjectId refs para relaciones entre modelos.
- **Virtuals**: Implementa campos virtuales para datos calculados.
- **Middlewares**: Pre/post hooks para lógica automática (hasheo de passwords, timestamps).

### Métodos y Estáticos
- **Métodos de instancia**: Lógica específica del documento (e.g., `calculateTotal()` en Order).
- **Métodos estáticos**: Consultas comunes (e.g., `findByFilters()` en Product).
- **Helpers**: Métodos utilitarios (e.g., `getFinalPrice()` en Product).

### Ejemplos de Patrones
- **Product**: Esquema rico con precios, descuentos, filtros, referencias a ofertas.
- **User**: Autenticación completa con bcrypt, roles, preferencias y estadísticas.
- **SystemSettings**: Configuraciones dinámicas con validación y versionado.
- **Order**: Gestión completa de pedidos con estados, pagos y envíos.

## Evolución y Mutaciones

### Arquitectura Evolutiva
La arquitectura puede cambiar durante el desarrollo. No asumas diseño final desde el inicio.

### Iteraciones
- **Sandbox/Experiments/**: Prueba esquemas alternativos.
- **Sandbox/Prototypes/**: Validación de prototipos.
- **Producción**: Implementación final.

### Registro de Cambios
Documenta cada mutación en `Library/archivos/db-cambios.md`. Formato:
```
# Cambios en Arquitectura MongoDB Atlas

## Fecha: [Fecha]
## Cambio: [Descripción, e.g., Migración a Atlas y cambio de admin a users_db]
## Razón: [Por qué se cambió]
## Impacto: [Colecciones afectadas, migraciones]
## Commit: [Número de commit]
```

### Migraciones
- Usa scripts de migración para cambios en esquemas.
- Realiza backups antes de migraciones (Atlas tiene backups automáticos).
- Prueba migraciones en entornos de desarrollo.

### Regla de Simetría
**IMPORTANTE**: Si en algún momento se realiza un cambio en la arquitectura de base de datos (agregar dominio, modificar esquema, cambiar conexiones, etc.), este instructivo DEBE ser modificado inmediatamente para mantener simetría con la arquitectura actual. La documentación debe reflejar siempre el estado real del sistema.

## Mejores Prácticas

### Diseño
- **Normalización**: Mantén consistencia en datos procesados.
- **Escalabilidad**: Diseña para crecimiento (sharding disponible en Atlas).
- **Performance**: Optimiza consultas con índices compuestos y agregaciones.

### Seguridad
- **Validación**: Siempre valida inputs en esquemas.
- **Auditoría**: Registra cambios sensibles (SystemSettings con versionado).
- **Privacidad**: No almacenes datos sensibles sin encriptación.
- **Atlas Security**: Habilita autenticación de dos factores, encriptación en reposo.

### Mantenimiento
- **Backup**: Atlas proporciona backups automáticos; configura retención.
- **Monitoring**: Usa Atlas dashboards para performance y uso.
- **Testing**: DB de test separadas para cada dominio (crea clusters separados si es necesario).

### Desarrollo
- **Versionado**: Incluye DB en Git (excluyendo datos sensibles).
- **Documentación**: Mantén modelos documentados en `Library/archivos/`.
- **Consistencia**: Usa patrones uniformes en todos los modelos.

## Flujo de Trabajo

1. **Planificación**: Define requisitos por dominio basado en `cuestionario-inicial.md`.
2. **Diseño**: Crea esquemas iniciales en `Sandbox/Experiments/`.
3. **Implementación**: Desarrolla modelos con conexiones específicas a Atlas.
4. **Testing**: Valida en DB de test.
5. **Evolución**: Registra cambios y actualiza este instructivo.
6. **Integración**: Despliega con backups y migraciones.

## Referencias

- Consulta `puertos.md` para asignación de puertos (no aplica a Atlas).
- Registra en `registro-archivos.md` archivos relacionados con DB.
- Revisa modelos en `src/backend/src/models/` para ejemplos actuales.
- Consulta `Library/archivos/DATABASE_SETUP.md` para detalles específicos de configuración multi-database.

Este instructivo asegura un manejo seguro, modular y adaptable de MongoDB Atlas. Actualiza según evolucione el proyecto y mantén simetría con la arquitectura implementada.