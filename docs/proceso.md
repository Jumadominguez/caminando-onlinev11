# Proceso de Desarrollo - Caminando Onl#### Testing
- Ejecución exitosa con generación de 5 archivos HTML
- Validación de outerHTML completo (1.2MB+ por página)
- Verificación de timestamps y nomenclatura de archivosV11

## Fecha de Inicio
Septiembre 28, 2025

## Fase Actual
Desarrollo de Scrapers - OuterHTML Extraction

## Resumen del Proceso
Este documento registra el proceso completo de desarrollo de features aprobadas en el proyecto Caminando Online. Cada feature incluye fases desde experimentación hasta integración final.

## Features Desarrolladas

### Feature 1: Scraper de OuterHTML para Carrefour
**Fecha de Aprobación**: Septiembre 28, 2025

#### Fase de Experimentación (Sandbox/Experiments/)
- Desarrollo inicial con Firefox (fallido por no disponibilidad)
- Adaptación a Edge con WebDriver Manager
- Creación de script básico para extracción de home page
- Pruebas de funcionalidad y validación de outerHTML

#### Fase de Debugging (Sandbox/Debug/)
- Resolución de problemas con ChromeDriver version mismatch
- Ajustes en delays y waits para carga de páginas
- Logging de errores para identificación de issues

#### Fase de Prototipado (Sandbox/Prototypes/)
- Desarrollo de crawler avanzado con identificación automática de páginas
- Integración de URLs específicas proporcionadas por usuario
- Intentos de interacción con menú desplegable y sidebar
- Validación de extracción de múltiples páginas (home, categorías, productos)

#### Integración Final
- Movimiento del script a `src/backend/src/scripts/scrapers/carrefour/carrefour_outerhtml_crawler.py`
- Configuración de output_dir a carpeta `HTML/`
- Creación de documentación en `Library/archivos/carrefour_outerhtml_crawler.py.md`
- Preparación para scrapers jerárquicos siguientes

#### Testing
- Ejecución exitosa en terminal con generación de 5+ archivos HTML
- Validación de outerHTML completo (1.2MB+ por página)
- Verificación de timestamps y nomenclatura de archivos

#### Documentación
- Actualización de `proceso.md` con registro completo
- Documento de desglose del archivo creado
- Registro en `Library/archivos/`

### Feature 2: Scraper de OuterHTML para Día
**Fecha de Aprobación**: Septiembre 28, 2025

#### Fase de Experimentación (Sandbox/Experiments/)
- Desarrollo basado en script de Carrefour
- Adaptación de URLs específicas para Día
- Configuración de base_url para diaonline.supermercadosdia.com.ar

#### Fase de Prototipado (Sandbox/Prototypes/)
- Creación de crawler simplificado con URLs directas
- Extracción de home, categoría almacen, producto ejemplo

#### Integración Final
- Movimiento del script a `src/backend/src/scripts/scrapers/dia/dia_outerhtml_crawler.py`
- Creación de carpeta `HTML/` para archivos generados
- Creación de documentación en `Library/archivos/dia_outerhtml_crawler.py.md`

#### Testing
- Ejecución exitosa con extracción de 3 archivos HTML
- Validación de outerHTML completo para cada página
- Verificación de funcionamiento en producción

#### Documentación
- Actualización de `proceso.md` con registro completo
- Documento de desglose del archivo creado

### Feature 3: Sistema de Vault para Versionado de HTMLs
**Fecha de Aprobación**: Septiembre 28, 2025

#### Fase de Experimentación (Sandbox/Experiments/)
- Diseño del sistema de versionado para mantener versiones recientes de HTMLs
- Creación de función clean_vault() para mantener solo 2 versiones por página
- Implementación de lógica de movimiento de archivos antiguos al vault

#### Fase de Prototipado (Sandbox/Prototypes/)
- Integración del vault en scripts de Carrefour y Día
- Pruebas de movimiento de archivos y limpieza automática
- Validación de que solo se mantienen versiones recientes en HTML/

#### Integración Final
- Actualización de `carrefour_outerhtml_crawler.py` con vault system
- Actualización de `dia_outerhtml_crawler.py` con vault system
- Creación de carpetas `vault/` en ambas estructuras HTML/
- Modificación de extract_outerhtml() para incluir vault_dir parameter

#### Testing
- Ejecución exitosa con movimiento automático de archivos antiguos
- Validación de que vault mantiene máximo 2 versiones por page_name
- Verificación de que HTML/ contiene solo las versiones más recientes

#### Documentación
- Actualización de `proceso.md` con registro completo
- Commit [FEAT-003] con cambios implementados

