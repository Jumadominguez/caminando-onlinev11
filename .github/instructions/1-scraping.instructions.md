# Instructivo para Desarrollo de Scrapers de Supermercados

Este documento proporciona guías detalladas y optimizadas para agentes de IA en el desarrollo de scrapers para la plataforma Caminando Online. El enfoque está en extraer datos de productos de 5 supermercados (Carrefour, Dia, Jumbo, Vea, Disco) siguiendo una jerarquía modular, utilizando checkpoints para resiliencia ante fallas, y optimizando el procesamiento con chunks simultáneos para manejar volúmenes exponenciales de datos.

## Introducción

Los scrapers se desarrollan para poblar los modelos de `product_raw` en MongoDB Atlas, organizados por supermercado. Cada scraper extrae datos específicos siguiendo la jerarquía: **Supermarket Info** → **Categories** → **Subcategories** → **Product Types** (con Filters como subsección) → **Products**. Incluye análisis de ofertas y promociones.

**Objetivos Clave**:
- Resiliencia: Checkpoints en cada avance significativo para revertir fallas.
- Eficiencia: Procesamiento por chunks en sesiones simultáneas para reducir tiempos.
- Sigilo: Evitar detección como bot mediante técnicas anti-detección.
- Automatización: Scrapers diarios para mantener datos actualizados.
- Futuro: Integración con dashboard GUI para control granular.

**Browser**: Mozilla Firefox (instalado y configurado en el entorno).

## Arquitectura de Datos y Jerarquía

Los datos se almacenan en bases de datos separadas por supermercado (e.g., `carrefour`, `dia`) bajo el esquema `product_raw`. La jerarquía es estricta:

1. **Supermarket Info**: Metadatos del sitio.
2. **Categories**: Categorías principales.
3. **Subcategories**: Subcategorías bajo categorías.
4. **Product Types**: Tipos específicos bajo subcategorías.
4.1. **Filters**: Son una subsección de Product Types.
5. **Products**: Productos individuales. Incluye precios, ofertas y promociones.
6. **Offers**: Detalles de promociones específicas. Se debe luego aplicar a cada producto que corresponda segun lo definido en el sitio web del supermercado.

Cada nivel depende del anterior. Los scrapers deben validar dependencias antes de procesar.

## Uso Efectivo de Sandbox

Sigue las reglas de `sandbox.instructions.md` para desarrollo iterativo:

- **Experiments**: Desarrolla y prueba scrapers iniciales aquí. Crea versiones experimentales, prueba selectores y lógica.
- **Debug**: Aísla y resuelve problemas. Registra logs, scripts de diagnóstico y versiones temporales.
- **Prototypes**: Valida scrapers completados antes de integración. Prueba con datos reales y mide rendimiento. Guarda versiones funcionales antes de intentar modificaciones nuevas en experiments.
- **Temps**: Archivos temporales como screenshots, reportes de debug o versiones simplificadas. Limpia periódicamente.
- **Vault**: Backup de código viejo. Excluido de Git.

**Flujo**:
1. Desarrolla en `Experiments/`.
2. Depura en `Debug/`.
3. Valida en `Prototypes/`.
4. Integra a `src/backend/src/scripts/scrapers/{supermercado}/` solo tras aprobación.
5. Documenta en `Library/archivos/` y actualiza `proceso.md`.

## Desarrollo Inicial: Scraper de OuterHTML

Antes de scrapers específicos, desarrolla un script para extraer y almacenar outerHTML completos de páginas clave. Esto permite análisis offline de elementos, selectores y metadata.

**Propósito**: Capturar snapshots completos de páginas para referencia constante, evitando requests repetidos y facilitando debugging.

**Ubicación**: `src/backend/src/scripts/scrapers/{supermercado}/HTML/`.

**Funcionalidad**:
- Navega a URLs clave (home, categorías, subcategorías, etc.).
- Extrae `document.documentElement.outerHTML` completo.
- Guarda en archivos `.html` con timestamps (e.g., `home_20250928.html`).
- Incluye metadata (headers, cookies, user-agent).
- Ejecuta periódicamente para detectar cambios en DOM.

**Implementación**:
- Usa Selenium con Firefox.
- Configura headless para eficiencia.
- Maneja errores de carga y timeouts.
- Almacena en carpetas por tipo de página (e.g., `HTML/categories/`, `HTML/products/`).

**Checkpoint**: Commit después de cada sitio completado.

## Orden de Desarrollo de Scrapers

Desarrolla scrapers por nivel, completando todos los 5 supermercados antes de pasar al siguiente. Usa los archivos HTML guardados por el scraper de outerHTML como base para identificar los selectores.

1. **Supermarket Info** (1 por supermercado):
   - Extrae metadatos: nombre, URL base, logo, políticas.
   - Modelo: `supermarket-info.js`.

2. **Categories**:
   - Extrae categorías principales desde el menu desplegable de la home.
   - En Carrefour y Dia, el menu desplegable se activa con "Click". En Jumbo, Vea y Disco, el menu desplegable se activa con "Hover".
   - Modelo: `Category.js`.
   - Depende de: Supermarket Info.

3. **Subcategories**:
   - Extrae subcategorías bajo cada categoría.
   - Modelo: `Subcategory.js`.
   - Depende de: Categories.

4. **Product Types**:
   - Extrae tipos de producto bajo subcategorías.
   - Incluye Filters como subsección integrada.
   - Modelo: `ProductType.js` y `Filter.js`.
   - Depende de: Subcategories.

