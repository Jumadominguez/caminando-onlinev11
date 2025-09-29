# Desglose de Archivo: 3-carrefour-subcategories.py

## Propósito
Script completo para scraping de subcategorías de Carrefour (Nivel 3). Extrae subcategorías de páginas de categoría, maneja operaciones de base de datos (insertar/actualizar/eliminar) y proporciona logging consolidado. Incluye modo test para desarrollo sin conexión a base de datos.

## Relaciones con Otros Archivos
- Depende de: `carrefour_subcategories_scraping_process.md` (documentación del proceso)
- Interactúa con: Base de datos MongoDB Atlas (colecciones `categories` y `subcategories`)
- Utiliza: GeckoDriver para automatización de Firefox
- Genera: Logs en `3-carrefour-subcategories.log`

## Recreación
1. Crear archivo en `Sandbox/Prototypes/3-carrefour-subcategories.py`
2. Instalar dependencias: `pip install selenium pymongo webdriver-manager`
3. Descargar GeckoDriver en `drivers/geckodriver.exe`
4. Configurar conexión MongoDB Atlas con credenciales reales
5. Ejecutar: `python 3-carrefour-subcategories.py`

## Funcionalidades Clave
- **Extracción específica**: Solo subcategorías del filtro "Sub-Categoría" (38-26 items vs 88-76 totales)
- **Modo test**: Simula operaciones de BD cuando no hay conexión
- **Manejo robusto**: JavaScript click para botones, textContent para extracción de texto
- **Logging consolidado**: Un línea por categoría con estadísticas de operaciones

## Fecha de Incorporación
29 de septiembre de 2025

## Feature Asociada
Scraping de subcategorías Carrefour - Nivel 3 de jerarquía de productos