### Feature 4: OuterHTML Scraper para Disco
**Fecha de Aprobación**: Septiembre 28, 2025

#### Fase de Experimentación (Sandbox/Experiments/)
- Desarrollo basado en scripts de Carrefour y Día
- Adaptación de URLs específicas para Disco
- Configuración de base_url para disco.com.ar

#### Fase de Prototipado (Sandbox/Prototypes/)
- Creación de crawler simplificado con URLs directas
- Extracción de home, categoría almacen, producto ejemplo
- Integración del vault system desde el inicio

#### Integración Final
- Movimiento del script a `src/backend/src/scripts/scrapers/disco/disco_outerhtml_crawler.py`
- Creación de carpeta `HTML/` para archivos generados
- Creación de carpeta `vault/` para versionado
- Creación de documentación en `Library/archivos/disco_outerhtml_crawler.py.md`

#### Testing
- Ejecución exitosa con extracción de 6 archivos HTML
- Validación de outerHTML completo para cada página
- Verificación de funcionamiento del vault system

#### Documentación
- Actualización de `proceso.md` con registro completo
- Documento de desglose del archivo creado

### Feature 5: Eliminación de Páginas de Ofertas
**Fecha de Aprobación**: Septiembre 28, 2025

#### Fase de Experimentación (Sandbox/Experiments/)
- Identificación de URLs de ofertas inválidas en todos los supermercados
- Verificación de que {supermercado}.com.ar/ofertas no existe para ninguno

#### Fase de Prototipado (Sandbox/Prototypes/)
- Eliminación de entradas "ofertas", "promociones", "medios_pago_promociones" de todos los diccionarios specific_urls
- Actualización de scripts de Carrefour, Día y Disco para extraer solo 3 páginas: home, categoria_almacen, producto_ejemplo

#### Integración Final
- Modificación de `carrefour_outerhtml_crawler.py`, `dia_outerhtml_crawler.py`, `disco_outerhtml_crawler.py`
- Actualización de documentación en `Library/archivos/` para todos los scripts
- Actualización de `proceso.md` con cambios

#### Testing
- Verificación de que los scripts ahora extraen solo 3 archivos HTML por supermercado
- Validación de funcionamiento correcto sin errores

#### Documentación
- Actualización de `proceso.md` con registro completo
- Commit [FEAT-005] con cambios implementados

### Feature 6: Páginas Adicionales Carrefour
**Fecha de Aprobación**: Septiembre 28, 2025

#### Fase de Experimentación (Sandbox/Experiments/)
- Identificación de URLs adicionales útiles para Carrefour
- Verificación de existencia de páginas de promociones y descuentos bancarios

#### Fase de Prototipado (Sandbox/Prototypes/)
- Agregar URLs de promociones y descuentos bancarios al diccionario specific_urls
- Verificar funcionamiento correcto de las nuevas URLs

#### Integración Final
- Actualización de `carrefour_outerhtml_crawler.py` con 5 páginas en total
- Testing de funcionamiento con vault system

#### Testing
- Ejecución exitosa con extracción de 5 archivos HTML
- Validación de vault system manteniendo versiones
- Verificación de funcionamiento de todas las URLs

#### Documentación
- Actualización de `proceso.md` con registro completo
- Commit [FEAT-006] con cambios implementados

### Feature 7: Páginas de Descuentos Disco
**Fecha de Aprobación**: Septiembre 28, 2025

#### Fase de Experimentación (Sandbox/Experiments/)
- Identificación de URLs de descuentos específicas para Disco
- Verificación de existencia de páginas de descuentos por día, banco y CencoPay

#### Fase de Prototipado (Sandbox/Prototypes/)
- Agregar URLs de descuentos al diccionario specific_urls
- Verificar funcionamiento correcto de las nuevas URLs

#### Integración Final
- Actualización de `disco_outerhtml_crawler.py` con 6 páginas en total
- Testing de funcionamiento con vault system

#### Testing
- Ejecución exitosa con extracción de 6 archivos HTML
- Validación de vault system manteniendo versiones
- Verificación de funcionamiento de todas las URLs de descuentos

#### Documentación
- Actualización de `proceso.md` con registro completo
- Commit [FEAT-007] con cambios implementados

### Feature 8: OuterHTML Scraper Jumbo
**Fecha de Aprobación**: Septiembre 28, 2025

#### Fase de Experimentación (Sandbox/Experiments/)
- Desarrollo basado en scripts de Carrefour, Día y Disco
- Adaptación de URLs específicas para Jumbo
- Configuración de base_url para jumbo.com.ar

