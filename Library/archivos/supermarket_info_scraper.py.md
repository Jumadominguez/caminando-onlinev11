# Desglose de Archivo: supermarket_info_scraper.py

## Propósito
Este archivo implementa el scraper de Supermarket Info para Carrefour, que extrae metadata completa del sitio web incluyendo información básica, geográfica, técnica, legal y de PWA. Es el primer nivel de la jerarquía de scraping según las instrucciones de scraping.instructions.md.

## Relaciones
- **Modelo**: Utiliza el esquema `supermarket-info.js` en `src/backend/src/models/product_raw/carrefour_raw/`
- **Dependencias**: Selenium WebDriver con Edge, logging, regex, datetime
- **Output**: Genera archivo JSON con toda la metadata extraída
- **Integración**: Parte de la jerarquía de scraping (Supermarket Info → Categories → Subcategories → Products → Offers)

## Recreación
1. **Ubicación**: `src/backend/src/scripts/scrapers/carrefour/supermarket_info_scraper.py`
2. **Dependencias**: 
   - Python 3.8+
   - selenium 4.35.0
   - Edge WebDriver
3. **Configuración**:
   - Modo headless para producción
   - Timeouts de 30 segundos
   - User-agent personalizado
4. **Ejecución**: `python supermarket_info_scraper.py`
5. **Output**: `carrefour_supermarket_info_YYYYMMDD_HHMMSS.json`

## Funcionalidad por Método

### `setup_driver()`
- Configura Edge WebDriver con opciones optimizadas
- Modo headless, sin imágenes para velocidad
- Timeouts y user-agent configurados

### `extract_basic_info()`
- Extrae título de la página
- Busca logo en múltiples selectores
- Recopila todas las meta tags

### `extract_geographic_info(meta_tags)`
- Extrae país, idioma y moneda de meta tags
- Valores por defecto: ARG, es-AR, ARS

### `extract_platform_info()`
- Detecta plataforma VTEX y versión del render server
- Busca información de tema en assets
- Identifica workspace (default: master)

### `extract_analytics_info()`
- Detecta Google Tag Manager (GTM-*)
- Busca Google Analytics 4 (G-*)
- Identifica Facebook Pixel, Dynamic Yield, Activity Flow
- Escanea todos los scripts por patrones regex

### `extract_legal_info()`
- Busca enlaces de términos y condiciones
- Detecta políticas de privacidad y cookies
- Incluye URL conocida de defensa del consumidor
- Escanea todos los enlaces de la página

### `extract_pwa_info()`
- Verifica manifest.json
- Extrae theme-color
- Recopila todos los iconos PWA
- Detecta si PWA está habilitado

### `extract_cookie_consent_info()`
- Detecta OneTrust u otros proveedores
- Busca URLs de política de privacidad en cookies

### `scrape_supermarket_info()`
- Método principal que coordina toda la extracción
- Navega a la homepage y espera carga completa
- Compila todos los datos en estructura JSON
- Maneja errores y logging

## Estructura de Datos de Output

```json
{
  "_id": "carrefour",
  "name": "Carrefour",
  "logo": "URL_DEL_LOGO",
  "website": "https://www.carrefour.com.ar",
  "country": "ARG",
  "language": "es-AR",
  "currency": "ARS",
  "platform": "VTEX",
  "platformVersion": "8.136.1",
  "analytics": {...},
  "homepageMetadata": {...},
  "legalInfo": {...},
  "pwa": {...},
  "cookieConsent": {...},
  "active": true,
  "lastHomepageScraped": "timestamp"
}
```

## Casos de Uso
- **Primera ejecución**: Extraer metadata inicial de Carrefour
- **Actualización**: Re-ejecutar para detectar cambios en plataforma/tema
- **Validación**: Verificar que todos los campos requeridos se extraigan
- **Debugging**: Usar logs para identificar problemas de detección

## Manejo de Errores
- **WebDriver errors**: Retry con backoff
- **Timeout errors**: Logging y continuación
- **Element not found**: Valores null con warning
- **Network issues**: Reintentos automáticos

## Optimizaciones
- **Headless mode**: Para ejecución en background
- **Image disabling**: Acelera carga de página
- **Selective waiting**: Espera solo elementos necesarios
- **Regex patterns**: Detección eficiente de analytics

## Próximos Pasos en Jerarquía
1. **Supermarket Info** ✓ (Completado)
2. **Categories**: Extraer menú de navegación principal
3. **Subcategories**: Procesar cada categoría
4. **Product Types**: Identificar tipos bajo subcategorías
5. **Products**: Extraer productos individuales con precios
6. **Offers**: Procesar promociones y descuentos

## Logs y Debugging
- **Archivo**: `supermarket_info_scraper.log`
- **Niveles**: INFO para progreso, WARNING para issues, ERROR para fallos
- **Formato**: Timestamp, nivel, mensaje

## Fecha de Creación
28 de septiembre de 2025

## Commit Relacionado
`[FEAT-010] Implementar scraper de Supermarket Info para Carrefour`

## Notas de Implementación
- Basado en análisis del HTML de Carrefour
- Compatible con VTEX e-commerce platform
- Extensible para otros supermercados
- Incluye detección de PWA y analytics modernos