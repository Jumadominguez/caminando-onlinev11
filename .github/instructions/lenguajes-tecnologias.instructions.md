# Lenguajes y Tecnologías del Proyecto

## 📋 Información General

**Proyecto**: Caminando Online V4 - Plataforma de Comparación de Precios
**Fecha**: Septiembre 2025
**Versión**: 1.0.0
**Tipo**: Aplicación Web Full-Stack

Este documento describe todos los lenguajes de programación, frameworks y tecnologías utilizados en el proyecto Caminando Online, una plataforma de comparación de precios que extrae datos de supermercados como Carrefour.

## 🐍 Python

### Rol en el Proyecto
- **Scraping de datos**: Extracción automatizada de información de productos desde sitios web de supermercados
- **Procesamiento de datos**: Limpieza, transformación y estructuración de datos extraídos
- **Automatización**: Scripts para procesamiento batch y tareas programadas

### Tecnologías y Librerías
- **Selenium WebDriver**: Automatización de navegadores para scraping web
- **BeautifulSoup/Requests**: Parsing HTML y requests HTTP
- **Pandas**: Manipulación y análisis de datos
- **PyMongo**: Conexión y operaciones con MongoDB
- **Threading**: Procesamiento paralelo para mejorar rendimiento

### Archivos Principales
- `Sandbox/Experiments/*.py` - Scripts de desarrollo y experimentación
- `Sandbox/prototypes/*.py` - Versiones validadas de scripts
- `check_db.py`, `clear_products.py` - Utilidades de base de datos

### Versiones
- **Python**: 3.8+
- **Selenium**: 4.x
- **PyMongo**: 4.x

## ☕ JavaScript/Node.js

### Rol en el Proyecto
- **Backend API**: Servidor REST API para comunicación frontend-backend
- **Autenticación**: Gestión de usuarios y sesiones
- **Middleware**: Procesamiento de requests, validación y seguridad

### Tecnologías y Frameworks
- **Express.js**: Framework web minimalista para APIs
- **MongoDB/Mongoose**: Base de datos y ODM
- **JWT**: Autenticación basada en tokens
- **bcryptjs**: Hashing de contraseñas
- **Helmet**: Seguridad HTTP headers
- **CORS**: Cross-Origin Resource Sharing
- **Rate Limiting**: Control de frecuencia de requests

### Archivos Principales
- `backend/server.js` - Punto de entrada del servidor
- `backend/src/app.js` - Configuración de la aplicación Express
- `backend/src/routes/` - Definición de endpoints API
- `backend/src/controllers/` - Lógica de negocio
- `backend/src/models/` - Modelos de datos MongoDB

### Versiones
- **Node.js**: 18.x+
- **Express**: 5.x
- **MongoDB**: 8.x

## 🔷 TypeScript

### Rol en el Proyecto
- **Frontend type-safe**: Desarrollo del interfaz de usuario con tipado estático
- **Mejor mantenibilidad**: Detección de errores en tiempo de desarrollo
- **Mejor DX**: Autocompletado y refactorización avanzada

### Tecnologías y Frameworks
- **React**: Biblioteca para interfaces de usuario
- **React DOM**: Renderizado en el navegador
- **TypeScript**: Superset de JavaScript con tipos
- **Sass/SCSS**: Preprocesador CSS para estilos avanzados

### Archivos Principales
- `frontend/tsconfig.json` - Configuración de TypeScript
- `frontend/src/` - Código fuente del frontend (componentes React)
- `frontend/public/` - Archivos estáticos

### Versiones
- **TypeScript**: 4.9.x
- **React**: 19.x

## ⚛️ React

### Rol en el Proyecto
- **Interfaz de usuario**: Componentes interactivos para comparación de precios
- **Estado de aplicación**: Gestión del estado de productos, carrito, filtros
- **Navegación**: Routing entre diferentes secciones de la aplicación

### Características Implementadas
- **Componentes funcionales**: Con hooks para estado y efectos
- **Responsive design**: Adaptable a diferentes tamaños de pantalla
- **Modular architecture**: Componentes reutilizables y mantenibles

### Versiones
- **React**: 19.1.x
- **React DOM**: 19.1.x
- **React Scripts**: 5.0.x

