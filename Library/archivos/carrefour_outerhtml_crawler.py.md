# Desglose de Archivo: carrefour_outerhtml_crawler.py

## Propósito
Este archivo implementa un crawler básico para extraer outerHTML completo de páginas clave del sitio web de Carrefour. Incluye sistema de vault para versionado, manteniendo solo las versiones más recientes en HTML/ y archivando antiguas en vault/. Se utiliza como base para analizar selectores y estructura DOM offline antes de desarrollar scrapers específicos.

## Relaciones
- Ubicado en `src/backend/src/scripts/scrapers/carrefour/`
- Guarda archivos HTML en `src/backend/src/scripts/scrapers/carrefour/HTML/`
- Archiva versiones antiguas en `src/backend/src/scripts/scrapers/carrefour/HTML/vault/`
- No depende de otros archivos; es independiente para extracción inicial
- Preparación para scrapers jerárquicos (Supermarket Info → Categories → etc.)

## Recreación
1. Crear archivo en `src/backend/src/scripts/scrapers/carrefour/carrefour_outerhtml_crawler.py`
2. Importar dependencias: `selenium`, `webdriver_manager`, `os`, `time`, `datetime`, `shutil`
3. Definir función `clean_vault()` para mantener solo 2 versiones por page_name
4. Definir función `extract_outerhtml()` para capturar outerHTML con Selenium:
   - Mover archivos existentes al vault
   - Extraer nuevo outerHTML
   - Llamar a clean_vault() para mantener versiones
5. Implementar `find_links()` para encontrar enlaces por patrones
6. Crear `crawl_carrefour()` que:
   - Define vault_dir = os.path.join(output_dir, "vault")
   - Crea vault_dir si no existe
   - Configura Edge headless
   - Extrae URLs específicas con vault system
7. En `__main__`, definir output_dir como `HTML/` y ejecutar crawl

## Fecha de Incorporación
Septiembre 28, 2025

## Feature Asociada
Sistema de vault para versionado de HTMLs - Feature 3