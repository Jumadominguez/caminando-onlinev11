# Proceso de Scraping de Subcategorías - Carrefour

## Fecha: Septiembre 29, 2025
## Versión: 1.0
## Autor: GitHub Copilot (Vibe Coding)

## Introducción

Este documento detalla el proceso de scraping de subcategorías para el supermercado Carrefour en la plataforma Caminando Online. El enfoque está en eficiencia, resiliencia y modularidad, siguiendo las instrucciones de `scraping.instructions.md` y trabajando en el entorno Sandbox.

## Objetivos

- Extraer todas las subcategorías disponibles para cada categoría existente en la base de datos.
- Implementar navegación eficiente con expansión de filtros dinámicos.
- Optimizar tiempos de ejecución y reducir detección como bot.
- Preparar datos para el siguiente nivel (Product Types).

## Arquitectura y Flujo

### 1. Obtención de Categorías desde Base de Datos

**Paso 1.1**: Conectar a la base de datos `carrefour` en MongoDB Atlas.
- Usar conexión específica: `global.databaseConnections.carrefour`
- Consultar colección `categories` para obtener todas las categorías activas.
- Campos requeridos: `name`, `slug`, `url` (o generar URL si no existe).

**Paso 1.2**: Generar URLs de categorías.
- Patrón URL: `https://www.carrefour.com.ar/{categoria-slug}`
- Validar URLs antes de navegación.

### 2. Navegación y Expansión de Filtros

**Paso 2.1**: Inicializar navegador Firefox (no headless para debugging).
- Configuración: User-agent rotativo, delays mínimos, sin headless.
- Navegar a URL de categoría.

**Paso 2.2**: Localizar y expandir filtro "Sub-Categoría".
- Selector CSS del contenedor principal:
  ```
  div.valtech-carrefourar-search-result-3-x-filter__container.bb.b--muted-4.valtech-carrefourar-search-result-3-x-filter__container--category-3
  ```
- Dentro de este contenedor, localizar el botón de expansión:
  ```
  div[role="button"][tabindex="0"].pointer.outline-0
  ```
- Contenedor padre del filtro:
  ```
  div.valtech-carrefourar-search-result-3-x-filtersContainer > div.valtech-carrefourar-search-result-3-x-filtersWrapper > div.valtech-carrefourar-search-result-3-x-filter__container.valtech-carrefourar-search-result-3-x-filter__container--title.bb.b--muted-4
  ```

**Paso 2.3**: Hacer scroll y expandir completamente.
- Una vez expandido, localizar el contenedor de subcategorías.
- Hacer scroll hasta el final del contenedor para cargar todas las opciones.
- Localizar botón "Ver más":
  ```
  button.valtech-carrefourar-search-result-3-x-seeMoreButton.mt2.pv2.bn.pointer.c-link.outline-0
  ```
- Clickear el botón para expandir todas las subcategorías.

### 3. Extracción de Datos

**Paso 3.1**: Una vez expandido, extraer lista de subcategorías.
- Selector para elementos de subcategoría:
  ```css
  label.vtex-checkbox__label.w-100.c-on-base.pointer
  ```
- Para cada subcategoría encontrada, extraer el texto del label excluyendo el span de cantidad:
  ```javascript
  // Ejemplo: "Aceites comunes (13)" → "Aceites comunes"
  const fullText = labelElement.textContent;
  const name = fullText.replace(/\s*\(\d+\)\s*$/, '').trim();
  ```
- Extraer todos los campos disponibles del modelo Subcategory.js:
  - `name`: Nombre de la subcategoría (texto limpio sin cantidad)
  - `slug`: Generar automáticamente desde el name (método `generateSlug()`)
  - `url`: Generar automáticamente como `/productos/{category-slug}/{subcategory-slug}`
  - `displayName`: Usar el mismo valor que `name`
  - `category`: Slug de la categoría padre (obtenido de la URL actual)
  - `priority`: 0 por defecto (orden alfabético o por aparición)
  - `active`: true por defecto
  - `featured`: false por defecto
  - `metadata.productCount`: Extraer del span si está disponible (ej: "13" de "(13)")
  - `metadata.productTypeCount`: 0 por defecto (se completará en nivel siguiente)
  - `metadata.lastUpdated`: Timestamp actual
  - `createdAt` y `updatedAt`: Timestamps automáticos

**Paso 3.2**: Cargar la información extraída en la colección `subcategories`.
- **Antes de procesar**: Obtener todas las subcategorías existentes para esta categoría:
  ```javascript
  const existingSubcategories = await db.collection('subcategories')
    .find({ category: categorySlug, active: true })
    .project({ slug: 1, _id: 0 })
    .toArray();
  const existingSlugs = new Set(existingSubcategories.map(s => s.slug));
  ```
