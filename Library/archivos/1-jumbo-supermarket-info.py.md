# Desglose de Archivo: 1-vea-supermarket-info.py

## Propósito
Este archivo implementa un scraper completo para extraer metadatos del supermercado Vea desde su página web principal. Extrae información básica, plataforma técnica, analytics, información legal, configuración PWA y consentimiento de cookies, guardando los datos en la base de datos MongoDB Atlas específica para Vea.

## Relaciones con Otros Archivos
- **Dependencias**: Utiliza `python-dotenv` para cargar variables de entorno desde `.env`
- **Base de datos**: Se conecta a la base de datos `vea` en MongoDB Atlas usando `MONGO_VEA_URI`
- **Colección**: Guarda datos en la colección `supermarket-info`
- **Relacionado con**: Scripts similares para otros supermercados (Disco, Jumbo) con estructura idéntica
- **HTML Source**: Utiliza archivos HTML guardados en `src/backend/src/scripts/scrapers/vea/HTML/` para análisis offline

## Recreación
1. **Ubicación**: Crear archivo en `src/backend/src/scripts/scrapers/vea/1-vea-supermarket-info.py`
2. **Dependencias**: Instalar `pymongo`, `selenium`, `colorama`, `python-dotenv`, `requests`
3. **Configuración**:
   - Configurar variable de entorno `MONGO_VEA_URI` apuntando a base de datos `vea`
   - Asegurar que Edge WebDriver esté disponible
4. **Estructura de Clase**:
   - Clase `VeaSupermarketInfoScraper` con métodos para cada tipo de extracción
   - Métodos principales: `extract_basic_info()`, `extract_platform_info()`, `extract_analytics_info()`, etc.
5. **URLs Específicas**:
   - Base URL: `https://www.vea.com.ar`
   - Logo URL: `https://veaargentina.vtexassets.com/assets/vtex.file-manager-graphql/images/5ec9e355-3673-4a62-9cac-16709ca901b6___e6e35cab9242ab53d3f188a1069e3bf8.png`
6. **Campos de Datos**:
   - Información geográfica: País ARG, Idioma es-AR, Moneda ARS
   - Plataforma: VTEX con versión detectada automáticamente
   - Analytics: Google Analytics, Tag Manager, Facebook Pixel, etc.
7. **Ejecución**: Ejecutar con `python 1-vea-supermarket-info.py` desde el directorio del script

## Fecha de Incorporación
28 de septiembre de 2025

## Feature Asociada
Implementación de scraper de metadatos para supermercado Vea como parte del sistema de comparación de precios de Caminando Online.</content>
<parameter name="filePath">d:\dev\caminando-onlinev11\Library\archivos\1-vea-supermarket-info.py.md