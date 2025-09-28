# Desglose de Archivo: dia_outerhtml_crawler.py

## Propósito
Este archivo implementa un crawler básico para extraer outerHTML completo de páginas clave del sitio web de Día. Se utiliza como base para analizar selectores y estructura DOM offline antes de desarrollar scrapers específicos.

## Relaciones
- Ubicado en `src/backend/src/scripts/scrapers/dia/`
- Guarda archivos HTML en `src/backend/src/scripts/scrapers/dia/HTML/`
- No depende de otros archivos; es independiente para extracción inicial
- Preparación para scrapers jerárquicos (Supermarket Info → Categories → etc.)

## Recreación
1. Crear archivo en `src/backend/src/scripts/scrapers/dia/dia_outerhtml_crawler.py`
2. Importar dependencias: `selenium`, `webdriver_manager`, `os`, `time`, `datetime`
3. Definir función `extract_outerhtml()` para capturar outerHTML con Selenium
4. Crear `crawl_dia()` que:
   - Configura Edge headless
   - Extrae URLs específicas: home, categoria_almacen, producto_ejemplo, medios_pago_promociones
5. En `__main__`, definir output_dir como `HTML/` y ejecutar crawl

## Fecha de Incorporación
Septiembre 28, 2025

## Feature Asociada
Desarrollo inicial de scrapers para Día - Fase outerHTML