- Para cada subcategoría extraída, crear/actualizar documento con `featured: true`:
  ```javascript
  const subcategoryDoc = {
    name: extractedName,
    slug: generateSlug(extractedName),
    url: `/productos/${categorySlug}/${generateSlug(extractedName)}`,
    displayName: extractedName,
    category: categorySlug,
    priority: index,
    active: true,
    featured: true, // Siempre true cuando se extrae/en encuentra
    metadata: {
      productCount: extractedCount || 0,
      productTypeCount: 0,
      lastUpdated: new Date()
    }
  };

  const result = await db.collection('subcategories').updateOne(
    { slug: subcategoryDoc.slug, category: categorySlug },
    { $set: subcategoryDoc },
    { upsert: true }
  );

  // Contabilizar agregadas vs actualizadas
  if (result.upsertedCount > 0) {
    addedCount++;
  } else if (result.modifiedCount > 0) {
    updatedCount++;
  }
  ```
- **Después de procesar**: Marcar como `featured: false` las subcategorías que ya no existen:
  ```javascript
  const extractedSlugs = new Set(extractedSubcategories.map(s => generateSlug(s.name)));
  const removedSlugs = [...existingSlugs].filter(slug => !extractedSlugs.has(slug));

  let removedCount = 0;
  if (removedSlugs.length > 0) {
    const result = await db.collection('subcategories').updateMany(
      { slug: { $in: removedSlugs }, category: categorySlug },
      { $set: { featured: false, 'metadata.lastUpdated': new Date() } }
    );
    removedCount = result.modifiedCount;
  }

  // Log consolidado en una sola línea
  logger.info(`Category ${categorySlug}: ${addedCount} added, ${updatedCount} updated, ${removedCount} removed subcategories`);
  ```
- Mantener array local de subcategorías procesadas para el conteo del siguiente paso.

**Paso 3.3**: Contar subcategorías por categoría y actualizar metadata.
- Contar las subcategorías procesadas para esta categoría (longitud del array local).
- Actualizar el campo `metadata.subcategoryCount` en el documento Category correspondiente:
  ```javascript
  await db.collection('categories').updateOne(
    { slug: categorySlug },
    { 
      $set: { 
        'metadata.subcategoryCount': subcategoryCount,
        'metadata.lastUpdated': new Date()
      }
    }
  );
  ```

### 4. Optimizaciones y Mejoras

**Mejora 4.1: Procesamiento por Chunks Simultáneos**
- Dividir categorías en chunks de 5-10.
- Abrir múltiples instancias de Firefox simultáneas.
- Procesar chunks en paralelo para reducir tiempo total.

**Mejora 4.2: Checkpoints y Resiliencia**
- Guardar progreso cada 5 categorías procesadas.
- Archivo JSON: `checkpoint_subcategories_{timestamp}.json`
- Recuperar estado al reiniciar.

**Mejora 4.3: Anti-Detección**
- Delays aleatorios: 1-3 segundos entre acciones.
- User-agent rotativo por sesión.
- Evitar patrones repetitivos.

**Mejora 4.4: Logging Eficiente**
- Solo logs críticos: inicio/fin de categoría, errores.
- Reducir verbosity de Selenium.

**Mejora 4.5: Validación de Elementos**
- Esperar elementos con `WebDriverWait` (timeout 10s).
- Retry automático en fallos (máx 3 intentos).

## Implementación Técnica

### Tecnologías
- **Python 3.8+**
- **Selenium WebDriver** con GeckoDriver
- **Firefox** (no headless inicialmente)
- **PyMongo** para DB
- **Threading** para concurrencia

### Estructura de Archivos
```
Sandbox/Experiments/
├── carrefour_subcategories_scraping_process.md (este documento)
├── carrefour_subcategories_scraper.py
├── checkpoint_subcategories_{timestamp}.json (generado)
└── logs/
    └── subcategories_scraping.log
```

### Código Base
```python
# Importaciones
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from pymongo import MongoClient
import time
import json

# Configuración DB
client = MongoClient('mongodb://localhost:27017/')
db = client['carrefour']
categories_collection = db['categories']

# Configuración navegador
options = Options()
# NO headless para debugging
driver = webdriver.Firefox(options=options)

# Función principal
def scrape_subcategories():
    categories = list(categories_collection.find({'active': True}))
    for category in categories:
        url = f"https://www.carrefour.com.ar/{category['slug']}"
        driver.get(url)
        # Lógica de expansión y extracción
        # ...
```

## Validación y Testing

### Pruebas Iniciales
- Ejecutar con 1-2 categorías para verificar funcionamiento.
- Verificar expansión visual del filtro.
- Validar extracción de datos.

### Métricas de Éxito
- Tiempo por categoría: < 30 segundos.
- Tasa de éxito: > 95%.
- Sin detección como bot.

## Próximos Pasos

1. Implementar script básico (esta sesión).
2. Agregar concurrencia y checkpoints.
3. Integrar con pipeline completo de scraping.
4. Mover a prototipos tras validación.

## Referencias

- `scraping.instructions.md`: Guías generales de scraping.
- `base-datos.md`: Arquitectura DB.
- OuterHTML de `categoria_almacen_20250928_104932.html`: Estructura de referencia.

## Notas Adicionales

- Priorizar eficiencia sobre complejidad inicial.
- Documentar cualquier cambio en selectores CSS.
- Mantener compatibilidad con futuras expansiones.