## 🍃 MongoDB

### Rol en el Proyecto
- **Base de datos principal**: Almacenamiento de datos de productos, categorías y usuarios
- **Datos no estructurados**: Flexibilidad para diferentes tipos de productos
- **Escalabilidad**: Capacidad para manejar grandes volúmenes de datos

### Colecciones Principales
- **categories**: Categorías de productos
- **subcategories**: Subcategorías
- **products**: Información detallada de productos
- **producttypes**: Tipos de productos por subcategoría
- **users**: Información de usuarios (futuro)

### Características
- **Document-based**: Almacenamiento en documentos JSON-like
- **Indexing**: Optimización de consultas frecuentes
- **Aggregation**: Procesamiento avanzado de datos

### Versiones
- **MongoDB**: 8.0.x
- **Mongoose**: 8.x (ODM para Node.js)

## 🎨 HTML/CSS/Sass

### Rol en el Proyecto
- **Estructura**: Maquetado semántico de páginas web
- **Estilos**: Diseño visual y experiencia de usuario
- **Responsive**: Adaptabilidad a diferentes dispositivos

### Tecnologías
- **HTML5**: Estructura semántica moderna
- **CSS3**: Estilos avanzados con flexbox, grid, animaciones
- **Sass/SCSS**: Preprocesador para estilos mantenibles

### Características
- **Mobile-first**: Diseño prioritario para móviles
- **Component-based**: Estilos modulares por componente
- **Variables**: Sistema de colores y medidas consistente

## 🐚 Shell/PowerShell

### Rol en el Proyecto
- **Automatización**: Scripts para setup, deployment y mantenimiento
- **Control de procesos**: Gestión de servicios (MongoDB, Node.js)
- **Testing**: Ejecución de tests y validaciones

### Scripts Comunes
- **Inicio de servicios**: `mongod`, `npm start`
- **Gestión de procesos**: Start, stop, restart de servicios
- **File operations**: Copia, movimiento y limpieza de archivos
- **Git operations**: Control de versiones

## 🔧 Herramientas de Desarrollo

### Control de Versiones
- **Git**: Sistema de control de versiones distribuido
- **GitHub**: Plataforma de colaboración y hosting

### Entorno de Desarrollo
- **VS Code**: Editor principal con extensiones especializadas
- **Node.js**: Runtime para JavaScript
- **Python venv**: Entornos virtuales aislados
- **MongoDB Compass**: GUI para gestión de base de datos

### Testing
- **Jest**: Framework de testing para JavaScript/React
- **Testing Library**: Utilidades para testing de componentes React
- **PyTest**: Framework de testing para Python (futuro)

## 📊 Arquitectura General

```
Frontend (TypeScript/React)
    ↓ HTTP Requests
Backend (Node.js/Express)
    ↓ Database Queries
MongoDB (NoSQL Database)
    ↑ Data Storage
Python Scripts (Scraping/Automation)
```

## 🔄 Flujo de Datos

1. **Scraping**: Python scripts extraen datos de supermercados
2. **Almacenamiento**: Datos se guardan en MongoDB
3. **API**: Backend Node.js expone datos via REST API
4. **Frontend**: React consume API y muestra datos al usuario
5. **Interacción**: Usuario interactúa con la aplicación

## 📈 Escalabilidad y Rendimiento

- **Backend**: Express.js optimizado con rate limiting y caching
- **Base de datos**: MongoDB con índices optimizados
- **Frontend**: React con lazy loading y code splitting
- **Scraping**: Procesamiento paralelo con Python threading

## 🔒 Seguridad

- **Backend**: Helmet, CORS, rate limiting, input validation
- **Autenticación**: JWT tokens con bcrypt hashing
- **Base de datos**: Validación de esquemas con Mongoose
- **Frontend**: Sanitización de inputs y CSP headers

## 🚀 Deployment

- **Backend**: Node.js server en puerto configurado
- **Frontend**: Build estático servido por web server
- **Base de datos**: MongoDB local o en la nube
- **Monitoreo**: Logs centralizados y health checks

---

**Este documento se actualizará conforme evolucione la tecnología del proyecto.**</content>
<parameter name="filePath">d:\dev\caminando-onlinev10\Library\lenguajes-tecnologias.md