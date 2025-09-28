# Desglose de Archivo: carrefour_outerhtml_crawler.py

## Propósito
Este archivo implementa un crawler básico para extraer outerHTML completo de páginas clave del sitio web de Carrefour. Se utiliza como base para analizar selectores y estructura DOM offline antes de desarrollar scrapers específicos.

## Relaciones
- Ubicado en `src/backend/src/scripts/scrapers/carrefour/`
- Guarda archivos HTML en `src/backend/src/scripts/scrapers/carrefour/HTML/`
- No depende de otros archivos; es independiente para extracción inicial
- Preparación para scrapers jerárquicos (Supermarket Info → Categories → etc.)

## Recreación
1. Crear archivo en `src/backend/src/scripts/scrapers/carrefour/carrefour_outerhtml_crawler.py`
2. Importar dependencias: `selenium`, `webdriver_manager`, `os`, `time`, `datetime`
3. Definir función `extract_outerhtml()` para capturar outerHTML con Selenium
4. Implementar `find_links()` para encontrar enlaces por patrones
5. Crear `crawl_carrefour()` que:
   - Configura Edge headless
   - Extrae home page
   - Intenta click en menú "Categorías"
   - Encuentra enlaces a categorías
   - Extrae URLs específicas (almacén, producto ejemplo, ofertas)
   - Extrae subcategorías del sidebar
6. En `__main__`, definir output_dir como `HTML/` y ejecutar crawl

## Fecha de Incorporación
Septiembre 28, 2025

## Feature Asociada
Desarrollo inicial de scrapers para Carrefour - Fase outerHTML