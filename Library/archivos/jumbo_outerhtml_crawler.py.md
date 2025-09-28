# Desglose de Archivo: jumbo_outerhtml_crawler.py

## Propósito
Este archivo implementa un crawler básico para extraer outerHTML completo de páginas clave del sitio web de Jumbo. Incluye sistema de vault para versionado, manteniendo solo las versiones más recientes en HTML/ y archivando antiguas en vault/. Se utiliza como base para analizar selectores y estructura DOM offline antes de desarrollar scrapers específicos.

## Relaciones
- Ubicado en `src/backend/src/scripts/scrapers/jumbo/`
- Guarda archivos HTML en `src/backend/src/scripts/scrapers/jumbo/HTML/`
- Archiva versiones antiguas en `src/backend/src/scripts/scrapers/jumbo/HTML/vault/`
- No depende de otros archivos; es independiente para extracción inicial
- Preparación para scrapers jerárquicos (Supermarket Info → Categories → etc.)

## Recreación
1. Crear archivo en `src/backend/src/scripts/scrapers/jumbo/jumbo_outerhtml_crawler.py`
2. Importar dependencias: `selenium`, `webdriver_manager`, `os`, `time`, `datetime`, `shutil`
3. Definir función `clean_vault()` para mantener solo 2 versiones por page_name
4. Definir función `extract_outerhtml()` para capturar outerHTML con Selenium:
   - Mover archivos existentes al vault
   - Extraer nuevo outerHTML
   - Llamar a clean_vault() para mantener versiones
5. Crear `crawl_jumbo()` que:
   - Define vault_dir = os.path.join(output_dir, "vault")
   - Crea vault_dir si no existe
   - Configura Edge headless
   - Extrae URLs específicas: home, categoria_almacen, producto_ejemplo, descuentos_dia, descuentos_banco, descuentos_cencopay
6. En `__main__`, definir output_dir como `HTML/` y ejecutar crawl

## Fecha de Incorporación
Septiembre 28, 2025

## Feature Asociada
Desarrollo inicial de scrapers para Jumbo - Fase outerHTML