#### Fase de Prototipado (Sandbox/Prototypes/)
- Creación de crawler con URLs directas incluyendo descuentos
- Extracción de home, categoría almacen, producto ejemplo y páginas de descuentos
- Integración del vault system desde el inicio

#### Integración Final
- Movimiento del script a `src/backend/src/scripts/scrapers/jumbo/jumbo_outerhtml_crawler.py`
- Creación de carpeta `HTML/` para archivos generados
- Creación de carpeta `vault/` para versionado

#### Testing
- Ejecución exitosa con extracción de 6 archivos HTML
- Validación de outerHTML completo para cada página
- Verificación de funcionamiento del vault system

#### Documentación
- Actualización de `proceso.md` con registro completo
- Documento de desglose del archivo creado

### Feature 9: OuterHTML Scraper Vea
**Fecha de Aprobación**: Septiembre 28, 2025

#### Fase de Experimentación (Sandbox/Experiments/)
- Desarrollo basado en patrón establecido por Carrefour, Día, Disco y Jumbo
- Configuración de URLs específicas para vea.com.ar
- Implementación del vault system desde el inicio

#### Fase de Prototipado (Sandbox/Prototypes/)
- Creación de crawler con 6 páginas clave incluyendo descuentos
- URLs: home, categoria_almacen, producto_ejemplo, descuentos_dia, descuentos_banco, descuentos_cencopay
- Integración completa del sistema de vault

#### Integración Final
- Movimiento del script a `src/backend/src/scripts/scrapers/vea/HTML/vea_outerhtml_crawler.py`
- Creación de directorios `HTML/` y `vault/`
- Configuración de output_dir y vault_dir

#### Testing
- Script creado y configurado correctamente
- Estructura de directorios preparada
- Sistema de vault implementado

#### Documentación
- Actualización de `proceso.md` con registro completo
- Documento de desglose del archivo creado

### Feature 2: Scrapers de Supermarket Info para Jumbo y Vea
**Fecha de Aprobación**: Septiembre 28, 2025

#### Fase de Experimentación (Sandbox/Experiments/)
- Análisis del script base de Disco para replicación
- Identificación de URLs específicas de logos para cada supermercado
- Adaptación de URLs base (jumbo.com.ar, vea.com.ar)
- Configuración de conexiones MongoDB específicas (jumbo, vea)

#### Fase de Debugging (Sandbox/Debug/)
- Verificación de dependencias Python (pymongo, selenium, etc.)
- Configuración de entorno virtual y variables de entorno
- Testing de conexiones MongoDB Atlas
- Ajustes en timeouts para diferentes sitios web

#### Fase de Prototipado (Sandbox/Prototypes/)
- Creación de scripts idénticos basados en estructura de Disco
- Personalización de URLs y configuraciones específicas
- Validación de extracción de datos para cada supermercado
- Testing de guardado en bases de datos respectivas

#### Integración Final
- Movimiento de scripts a directorios respectivos:
  - `src/backend/src/scripts/scrapers/jumbo/1-jumbo-supermarket-info.py`
  - `src/backend/src/scripts/scrapers/vea/1-vea-supermarket-info.py`
- Configuración de variables de entorno MONGO_JUMBO_URI y MONGO_VEA_URI
- Creación de documentación en `Library/archivos/`
- Actualización de `registro-archivos.md`

#### Testing
- Ejecución exitosa de ambos scripts en terminal
- Validación de conexión MongoDB Atlas
- Verificación de extracción completa de metadatos
- Confirmación de guardado en colecciones respectivas

#### Documentación
- Creación de documentos de desglose para ambos scripts
- Actualización de `registro-archivos.md` con nuevas entradas
- Actualización de `proceso.md` con registro completo

## Próximas Features Planificadas
1. Scraper de Supermarket Info para Carrefour ✅ Completado
2. Scraper de Supermarket Info para Dia
3. Scraper de Supermarket Info para Disco ✅ Completado
4. Scraper de Supermarket Info para Jumbo ✅ Completado
5. Scraper de Supermarket Info para Vea ✅ Completado
6. Scraper de Categories para Carrefour
7. Implementación de checkpoints y procesamiento por chunks
8. Scrapers jerárquicos completos con anti-detección

## Notas Adicionales
- Browser utilizado: Microsoft Edge (Chromium-based) por disponibilidad
- Patrón: OuterHTML first para análisis offline de selectores
- Arquitectura: Jerarquía Supermarket → Categories → Subcategories → Products → Offers
- Anti-detección: Headless mode, user-agent rotation, delays implementados