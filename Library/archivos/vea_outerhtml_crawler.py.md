# Desglose de Archivo: vea_outerhtml_crawler.py

## Propósito
Este archivo implementa un crawler para extraer outerHTML completo de páginas clave del sitio web de Vea. Forma parte de la fase inicial de desarrollo de scrapers, permitiendo análisis offline de selectores CSS, estructura DOM y metadata para el desarrollo posterior de scrapers específicos. Basado en la implementación de Jumbo con vault system integrado.

## Relaciones
- **Ubicación**: `src/backend/src/scripts/scrapers/vea/HTML/vea_outerhtml_crawler.py`
- **Dependencias**: Selenium WebDriver con Edge
- **Salida**: Archivos HTML en `vea/HTML/` con timestamps
- **Vault**: Sistema de versionado que mantiene máximo 2 versiones por página
- **Integración**: Parte del flujo de desarrollo outerHTML → Supermarket Info → Categories → etc.

## Recreación
1. **Crear directorio**: `src/backend/src/scripts/scrapers/vea/HTML/`
2. **Crear vault**: Subdirectorio `vault/` para versiones antiguas
3. **Implementar funciones**:
   - `clean_vault()`: Mantiene solo 2 versiones recientes por page_name
   - `extract_outerhtml()`: Navega a URL, extrae outerHTML, guarda con timestamp y gestiona vault
   - `crawl_vea()`: Orquesta extracción de todas las páginas
4. **Configurar URLs**: 6 páginas clave con URLs específicas de Vea
5. **Browser setup**: Edge headless con user-agent y opciones anti-detección

## Funcionalidades Clave
- **Headless browsing**: Opera sin interfaz gráfica para eficiencia
- **Error handling**: Captura y reporta errores por página
- **Version control**: Vault system automático con movimiento de archivos antiguos
- **Timestamps**: Nombres de archivo con fecha/hora para tracking
- **Anti-detection**: User-agent y opciones para evitar bloqueos

## Páginas Extraídas
1. **home**: Página principal de Vea (https://www.vea.com.ar/)
2. **categoria_almacen**: Categoría de almacén (https://www.vea.com.ar/almacen)
3. **producto_ejemplo**: Página de producto específico (https://www.vea.com.ar/galletitas-surtido-bagley-400-gr-2/p)
4. **descuentos_dia**: Descuentos del día (https://www.vea.com.ar/descuentos-del-dia?type=por-dia&day=0)
5. **descuentos_banco**: Descuentos bancarios (https://www.vea.com.ar/descuentos-del-dia?type=por-banco)
6. **descuentos_cencopay**: Descuentos Cencosud (https://www.vea.com.ar/descuentos-del-dia?type=cencopay)

## Fecha de Incorporación
Septiembre 2025

## Feature Asociada
Feature 9: OuterHTML Scraper Vea

## Notas Técnicas
- **Browser**: Microsoft Edge (Chromium-based)
- **Driver**: WebDriver automático
- **Encoding**: UTF-8 para soporte de caracteres especiales
- **Timeouts**: time.sleep(5) para carga completa de páginas
- **Error recovery**: Driver cleanup en caso de excepciones
- **Vault System**: Mantiene máximo 2 versiones por página, elimina archivos antiguos automáticamente