5. **Products**:
   - Extrae productos individuales con precios, ofertas y promociones.
   - Analiza promociones específicas del sitio.
   - Modelo: `Product.js`, `Offer.js`, `PriceHistory.js`.
   - Depende de: Product Types.

6. **Offers**:
   - Extrae detalles de promociones específicas.
   - Aplica ofertas a productos correspondientes según reglas del sitio web.
   - Modelo: `Offer.js`.
   - Depende de: Products.

**Por niveles**: Completa el ciclo completo para un nivel antes de pasar a la siguiente (e.g., el script de Supermarket-info para los 5 supermercados antes de pasar al de categoría. El scraper de categorías para los 5 supermercados antes de pasar al de subcategorías.).

## Manejo de Checkpoints

Dado el alto riesgo de fallas (bloqueos, cambios en DOM, timeouts), implementa checkpoints en cada avance significativo.

**Estrategia**:
- **Frecuencia**: Después de procesar cada chunk, categoría o subcategoría completa y que el usuario haya confirmado que el script funciona correctamente.
- **Formato**: Guarda estado en JSON (e.g., `checkpoint_{nivel}_{timestamp}.json`) con progreso, datos extraídos y errores.
- **Ubicación**: `Sandbox/Debug/` para temporales; `Vault/` para backups.
- **Recuperación**: Script debe cargar último checkpoint al reiniciar, saltando datos ya procesados.
- **Commits**: Usa formato `[CHECKPOINT-NNN] Avance en scraper {nivel} para {supermercado}`. Actualiza `docs/commit-counter.txt`.

**Ejemplo**: Si falla en subcategoría 50/400, checkpoint permite reanudar desde ahí.

## Procesamiento por Chunks y Sesiones Simultáneas

Para manejar volúmenes exponenciales, divide el trabajo en chunks procesados en paralelo.

**Chunks**:
- Divide listas grandes (e.g., 3600 product types en chunks de 300).
- Asigna chunks a sesiones simultáneas.

**Sesiones Simultáneas**:
- Abre múltiples instancias de Firefox (e.g., 10 sesiones).
- Cada sesión procesa su chunk (e.g., Sesión 1: items 1-300, Sesión 2: 301-600).
- Usa threading/multiprocessing en Python para coordinación.
- Limita concurrencia para evitar sobrecarga (máx. 5-10 sesiones).

**Optimización**:
- Monitorea tiempos; ajusta chunk size dinámicamente.
- Pool de conexiones para reutilizar sesiones.
- Logging detallado por sesión.

## Evitar Detección como Bot

Aplica técnicas para simular navegación humana y evitar bloqueos.

**Técnicas**:
- **User-Agent Rotativo**: Cambia user-agent por sesión.
- **Delays Aleatorios**: Pausas entre requests (1-5 segundos).
- **Headless Variable**: Alterna entre headless y visible.
- **Cookies y Sesiones**: Mantén cookies para simular usuario logueado.
- **Proxy Rotativo**: Si disponible, rota IPs.
- **JavaScript Execution**: Ejecuta JS para cargar contenido dinámico.
- **CAPTCHA Handling**: Detecta y pausa para intervención manual si es necesario.
- **Rate Limiting**: Limita requests por minuto por sesión.

**Herramientas**: Selenium con Firefox, undetected-chromedriver si es necesario, pero prioriza Firefox.

## Configuración del Browser

- **Browser**: Mozilla Firefox.
- **Driver**: GeckoDriver (instalado en entorno).
- **Opciones**: 
  - `--headless` para producción.
  - `--disable-blink-features=AutomationControlled`.
  - `--user-agent` personalizado.
- **Perfil**: Crea perfiles temporales por sesión para aislamiento.

## Automatización Diaria

Una vez completados, configura scrapers para ejecución automática diaria.

**Mecanismo**:
- Usa cron jobs o scheduler (e.g., APScheduler en Python).
- Ejecuta a horas de bajo tráfico (e.g., 2 AM).
- Compara con datos existentes; actualiza solo cambios.
- Logs y alertas para fallos o productos removidos en los sitios webs de los supermercados.

**Integración**: Scripts en `scripts/` con triggers automáticos.

## Futuro: Dashboard GUI

Desarrolla un dashboard para control granular.

**Funcionalidades**:
- Seleccionar supermercado, categoría, subcategoría, etc., para scraping específico.
- Monitoreo en tiempo real de progreso y errores.
- Triggers manuales y automáticos.
- Visualización de datos extraídos.

**Tecnologías**: Web app simple (React/Express) integrada con scripts.

## Mejores Prácticas y Consideraciones Adicionales

- **Modularidad**: Scripts separados por nivel y supermercado.
- **Logging**: Usa logging detallado (niveles: DEBUG, INFO, ERROR) en archivos por sesión.
- **Error Handling**: Retry con backoff exponencial; skip elementos problemáticos.
- **Validación**: Verifica datos contra esquemas antes de insertar en DB.
- **Seguridad**: No almacena credenciales; sigue `seguridad.instructions.md`.
- **Performance**: Optimiza selectores CSS/XPath; evita full page loads innecesarios.
- **Documentación**: Actualiza `Library/archivos/` con desgloses de cada scraper.
- **Testing**: Prueba en `Sandbox/Experiments/` con datos mock antes de producción.
- **Actualización**: Revisa selectores periódicamente; usa outerHTML para detectar cambios.
- **Colaboración**: Comparte checkpoints y logs para debugging colaborativo.

Este instructivo asegura desarrollo eficiente y resiliente. Actualiza según evolucione el proyecto.