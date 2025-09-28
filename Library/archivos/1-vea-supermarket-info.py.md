# Desglose de Archivo: 1-jumbo-supermarket-info.py

## Propósito
Este archivo implementa un scraper completo para extraer metadatos del supermercado Jumbo desde su página web principal. Extrae información básica, plataforma técnica, analytics, información legal, configuración PWA y consentimiento de cookies, guardando los datos en la base de datos MongoDB Atlas específica para Jumbo.

## Relaciones con Otros Archivos
- **Dependencias**: Utiliza `python-dotenv` para cargar variables de entorno desde `.env`
- **Base de datos**: Se conecta a la base de datos `jumbo` en MongoDB Atlas usando `MONGO_JUMBO_URI`
- **Colección**: Guarda datos en la colección `supermarket-info`
- **Relacionado con**: Scripts similares para otros supermercados (Disco, Vea) con estructura idéntica
- **HTML Source**: Utiliza archivos HTML guardados en `src/backend/src/scripts/scrapers/jumbo/HTML/` para análisis offline

## Recreación
1. **Ubicación**: Crear archivo en `src/backend/src/scripts/scrapers/jumbo/1-jumbo-supermarket-info.py`
2. **Dependencias**: Instalar `pymongo`, `selenium`, `colorama`, `python-dotenv`, `requests`
3. **Configuración**:
   - Configurar variable de entorno `MONGO_JUMBO_URI` apuntando a base de datos `jumbo`
   - Asegurar que Edge WebDriver esté disponible
4. **Estructura de Clase**:
   - Clase `JumboSupermarketInfoScraper` con métodos para cada tipo de extracción
   - Métodos principales: `extract_basic_info()`, `extract_platform_info()`, `extract_analytics_info()`, etc.
5. **URLs Específicas**:
   - Base URL: `https://www.jumbo.com.ar`
   - Logo URL: `https://jumboargentinaio.vtexassets.com/assets/vtex.file-manager-graphql/images/bd790034-1117-4263-90e5-04f3f5a27503___ab950355900559ccc0bc0cb131364561.png`
6. **Campos de Datos**:
   - Información geográfica: País ARG, Idioma es-AR, Moneda ARS
   - Plataforma: VTEX con versión detectada automáticamente
   - Analytics: Google Analytics, Tag Manager, Facebook Pixel, etc.
7. **Ejecución**: Ejecutar con `python 1-jumbo-supermarket-info.py` desde el directorio del script

## Fecha de Incorporación
28 de septiembre de 2025

## Feature Asociada
Implementación de scraper de metadatos para supermercado Jumbo como parte del sistema de comparación de precios de Caminando Online.</content>
<parameter name="filePath">d:\dev\caminando-onlinev11\Library\archivos\1-jumbo-supermarket-info.py.md