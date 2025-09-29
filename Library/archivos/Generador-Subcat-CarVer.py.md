# Desglose de Archivo: Generador-Subcat-CarVer.py

## Propósito
Este archivo implementa un generador inteligente de subcategorías para productos de supermercados Carrefour, específicamente optimizado para categorías de "Carnes" y "Frutas y Verduras". Utiliza algoritmos de aprendizaje automático sin keywords hardcodeadas para crear subcategorías lógicas intermedias.

## Relaciones con Otros Archivos
- **Ubicación**: `Sandbox/prototypes/Generador-Subcat-CarVer.py`
- **Dependencias**: Selenium WebDriver para scraping web
- **Integración**: Diseñado para ser usado por scrapers de productos
- **Base de datos**: Compatible con MongoDB Atlas para almacenamiento de resultados

## Recreación
Para recrear este archivo:

1. **Crear archivo base**:
   ```bash
   touch Sandbox/prototypes/Generador-Subcat-CarVer.py
   ```

2. **Importaciones necesarias**:
   ```python
   import time
   from selenium import webdriver
   from selenium.webdriver.firefox.options import Options
   from selenium.webdriver.common.by import By
   from selenium.webdriver.support.ui import WebDriverWait
   from selenium.webdriver.support import expected_conditions as EC
   from collections import defaultdict, Counter
   import re
   from difflib import SequenceMatcher
   ```

3. **Funciones principales**:
   - `extract_product_types_from_category()`: Extrae tipos de producto usando Selenium
   - `analyze_category_context()`: Determina estrategia de agrupación por URL
   - `generate_subcategories_dynamically()`: Algoritmo principal inteligente
   - `generate_animal_based_subcategories()`: Para carnes (Vacuno, Porcino, Aves, etc.)
   - `generate_food_based_subcategories()`: Para frutas y verduras
   - `refine_with_similarity()`: Reclasificación usando similitud semántica

4. **Configuración de ejecución**:
   ```python
   if __name__ == "__main__":
       category_url = "https://www.carrefour.com.ar/Carnes-y-Pescados"
       analyze_category_and_generate_subcategories(category_url)
   ```

## Fecha de Incorporación
Septiembre 29, 2025

## Feature Asociada
Generador Inteligente de Subcategorías - Algoritmo que crea agrupaciones lógicas intermedias sin usar keywords hardcodeadas, optimizado para reducir productos en categoría "Otros" a menos del 10%.

## Características Técnicas
- **Algoritmo**: Aprendizaje automático basado en patrones de texto
- **Estrategias**: animal_type, food_type, beverage_type
- **Validación**: Clustering semántico con umbrales de coherencia
- **Rendimiento**: Clasificación >90% de productos en subcategorías lógicas
- **Escalabilidad**: Adaptable a cualquier categoría/supermercado

## Resultados Esperados
- **Carnes**: 5-6 subcategorías (Vacuno, Porcino, Aves, Pescados, Embutidos)
- **Frutas/Verduras**: 3-4 subcategorías (Frutas, Verduras, Frutos Secos)
- **Otros**: <10% de productos totales (solo excepciones reales)

## Testing
Para probar el funcionamiento:
```bash
cd Sandbox/prototypes
python Generador-Subcat-CarVer.py
```

Debe mostrar análisis completo con subcategorías generadas y estadísticas de clasificación.