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

## Próximas Features Planificadas
1. Scraper de Supermarket Info para Carrefour
2. Scraper de Categories para Carrefour
3. Expansión a otros supermercados (Dia, Jumbo, Vea, Disco)
4. Implementación de checkpoints y procesamiento por chunks
5. Scrapers jerárquicos completos con anti-detección

## Notas Adicionales
- Browser utilizado: Microsoft Edge (Chromium-based) por disponibilidad
- Patrón: OuterHTML first para análisis offline de selectores
- Arquitectura: Jerarquía Supermarket → Categories → Subcategories → Products → Offers
- Anti-detección: Headless mode, user-agent rotation, delays implementados