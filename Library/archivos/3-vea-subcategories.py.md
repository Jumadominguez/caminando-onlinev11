# Desglose de Archivo: 3-vea-subcategories.py

## Propósito
Este archivo implementa el scraper de subcategorías para el supermercado Vea, adaptado del scraper de Disco. Extrae subcategorías de cada categoría principal desde el sitio web vea.com.ar, utilizando la estructura VTEX específica del sitio.

## Relaciones
- **Base de datos**: Conecta a la base `vea` en MongoDB Atlas
- **Dependencias**: Utiliza categorías existentes de la colección `categories` en la base `vea`
- **Salida**: Almacena subcategorías en la colección `subcategories` de la base `vea`
- **Referencia**: Adaptado de `3-disco-subcategories.py` con selectores específicos para Vea

## Recreación
1. Crear archivo en `src/backend/src/scripts/scrapers/vea/3-vea-subcategories.py`
2. Importar dependencias: selenium, pymongo, concurrent.futures, dotenv
3. Configurar conexión MongoDB con URI `MONGO_VEA_URI`
4. Implementar clase `VeaSubcategoriesScraper` con métodos:
   - `__init__`: Inicialización con opciones de browser
   - `get_categories_from_db`: Obtener categorías de la base `vea`
   - `process_single_category`: Procesar categoría individual con browser dedicado
   - `_extract_subcategories_threaded`: Extraer subcategorías usando selector `.vtex-search-result-3-x-filter__container--category-3`
   - `run_scraping`: Ejecutar scraping paralelo con ThreadPoolExecutor
5. Configurar selectores específicos para Vea:
   - Contenedor de subcategorías: `.vtex-search-result-3-x-filter__container--category-3`
   - Botón expandir: `.vtex-search-result-3-x-seeMoreButton`
   - Labels: `label.vtex-checkbox__label`
6. Implementar manejo de botón "Mostrar X más" para expandir subcategorías
7. Configurar URLs con dominio `vea.com.ar`
8. Agregar logging detallado y manejo de errores

## Fecha de Incorporación
Septiembre 30, 2025

## Feature Asociada
Scraping de subcategorías para Vea - Parte del sistema de comparación de precios

## Notas Técnicas
- Utiliza procesamiento paralelo con hasta 5 workers simultáneos
- Implementa anti-detección para evitar bloqueos del sitio
- Maneja expansión dinámica de contenido con JavaScript
- Incluye recuperación de errores y logging detallado
- Compatible con estructura VTEX de Vea