# Inicialización de Base de Datos - Caminando Online

Este script inicializa la estructura de la base de datos MongoDB para el proyecto Caminando Online.

## Estructura Creada

### Colecciones
- **categories**: Categorías de productos (Frutas, Carnes, Lácteos, etc.)
- **subcategories**: Subcategorías dentro de cada categoría
- **products**: Productos individuales con precios, supermercados, etc.
- **supermarkets**: Información de supermercados disponibles
- **users**: Usuarios del sistema (futuro)

### Datos Iniciales
- 6 categorías principales con íconos
- 5 supermercados principales (Carrefour, Jumbo, Dia, Vea, Disco)

### Índices
- Índices en campos frecuentemente consultados de la colección `products`

## Uso

1. Asegúrate de que MongoDB esté ejecutándose
2. Activa el entorno virtual: `venv\Scripts\activate`
3. Ejecuta el script: `python src/scripts/initialize_database.py`

## Notas
- El script verifica si las colecciones ya existen antes de crearlas
- No sobrescribe datos existentes
- Si hay error de conexión, verifica que MongoDB esté corriendo en localhost:27017