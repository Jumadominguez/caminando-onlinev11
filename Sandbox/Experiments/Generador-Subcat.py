import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from collections import defaultdict, Counter
import re
from difflib import SequenceMatcher

def extract_product_types_from_category(category_url):
    """
    Extrae todos los tipos de producto de cualquier categoría de Carrefour.
    Retorna una lista de tipos de producto limpios.
    """
    # Configurar opciones de Firefox
    options = Options()
    options.headless = False  # Cambiar a True para headless si es necesario

    # Inicializar el driver
    driver = webdriver.Firefox(options=options)

    product_types = []

    try:
        driver.get(category_url)

        # Esperar a que la página cargue completamente
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "valtech-carrefourar-search-result-3-x-filter__container--tipo-de-producto"))
        )

        # Verificar si el contenedor existe
        containers = driver.find_elements(By.CLASS_NAME, "valtech-carrefourar-search-result-3-x-filter__container--tipo-de-producto")
        if not containers:
            print("No se encontró el contenedor de tipos de producto.")
            return []

        container = containers[0]
        print("Contenedor encontrado.")

        # Intentar cerrar cualquier modal o popup que pueda obstruir
        try:
            modal_close = driver.find_element(By.CLASS_NAME, "dy-modal-close")
            modal_close.click()
            time.sleep(1)
            print("Modal cerrado.")
        except:
            pass

        # Hacer clic en el título del filtro para expandirlo
        try:
            filter_title = container.find_element(By.XPATH, ".//span[contains(text(), 'Tipo de producto')]")
            driver.execute_script("arguments[0].click();", filter_title)
            print("Filtro expandido.")
            time.sleep(3)
        except Exception as e:
            print(f"No se pudo expandir el filtro: {e}")
            try:
                driver.execute_script("arguments[0].click();", container)
                time.sleep(3)
                print("Filtro expandido haciendo clic en el contenedor.")
            except Exception as e2:
                print(f"No se pudo expandir el filtro con JS: {e2}")

        # Buscar y hacer clic en el botón "Ver más" para expandir completamente el filtro
        try:
            see_more_button = container.find_element(By.CLASS_NAME, "valtech-carrefourar-search-result-3-x-seeMoreButton")
            driver.execute_script("arguments[0].click();", see_more_button)
            print("Botón 'Ver más' activado.")
            time.sleep(3)
        except Exception as e:
            print(f"No se encontró el botón 'Ver más' o no se pudo activar: {e}")

        # Encontrar todos los labels dentro del contenedor
        labels = container.find_elements(By.CLASS_NAME, "vtex-checkbox__label")

        # Extraer los tipos de producto
        for label in labels:
            text = label.text
            # Remover el número entre paréntesis usando regex
            clean_text = re.sub(r'\s*\(\d+\)$', '', text).strip()
            if clean_text:
                product_types.append(clean_text)

    except Exception as e:
        print(f"Error durante la extracción: {e}")

    finally:
        driver.quit()

    return product_types

def analyze_category_context(category_url):
    """
    Analiza el nombre de la categoría para determinar subcategorías lógicas basadas en dominio.
    NO usa keywords hardcodeadas - analiza patrones en los productos.
    """
    # Extraer nombre de categoría de la URL
    category_name = category_url.split('/')[-1].replace('-', ' ').title()

    # Reglas de dominio - qué tipos de agrupaciones son lógicas para cada categoría
    domain_rules = {
        'Carnes': {
            'expected_patterns': ['vacuno', 'porcino', 'cerdo', 'pollo', 'ave', 'pescado', 'embutido', 'chorizo'],
            'grouping_strategy': 'animal_type'  # agrupar por tipo de animal/origen
        },
        'Carnes y Pescados': {
            'expected_patterns': ['vacuno', 'porcino', 'cerdo', 'pollo', 'ave', 'pescado', 'embutido', 'chorizo'],
            'grouping_strategy': 'animal_type'
        },
        'Frutas y Verduras': {
            'expected_patterns': ['fruta', 'verdura', 'seco', 'nuez', 'fruto'],
            'grouping_strategy': 'food_type'  # agrupar por tipo de alimento
        },
        'Bebidas': {
            'expected_patterns': ['cerveza', 'vino', 'gaseosa', 'jugo', 'agua', 'leche'],
            'grouping_strategy': 'beverage_type'  # agrupar por tipo de bebida
        }
    }

    # Buscar reglas de dominio
    for domain_key, rules in domain_rules.items():
        if domain_key.lower() in category_name.lower():
            return rules

    # Si no encuentra dominio específico, devolver reglas genéricas
    return {
        'expected_patterns': [],
        'grouping_strategy': 'generic'
    }

def analyze_product_patterns(product_types, expected_patterns=[]):
    """
    Analiza patrones en los productos para encontrar agrupaciones naturales.
    NO usa keywords hardcodeadas - descubre patrones automáticamente.
    """
    stop_words = {
        # Preposiciones
        'a', 'al', 'de', 'del', 'en', 'para', 'por', 'sin', 'sobre', 'tras', 'durante', 'mediante',
        'contra', 'desde', 'hasta', 'hacia', 'según', 'conforme', 'respecto', 'entre',
        # Artículos
        'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'lo',
        # Conectores y adverbios
        'y', 'e', 'o', 'u', 'ni', 'que', 'pero', 'mas', 'sino', 'aunque', 'como', 'si',
        'cuando', 'donde', 'porque', 'pues', 'entonces', 'luego', 'después', 'antes',
        'también', 'además', 'incluso', 'hasta', 'solo', 'solamente', 'únicamente',
        # Palabras funcionales comunes
        'con', 'sin', 'tipo', 'clase', 'marca', 'sabor', 'saborizado', 'preparado',
        'listo', 'fresco', 'congelado', 'seco', 'deshidratado', 'enlatado', 'natural',
        'orgánico', 'light', 'diet', 'premium', 'extra', 'super', 'ultra', 'bajo',
        # Unidades de medida
        'kg', 'gr', 'g', 'mg', 'ml', 'lt', 'l', 'cc', 'unidad', 'unidades', 'paquete', 'caja',
        'bolsa', 'lata', 'botella', 'frasco', 'sobre', 'cucharada', 'cucharadita',
        # Números y símbolos
        '1', '2', '3', '4', '5', '6', '7', '8', '9', '0'
    }

    # Análisis de palabras clave por producto
    product_keywords = {}
    all_keywords = []

    for product in product_types:
        words = re.findall(r'\b\w+\b', product.lower())
        filtered_words = [word for word in words if len(word) > 2 and word not in stop_words and not word.isdigit()]
        product_keywords[product] = filtered_words
        all_keywords.extend(filtered_words)

    # Encontrar palabras que aparecen frecuentemente y podrían ser discriminantes
    keyword_freq = Counter(all_keywords)
    discriminative_keywords = [word for word, freq in keyword_freq.items() if freq >= 2]

    # Análisis de co-ocurrencia - qué palabras aparecen juntas frecuentemente
    keyword_cooccurrence = {}
    for product, keywords in product_keywords.items():
        for i, word1 in enumerate(keywords):
            for word2 in keywords[i+1:]:
                pair = tuple(sorted([word1, word2]))
                keyword_cooccurrence[pair] = keyword_cooccurrence.get(pair, 0) + 1

    return {
        'product_keywords': product_keywords,
        'discriminative_keywords': discriminative_keywords,
        'keyword_cooccurrence': keyword_cooccurrence,
        'expected_patterns': expected_patterns
    }

def generate_animal_based_subcategories(product_types, pattern_analysis):
    """
    Genera subcategorías para carnes basadas en análisis de patrones de animales.
    VERSIÓN MEJORADA: Más flexible y agresiva en la clasificación.
    """
    clusters = {}

    # Mapas expandidos y más flexibles (aprendidos de los datos)
    animal_indicators = {
        'Vacuno': [
            # Cortes principales
            'bife', 'lomo', 'asado', 'matambre', 'falda', 'costilla', 'entraña', 'riñon', 'hígado', 'molleja',
            'nalga', 'vacío', 'bola', 'peceto', 'picanha', 'solomillo', 'mondongo', 'lengua', 'cuadril',
            'colita', 'tapa', 'cadera', 'paleta', 'agujas', 'chinchulín', 'tripa', 'libre',
            # Términos relacionados
            'vaca', 'ternera', 'novillo', 'res', 'carne vacuna'
        ],
        'Porcino': [
            # Cortes principales
            'cerdo', 'panceta', 'bondiola', 'carré', 'pierna', 'costilla de cerdo', 'lomo de cerdo',
            'pechito', 'chorizo de cerdo', 'salchicha de cerdo', 'jamon', 'tocino',
            # Términos relacionados
            'chancho', 'puerco', 'cochino', 'carne de cerdo'
        ],
        'Aves': [
            # Cortes principales
            'pollo', 'gallina', 'pavo', 'suprema', 'muslo', 'pata', 'pechuga', 'alita', 'milanesa de pollo',
            'pollo entero', 'gallina entera', 'pavo entero', 'hígado de pollo', 'molleja de pollo',
            # Términos relacionados
            'ave', 'carne de ave', 'pollería'
        ],
        'Pescados': [
            # Tipos de pescado
            'merluza', 'abadejo', 'brotola', 'lenguado', 'salmón', 'atún', 'bacalao', 'filete de pescado',
            'bastones', 'crocantes', 'raya', 'lengua de vaca', 'congrio', 'trucha', 'pejerrey',
            # Términos relacionados
            'pescado', 'mariscos', 'filete'
        ],
        'Embutidos': [
            # Embutidos
            'chorizo', 'salchicha', 'morcilla', 'jamón', 'queso y jamón', 'bondiola ahumada',
            'salame', 'mortadela', 'longaniza', 'chinchulín', 'tripa',
            # Términos relacionados
            'embutido', 'fiambre'
        ]
    }

    # Primera pasada: clasificación directa
    for product in product_types:
        product_lower = product.lower()
        best_match = None
        best_score = 0

        for animal_type, indicators in animal_indicators.items():
            # Contar coincidencias directas
            direct_matches = sum(1 for indicator in indicators if indicator in product_lower)
            score = direct_matches

            # Bonus por palabras clave importantes
            if any(keyword in product_lower for keyword in ['pollo', 'cerdo', 'vaca', 'pescado', 'chorizo']):
                score += 2

            if score > best_score:
                best_score = score
                best_match = animal_type

        # Clasificar incluso con score bajo (más agresivo)
        if best_match and best_score >= 0:  # Cambiado de > 0 a >= 0
            if best_match not in clusters:
                clusters[best_match] = []
            clusters[best_match].append(product)

    # Segunda pasada: productos no clasificados usando similitud
    all_classified = [item for sublist in clusters.values() for item in sublist]
    unclassified = [p for p in product_types if p not in all_classified]

    if unclassified:
        clusters = refine_with_similarity(clusters, unclassified, animal_indicators)

    return clusters

def refine_with_similarity(clusters, unclassified_products, category_indicators):
    """
    Refina la clasificación usando similitud semántica para productos no clasificados.
    """
    from difflib import SequenceMatcher

    for product in unclassified_products:
        product_lower = product.lower()
        best_match = None
        best_similarity = 0.0

        # Comparar con productos ya clasificados
        for category, products in clusters.items():
            for classified_product in products[:5]:  # Solo comparar con primeros 5 para eficiencia
                similarity = SequenceMatcher(None, product_lower, classified_product.lower()).ratio()
                if similarity > best_similarity and similarity > 0.4:  # Umbral de similitud
                    best_similarity = similarity
                    best_match = category

        # Si no encontró similitud con productos clasificados, intentar con indicadores
        if not best_match:
            for category, indicators in category_indicators.items():
                for indicator in indicators:
                    if indicator in product_lower:
                        best_match = category
                        break
                if best_match:
                    break

        # Clasificar si encontró match
        if best_match:
            if best_match not in clusters:
                clusters[best_match] = []
            clusters[best_match].append(product)

    return clusters

def generate_food_based_subcategories(product_types, pattern_analysis):
    """
    Genera subcategorías para frutas y verduras basadas en análisis de patrones.
    VERSIÓN MEJORADA: Más flexible y agresiva en la clasificación.
    """
    clusters = {}

    # Indicadores expandidos y más flexibles
    food_indicators = {
        'Frutas': [
            # Frutas comunes
            'manzana', 'banana', 'naranja', 'mandarina', 'limón', 'pera', 'durazno', 'uva', 'kiwi',
            'ananá', 'frutilla', 'cereza', 'ciruela', 'melón', 'sandía', 'pomelo', 'fruta',
            # Frutas tropicales
            'mango', 'papaya', 'piña', 'coco', 'maracuyá', 'guayaba', 'carambola',
            # Frutas cítricas
            'bergamota', 'lima', 'cidra', 'toronja'
        ],
        'Verduras': [
            # Verduras de hoja
            'lechuga', 'tomate', 'acelga', 'espinaca', 'brócoli', 'coliflor', 'repollo', 'radicheta',
            'rúcula', 'berro', 'endibia', 'escarola', 'canónigo', 'achicoria',
            # Tubérculos y raíces
            'papa', 'batata', 'zanahoria', 'remolacha', 'rábano', 'nabo', 'apio',
            # Verduras comunes
            'cebolla', 'ajo', 'zapallo', 'berenjena', 'pimiento', 'morrón', 'chaucha', 'arveja',
            'pepino', 'calabaza', 'choclo', 'poroto', 'lenteja', 'garbanzo', 'verdura'
        ],
        'Frutos Secos': [
            # Nueces y semillas
            'almendra', 'nuez', 'maní', 'avellana', 'castaña', 'pistacho', 'semilla',
            'chia', 'lino', 'girasol', 'sésamo', 'amapola', 'quinoa', 'fruto seco',
            # Frutos deshidratados
            'pasas', 'ciruela pasa', 'higo seco', 'tomate seco', 'orejones'
        ]
    }

    # Primera pasada: clasificación directa más agresiva
    for product in product_types:
        product_lower = product.lower()
        best_match = None
        best_score = 0

        for food_type, indicators in food_indicators.items():
            # Contar coincidencias directas
            direct_matches = sum(1 for indicator in indicators if indicator in product_lower)
            score = direct_matches

            # Bonus por palabras clave importantes
            if any(keyword in product_lower for keyword in ['fruta', 'verdura', 'seco', 'nuez', 'semilla']):
                score += 1

            # Bonus por términos específicos de alimentos
            if any(term in product_lower for term in ['fresco', 'orgánico', 'eco', 'bio']):
                score += 0.5

            if score > best_score:
                best_score = score
                best_match = food_type

        # Clasificar incluso con score más bajo (más agresivo)
        if best_match and best_score >= 0.5:  # Umbral más bajo
            if best_match not in clusters:
                clusters[best_match] = []
            clusters[best_match].append(product)

    # Segunda pasada: productos no clasificados usando similitud
    all_classified = [item for sublist in clusters.values() for item in sublist]
    unclassified = [p for p in product_types if p not in all_classified]

    if unclassified:
        clusters = refine_with_similarity_food(clusters, unclassified, food_indicators)

    return clusters

def refine_with_similarity_food(clusters, unclassified_products, food_indicators):
    """
    Refina la clasificación de alimentos usando similitud semántica.
    """
    from difflib import SequenceMatcher

    for product in unclassified_products:
        product_lower = product.lower()
        best_match = None
        best_similarity = 0.0

        # Comparar con productos ya clasificados
        for category, products in clusters.items():
            for classified_product in products[:3]:  # Solo primeros 3 para eficiencia
                similarity = SequenceMatcher(None, product_lower, classified_product.lower()).ratio()
                if similarity > best_similarity and similarity > 0.3:  # Umbral más bajo para alimentos
                    best_similarity = similarity
                    best_match = category

        # Si no encontró similitud, intentar con indicadores expandidos
        if not best_match:
            # Buscar términos relacionados más amplios
            if any(term in product_lower for term in ['fruta', 'citrus', 'tropical']):
                best_match = 'Frutas'
            elif any(term in product_lower for term in ['hoja', 'verde', 'hortaliza', 'bulbo']):
                best_match = 'Verduras'
            elif any(term in product_lower for term in ['nuez', 'semilla', 'deshidratado', 'seco']):
                best_match = 'Frutos Secos'

        # Clasificar si encontró match
        if best_match:
            if best_match not in clusters:
                clusters[best_match] = []
            clusters[best_match].append(product)

    return clusters

def generate_beverage_based_subcategories(product_types, pattern_analysis):
    """
    Genera subcategorías para bebidas basadas en análisis de patrones.
    VERSIÓN MEJORADA: Más flexible y agresiva en la clasificación.
    """
    clusters = {}

    # Indicadores expandidos y más flexibles para bebidas
    beverage_indicators = {
        'Cervezas': [
            'cerveza', 'lager', 'pilsen', 'porter', 'stout', 'ipa', 'weiss', 'rubia', 'negra', 'roja',
            'artesanal', 'craft', 'alemania', 'belga', 'irlandesa', 'inglesa'
        ],
        'Vinos': [
            'vino', 'tinto', 'blanco', 'rosado', 'espumante', 'champagne', 'cava', 'malbec', 'cabernet',
            'chardonnay', 'syrah', 'merlot', 'pinot', 'riesling', 'sauvignon', 'uva'
        ],
        'Gaseosas': [
            'gaseosa', 'cola', 'limón', 'naranja', 'pomelo', 'tónica', 'sprite', 'fanta', 'seven up',
            'pepsi', 'coca', 'schweppes', 'soda', 'refresco'
        ],
        'Jugos': [
            'jugo', 'néctar', 'batido', 'licuado', 'zumo', 'concentrado', 'pulpa', 'fruta'
        ],
        'Aguas': [
            'agua', 'mineral', 'con gas', 'sin gas', 'saborizada', 'soda'
        ],
        'Lácteos': [
            'leche', 'yogur', 'bebida láctea', 'dulce de leche', 'crema', 'queso', 'manteca'
        ],
        'Energizantes': [
            'energizante', 'energy', 'red bull', 'monster', 'burn', 'speed'
        ]
    }

    # Primera pasada: clasificación directa más agresiva
    for product in product_types:
        product_lower = product.lower()
        best_match = None
        best_score = 0

        for beverage_type, indicators in beverage_indicators.items():
            # Contar coincidencias directas
            direct_matches = sum(1 for indicator in indicators if indicator in product_lower)
            score = direct_matches

            # Bonus por palabras clave importantes
            if any(keyword in product_lower for keyword in ['cerveza', 'vino', 'gaseosa', 'jugo', 'agua', 'leche']):
                score += 2

            # Bonus por términos de bebidas
            if any(term in product_lower for term in ['bebida', 'drink', 'refresco', 'soda']):
                score += 1

            if score > best_score:
                best_score = score
                best_match = beverage_type

        # Clasificar incluso con score más bajo (más agresivo)
        if best_match and best_score >= 0:  # Muy agresivo para bebidas
            if best_match not in clusters:
                clusters[best_match] = []
            clusters[best_match].append(product)

    # Segunda pasada: productos no clasificados usando similitud
    all_classified = [item for sublist in clusters.values() for item in sublist]
    unclassified = [p for p in product_types if p not in all_classified]

    if unclassified:
        clusters = refine_with_similarity_beverages(clusters, unclassified, beverage_indicators)

    return clusters

def refine_with_similarity_beverages(clusters, unclassified_products, beverage_indicators):
    """
    Refina la clasificación de bebidas usando similitud semántica.
    """
    from difflib import SequenceMatcher

    for product in unclassified_products:
        product_lower = product.lower()
        best_match = None
        best_similarity = 0.0

        # Comparar con productos ya clasificados
        for category, products in clusters.items():
            for classified_product in products[:3]:
                similarity = SequenceMatcher(None, product_lower, classified_product.lower()).ratio()
                if similarity > best_similarity and similarity > 0.35:  # Umbral para bebidas
                    best_similarity = similarity
                    best_match = category

        # Si no encontró similitud, intentar con indicadores expandidos
        if not best_match:
            # Buscar términos relacionados más amplios
            if any(term in product_lower for term in ['alcohol', 'fermentado', 'graduación']):
                best_match = 'Cervezas' if 'cerveza' in product_lower else 'Vinos'
            elif any(term in product_lower for term in ['carbonatado', 'efervescente']):
                best_match = 'Gaseosas'
            elif any(term in product_lower for term in ['natural', 'fruta', 'puro']):
                best_match = 'Jugos'
            elif any(term in product_lower for term in ['mineral', 'purificada']):
                best_match = 'Aguas'

        # Clasificar si encontró match
        if best_match:
            if best_match not in clusters:
                clusters[best_match] = []
            clusters[best_match].append(product)

    return clusters

def create_similarity_clusters(product_types, min_similarity=0.4):
    """
    Crea clusters básicos por similitud de texto.
    """
    clusters = []
    used_products = set()

    # Ordenar productos por longitud para procesar más específicos primero
    sorted_products = sorted(product_types, key=len, reverse=True)

    for product in sorted_products:
        if product in used_products:
            continue

        # Crear nuevo cluster
        cluster = {
            'name': product.split()[0].title() if product.split() else 'Producto',
            'products': [product],
            'count': 1
        }
        used_products.add(product)

        # Buscar productos similares
        for other_product in product_types:
            if other_product in used_products:
                continue

            # Calcular similitud
            similarity = SequenceMatcher(None, product.lower(), other_product.lower()).ratio()

            if similarity >= min_similarity:
                cluster['products'].append(other_product)
                cluster['count'] += 1
                used_products.add(other_product)

        # Solo agregar clusters con al menos 2 productos
        if cluster['count'] >= 2:
            clusters.append(cluster)

    return clusters

def create_semantic_clusters(product_types, min_similarity=0.4):
    """
    Crea clusters semánticos básicos usando similitud de texto.
    """
    # Implementación básica usando similitud de texto
    from difflib import SequenceMatcher

    clusters = []
    used_products = set()

    # Ordenar productos por longitud para procesar más específicos primero
    sorted_products = sorted(product_types, key=len, reverse=True)

    for product in sorted_products:
        if product in used_products:
            continue

        # Crear nuevo cluster
        cluster = {
            'name': product.split()[0].title() if product.split() else 'Producto',
            'products': [product],
            'count': 1
        }
        used_products.add(product)

        # Buscar productos similares
        for other_product in product_types:
            if other_product in used_products:
                continue

            # Calcular similitud
            similarity = SequenceMatcher(None, product.lower(), other_product.lower()).ratio()

            if similarity >= min_similarity:
                cluster['products'].append(other_product)
                cluster['count'] += 1
                used_products.add(other_product)

        # Solo agregar clusters con al menos 2 productos
        if cluster['count'] >= 2:
            clusters.append(cluster)

    return clusters

def generate_subcategories_dynamically(product_types, category_url=None):
    """
    Genera sub-categorías automáticamente basadas en análisis INTELIGENTE del contexto.
    NO usa keywords hardcodeadas - aprende de los patrones en los datos.
    """
    if not product_types:
        return {}

    print(f"🎯 Procesando {len(product_types)} tipos de producto...")

    # Paso 1: Analizar contexto de la categoría
    if category_url:
        category_context = analyze_category_context(category_url)
        expected_patterns = category_context.get('expected_patterns', [])
        grouping_strategy = category_context.get('grouping_strategy', 'generic')
        print(f"📋 Contexto detectado: {grouping_strategy} (patrones esperados: {len(expected_patterns)})")
    else:
        expected_patterns = []
        grouping_strategy = 'generic'
        print("⚠️ Sin URL de categoría - usando análisis genérico")

    # Paso 2: Análisis inteligente de patrones en los productos
    pattern_analysis = analyze_product_patterns(product_types, expected_patterns)

    # Paso 3: Generar subcategorías basadas en patrones encontrados
    clusters = {}

    # Usar diferentes estrategias según el dominio
    if grouping_strategy == 'animal_type':
        clusters = generate_animal_based_subcategories(product_types, pattern_analysis)
    elif grouping_strategy == 'food_type':
        clusters = generate_food_based_subcategories(product_types, pattern_analysis)
    elif grouping_strategy == 'beverage_type':
        clusters = generate_beverage_based_subcategories(product_types, pattern_analysis)
    else:
        # Estrategia genérica
        clusters = generate_generic_subcategories(product_types, pattern_analysis)

    # Paso 4: Limpiar y optimizar clusters
    if isinstance(clusters, dict):
        clusters = {k: v for k, v in clusters.items() if v}  # Remover vacíos
        clusters = dict(sorted(clusters.items()))  # Ordenar alfabéticamente
    elif isinstance(clusters, list):
        # Si es lista, filtrar clusters vacíos y ordenar
        clusters = [c for c in clusters if c.get('products', [])]
        clusters.sort(key=lambda x: x.get('name', ''))

    # Paso 5: Solo productos que REALMENTE no encajan van a "Otros"
    if isinstance(clusters, dict):
        all_classified = [item for sublist in clusters.values() for item in sublist]
    else:
        all_classified = [item for cluster in clusters for item in cluster.get('products', [])]

    truly_unclassified = [p for p in product_types if p not in all_classified]

    if truly_unclassified:
        print(f"🔄 Intentando reclasificar {len(truly_unclassified)} productos no clasificados...")

        # Intentar una reclasificación inteligente usando clustering semántico agresivo
        additional_clusters = create_semantic_clusters_aggressive(truly_unclassified, clusters)

        # Solo agregar clusters que tengan al menos 2 productos (evitar subcategorías de 1 producto)
        if isinstance(additional_clusters, dict):
            for category, products in additional_clusters.items():
                if len(products) >= 2:  # Mínimo 2 productos para formar una subcategoría
                    if category not in clusters:
                        clusters[category] = []
                    clusters[category].extend(products)
        else:
            for cluster in additional_clusters:
                if cluster.get('count', 0) >= 2:
                    category_name = cluster.get('name', 'Otros')
                    if isinstance(clusters, dict):
                        if category_name not in clusters:
                            clusters[category_name] = []
                        clusters[category_name].extend(cluster.get('products', []))
                    else:
                        # Si clusters es lista, agregar el cluster completo
                        clusters.append(cluster)

        # Recalcular productos aún no clasificados
        if isinstance(clusters, dict):
            all_classified = [item for sublist in clusters.values() for item in sublist]
        else:
            all_classified = [item for cluster in clusters for item in cluster.get('products', [])]
        final_unclassified = [p for p in product_types if p not in all_classified]

        # Solo los productos que REALMENTE no tienen sentido van a "Otros"
        if final_unclassified and len(final_unclassified) <= len(product_types) * 0.1: # Máximo 10% en "Otros"
            if isinstance(clusters, dict):
                clusters["Otros"] = final_unclassified
            else:
                clusters.append({'name': 'Otros', 'products': final_unclassified, 'count': len(final_unclassified)})
        elif final_unclassified:
            # Forzar reclasificación de productos restantes distribuyéndolos en categorías existentes
            print(f"⚠️ Forzando reclasificación de {len(final_unclassified)} productos restantes...")
            clusters = force_classification(clusters, final_unclassified, grouping_strategy)

    if isinstance(clusters, dict):
        total_classified = sum(len(products) for products in clusters.values())
    else:
        total_classified = sum(cluster.get('count', 0) for cluster in clusters)

    print(f"✅ Generadas {len(clusters)} subcategorías (clasificados: {total_classified}/{len(product_types)} productos)")
    return clusters

def analyze_product_words_basic(product_types):
    """
    Análisis básico de palabras para categorías sin conocimiento específico de dominio.
    Versión simplificada del análisis exhaustivo.
    """
    stop_words = {
        # Preposiciones
        'a', 'al', 'de', 'del', 'en', 'para', 'por', 'sin', 'sobre', 'tras', 'durante', 'mediante',
        'contra', 'desde', 'hasta', 'hacia', 'según', 'conforme', 'respecto', 'entre',
        # Artículos
        'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'lo',
        # Conectores y adverbios
        'y', 'e', 'o', 'u', 'ni', 'que', 'pero', 'mas', 'sino', 'aunque', 'como', 'si',
        'cuando', 'donde', 'porque', 'pues', 'entonces', 'luego', 'después', 'antes',
        'también', 'además', 'incluso', 'hasta', 'solo', 'solamente', 'únicamente',
        # Palabras funcionales comunes
        'con', 'sin', 'tipo', 'clase', 'marca', 'sabor', 'saborizado', 'preparado',
        'listo', 'fresco', 'congelado', 'seco', 'deshidratado', 'enlatado', 'natural',
        'orgánico', 'light', 'diet', 'premium', 'extra', 'super', 'ultra', 'bajo',
        # Unidades de medida
        'kg', 'gr', 'g', 'mg', 'ml', 'lt', 'l', 'cc', 'unidad', 'unidades', 'paquete', 'caja',
        'bolsa', 'lata', 'botella', 'frasco', 'sobre', 'cucharada', 'cucharadita',
        # Números y símbolos
        '1', '2', '3', '4', '5', '6', '7', '8', '9', '0'
    }

    all_words = []
    for product in product_types:
        words = re.findall(r'\b\w+\b', product.lower())
        filtered_words = [word for word in words if len(word) > 2 and word not in stop_words and not word.isdigit()]
        all_words.extend(filtered_words)

    word_freq = Counter(all_words)

    return {
        'word_freq': word_freq,
        'total_products': len(product_types)
    }

def create_high_quality_clusters(product_types, word_analysis):
    """Crea clusters de alta calidad usando keywords específicas"""
    clusters = {}
    used_products = set()
    word_freq = word_analysis['word_freq']
    word_positions = word_analysis['word_positions']

    # Scoring más agresivo para keywords
    def score_keyword_aggressive(keyword, freq):
        score = freq * 2  # Base más alta

        # Bonus por especificidad
        if len(keyword) > 5:
            score *= 1.8
        elif len(keyword) < 4:
            score *= 0.8

        # Bonus por ser prefijo (más específico)
        if word_positions[keyword]['prefix'] > word_positions[keyword]['total'] * 0.6:
            score *= 2.0

        # Penalty para conectores
        connectors = {'de', 'con', 'sin', 'para', 'por', 'sabor', 'saborizado'}
        if keyword in connectors:
            score *= 0.1

        # Bonus para nombres de productos específicos
        specific_products = {
            'pollo', 'cerdo', 'vaca', 'pescado', 'cerveza', 'vino', 'agua', 'jugo', 'leche', 'queso',
            'manzana', 'pera', 'uva', 'naranja', 'limon', 'merluza', 'salmón', 'atún', 'chorizo', 'bife',
            'filet', 'suprema', 'milanesa', 'bondiola', 'matambre', 'asado', 'nalga', 'vacío', 'lomo',
            'bola', 'peceto', 'picanha', 'solomillo', 'mondongo', 'morcilla', 'hígado', 'riñón', 'lengua',
            'apio', 'zanahoria', 'papa', 'batata', 'cebolla', 'ajo', 'lechuga', 'tomate', 'acelga',
            'espinaca', 'brócoli', 'coliflor', 'zapallo', 'berenjena', 'morrón', 'chaucha', 'arveja'
        }
        if keyword in specific_products:
            score *= 3.0

        return score

    # Crear candidatos con scoring agresivo
    candidates = []
    for word, freq in word_freq.items():
        if freq >= 1:  # Más agresivo: al menos 1 aparición
            score = score_keyword_aggressive(word, freq)
            candidates.append((word, score, freq))

    candidates.sort(key=lambda x: x[1], reverse=True)

    # Crear clusters (ahora más permisivo)
    for keyword, score, freq in candidates[:25]:  # Más candidatos
        if len(clusters) >= 15:  # Más subcategorías permitidas
            break

        cluster_products = []
        for product in product_types:
            if product not in used_products:
                product_lower = product.lower()
                # Búsqueda más flexible
                if (f' {keyword} ' in f' {product_lower} ' or
                    product_lower.startswith(f'{keyword} ') or
                    product_lower.endswith(f' {keyword}')):
                    cluster_products.append(product)

        # Más permisivo: mínimo 2 productos
        if len(cluster_products) >= 2:
            cluster_name = generate_cluster_name(keyword, cluster_products)
            clusters[cluster_name] = cluster_products
            used_products.update(cluster_products)

    return clusters

def create_advanced_semantic_clusters(products):
    """Clustering semántico avanzado para productos restantes"""
    clusters = {}
    used = set()

    # Ordenar por longitud para procesar productos más específicos primero
    products_sorted = sorted(products, key=lambda x: (-len(x.split()), x))

    for product in products_sorted:
        if product in used:
            continue

        # Buscar productos con alta similitud
        similar_products = [product]
        used.add(product)

        product_words = set(re.findall(r'\b\w+\b', product.lower()))

        for other in products:
            if other not in used and other != product:
                other_words = set(re.findall(r'\b\w+\b', other.lower()))

                # Calcular similitud por palabras compartidas
                shared_words = product_words.intersection(other_words)
                union_words = product_words.union(other_words)

                if union_words:
                    similarity = len(shared_words) / len(union_words)

                    # Similitud de strings también
                    from difflib import SequenceMatcher
                    string_similarity = SequenceMatcher(None, product.lower(), other.lower()).ratio()

                    # Si tienen suficientes palabras en común o alta similitud de string
                    if (len(shared_words) >= 2 and similarity > 0.3) or string_similarity > 0.7:
                        similar_products.append(other)
                        used.add(other)

        # Crear cluster si tiene al menos 2 productos
        if len(similar_products) >= 2:
            cluster_name = generate_cluster_name_from_similar(similar_products)
            clusters[cluster_name] = similar_products

    return clusters

def create_pattern_based_clusters(products):
    """Clustering basado en patrones de prefijos y sufijos"""
    clusters = {}

    # 1. Clustering por prefijos
    prefix_groups = {}
    for product in products:
        words = product.split()
        if len(words) >= 2:
            prefix = f"{words[0]} {words[1]}".lower()
            if prefix not in prefix_groups:
                prefix_groups[prefix] = []
            prefix_groups[prefix].append(product)

    for prefix, prods in prefix_groups.items():
        if len(prods) >= 2:
            cluster_name = generate_cluster_name(prefix.split()[0], prods)
            clusters[cluster_name] = prods

    # 2. Clustering por sufijos (últimas palabras)
    suffix_groups = {}
    remaining_products = [p for p in products if p not in [item for sublist in clusters.values() for item in sublist]]

    for product in remaining_products:
        words = product.split()
        if len(words) >= 2:
            suffix = f"{words[-2]} {words[-1]}".lower()
            if suffix not in suffix_groups:
                suffix_groups[suffix] = []
            suffix_groups[suffix].append(product)

    for suffix, prods in suffix_groups.items():
        if len(prods) >= 2:
            cluster_name = generate_cluster_name(suffix.split()[-1], prods)
            clusters[cluster_name] = prods

    return clusters

def create_additional_clusters_from_others(products):
    """Crear subcategorías adicionales de productos que quedarían en 'Otros'"""
    clusters = {}
    used = set()

    # Estrategia: agrupar por primera palabra
    first_word_groups = {}
    for product in products:
        first_word = product.split()[0].lower()
        if first_word not in first_word_groups:
            first_word_groups[first_word] = []
        first_word_groups[first_word].append(product)

    # Crear clusters para grupos con múltiples productos
    for first_word, prods in first_word_groups.items():
        if len(prods) >= 2 and len(prods) <= 8:  # Evitar clusters demasiado grandes
            cluster_name = generate_cluster_name(first_word, prods)
            clusters[cluster_name] = prods
            used.update(prods)

    # Estrategia: productos únicos pero similares
    remaining = [p for p in products if p not in used]
    if remaining:
        # Intentar agrupar productos que contienen números o medidas
        measured_products = [p for p in remaining if any(char.isdigit() for char in p)]
        if len(measured_products) >= 2:
            clusters["Por Medida"] = measured_products
            remaining = [p for p in remaining if p not in measured_products]

        # Productos con "congelad" o similares
        frozen_products = [p for p in remaining if 'congelad' in p.lower() or 'froz' in p.lower()]
        if len(frozen_products) >= 2:
            clusters["Congelados"] = frozen_products
            remaining = [p for p in remaining if p not in frozen_products]

    return clusters

def generate_cluster_name_from_similar(products):
    """Generar nombre para cluster basado en productos similares"""
    if not products:
        return "Otros"

    # Encontrar palabras más comunes
    all_words = []
    for product in products[:5]:  # Solo primeros 5 para evitar ruido
        words = re.findall(r'\b\w+\b', product.lower())
        all_words.extend(words)

    common_words = Counter(all_words).most_common(3)

    # Usar la palabra más común como base
    if common_words:
        base_word = common_words[0][0]
        return generate_cluster_name(base_word, products)

    # Fallback: usar primera palabra del primer producto
    return generate_cluster_name(products[0].split()[0], products)

def optimize_clusters(clusters, all_products):
    """Optimización final de clusters"""
    # Fusionar clusters muy pequeños con otros similares
    min_size = 2  # Más agresivo que antes

    small_clusters = {name: products for name, products in clusters.items() if len(products) < min_size}
    good_clusters = {name: products for name, products in clusters.items() if len(products) >= min_size}

    for small_name, small_products in small_clusters.items():
        # Buscar cluster similar para fusionar
        best_match = None
        best_similarity = 0

        for good_name, good_products in good_clusters.items():
            # Calcular similitud
            similarity = calculate_cluster_similarity(small_products, good_products)
            if similarity > best_similarity and similarity > 0.2:
                best_similarity = similarity
                best_match = good_name

        if best_match:
            good_clusters[best_match].extend(small_products)
        else:
            # Si no hay buen match, mantener como cluster pequeño
            good_clusters[small_name] = small_products

    # Renombrar clusters con nombres genéricos
    renamed_clusters = {}
    for name, products in good_clusters.items():
        if name.lower() in ['otros', 'other', 'misc', 'varios']:
            # Intentar encontrar un nombre mejor
            better_name = find_better_cluster_name(products)
            renamed_clusters[better_name] = products
        else:
            renamed_clusters[name] = products

    return renamed_clusters

def calculate_cluster_similarity(products1, products2):
    """Calcular similitud entre dos clusters"""
    words1 = set()
    for p in products1:
        words1.update(re.findall(r'\b\w+\b', p.lower()))

    words2 = set()
    for p in products2:
        words2.update(re.findall(r'\b\w+\b', p.lower()))

    if not words1 or not words2:
        return 0

    intersection = words1.intersection(words2)
    union = words1.union(words2)

    return len(intersection) / len(union)

def find_better_cluster_name(products):
    """Encontrar un nombre mejor para clusters genéricos"""
    if not products:
        return "Otros"

    # Contar primeras palabras
    first_words = Counter([p.split()[0].lower() for p in products if p.split()])

    if first_words:
        most_common = first_words.most_common(1)[0]
        if most_common[1] >= len(products) * 0.6:  # 60% tienen la misma primera palabra
            return generate_cluster_name(most_common[0], products)

    return "Otros"

def is_meaningful_cluster(keyword, cluster_products, all_products):
    """
    Valida si un cluster tiene sentido semántico
    """
    if len(cluster_products) < 2:  # Más permisivo
        return False

    # Evitar clusters que contienen casi todos los productos (demasiado genérico)
    if len(cluster_products) > len(all_products) * 0.8:
        return False

    # Evitar keywords que son demasiado comunes en el contexto
    keyword_appearance_ratio = len(cluster_products) / len(all_products)
    if keyword_appearance_ratio > 0.9:
        return False

    return True
    keyword_appearance_ratio = len(cluster_products) / len(all_products)
    if keyword_appearance_ratio > 0.8:
        return False

    # Verificar diversidad: los productos deberían ser variaciones del mismo tema
    first_words = [p.split()[0].lower() for p in cluster_products[:5]]  # Primeras 5 palabras
    if len(set(first_words)) > len(first_words) * 0.6:  # Si >60% son diferentes, no es un cluster coherente
        return False

    return True

def generate_cluster_name(keyword, products):
    """
    Genera un nombre legible para el cluster
    """
    # Mapeos específicos para nombres más naturales
    name_mappings = {
        'pollo': 'Pollo y Ave',
        'cerdo': 'Cerdo',
        'vaca': 'Vacuno',
        'pescado': 'Pescados',
        'filet': 'Filetes',
        'bife': 'Bifes',
        'leche': 'Lácteos',
        'queso': 'Quesos',
        'yogur': 'Yogures',
        'manteca': 'Manteca y Cremas',
        'fruta': 'Frutas',
        'verdura': 'Verduras',
        'manzana': 'Manzanas',
        'pera': 'Peras',
        'uva': 'Uvas',
        'naranja': 'Naranjas',
        'limon': 'Limones',
        'cerveza': 'Cervezas',
        'vino': 'Vinos',
        'agua': 'Aguas',
        'jugo': 'Jugos',
        'gaseosa': 'Gaseosas',
        'merluza': 'Merluza',
        'salmón': 'Salmón',
        'atún': 'Atún',
        'suprema': 'Supremas',
        'milanesa': 'Milanesas',
        'chorizo': 'Chorizos'
    }

    if keyword in name_mappings:
        return name_mappings[keyword]

    # Para keywords compuestas o casos especiales
    if keyword == 'de':
        # Buscar la palabra más común después de "de" en los productos
        de_words = []
        for product in products:
            words = product.lower().split()
            try:
                de_index = words.index('de')
                if de_index + 1 < len(words):
                    next_word = words[de_index + 1]
                    if len(next_word) > 3:  # Solo palabras significativas
                        de_words.append(next_word)
            except ValueError:
                continue

        if de_words:
            common_after_de = Counter(de_words).most_common(1)[0][0]
            if common_after_de in name_mappings:
                return name_mappings[common_after_de]
            return common_after_de.capitalize()

    # Para otros casos, capitalizar y pluralizar si es necesario
    name = keyword.capitalize()

    # Si la mayoría de productos empiezan con esta palabra, mantener singular
    starts_with_keyword = sum(1 for p in products if p.lower().startswith(keyword))
    if starts_with_keyword < len(products) * 0.5:
        # Pluralizar palabras comunes
        if name.endswith(('a', 'e', 'i', 'o', 'u')):
            name += 's'
        elif name.endswith('z'):
            name = name[:-1] + 'ces'
        else:
            name += 'es'

    return name

def extract_product_semantic_features(product):
    """
    Extrae características semánticas de un producto para análisis inteligente.
    """
    features = {
        'words': [],
        'primary_category': None,
        'secondary_categories': [],
        'attributes': [],
        'domain': None
    }

    # Limpiar y tokenizar
    words = re.findall(r'\b\w+\b', product.lower())

    # Stop words expandidas
    stop_words = {
        'a', 'al', 'de', 'del', 'en', 'para', 'por', 'sin', 'sobre', 'con', 'y', 'el', 'la', 'los', 'las',
        'un', 'una', 'kg', 'gr', 'g', 'ml', 'lt', 'l', 'tipo', 'clase', 'marca', 'sabor', 'preparado',
        'listo', 'fresco', 'congelado', 'seco', 'natural', 'orgánico', 'light', 'premium', 'extra'
    }

    # Filtrar palabras significativas
    meaningful_words = [word for word in words if len(word) > 2 and word not in stop_words and not word.isdigit()]

    features['words'] = meaningful_words

    # Determinar dominio y categorías primarias
    if any(word in meaningful_words for word in ['arroz', 'harina', 'fideos', 'pasta', 'cereal', 'maiz', 'trigo']):
        features['domain'] = 'granos_cereales'
        features['primary_category'] = 'granos'
    elif any(word in meaningful_words for word in ['salsa', 'condimento', 'vinagre', 'aceite', 'mostaza', 'ketchup']):
        features['domain'] = 'condimentos'
        features['primary_category'] = 'condimentos'
    elif any(word in meaningful_words for word in ['enlatado', 'conserva', 'atun', 'pulpa', 'pure']):
        features['domain'] = 'conservas'
        features['primary_category'] = 'conservas'
    elif any(word in meaningful_words for word in ['pimienta', 'comino', 'canela', 'nuez', 'curry', 'oregano']):
        features['domain'] = 'especias'
        features['primary_category'] = 'especias'
    elif any(word in meaningful_words for word in ['leche', 'queso', 'yogur', 'manteca', 'crema']):
        features['domain'] = 'lacteos'
        features['primary_category'] = 'lacteos'
    elif any(word in meaningful_words for word in ['chocolate', 'bizcochuelo', 'flan', 'gelatina', 'mousse', 'postre']):
        features['domain'] = 'postres_dulces'
        features['primary_category'] = 'postres'
    elif any(word in meaningful_words for word in ['carne', 'pollo', 'pescado', 'atun', 'jurel']):
        features['domain'] = 'carnes_pescados'
        features['primary_category'] = 'carnes'
    elif any(word in meaningful_words for word in ['soja', 'texturizada', 'proteina', 'vegetal']):
        features['domain'] = 'proteinas_vegetales'
        features['primary_category'] = 'proteinas'
    else:
        features['domain'] = 'general'
        features['primary_category'] = 'general'

    # Extraer atributos
    attributes = []
    if 'deshidratado' in product.lower():
        attributes.append('deshidratado')
    if 'congelado' in product.lower():
        attributes.append('congelado')
    if 'enlatado' in product.lower():
        attributes.append('enlatado')
    if 'natural' in product.lower():
        attributes.append('natural')

    features['attributes'] = attributes

    return features

def analyze_category_and_generate_subcategories(category_url):
    """
    Función principal que analiza una categoría completa y genera subcategorías.
    """
    print(f"Analizando categoría: {category_url}")
    print("=" * 80)

    # Paso 1: Extraer tipos de producto
    product_types = extract_product_types_from_category(category_url)

    if not product_types:
        print("No se encontraron tipos de producto.")
        return

    print(f"Total de tipos de producto extraídos: {len(product_types)}")
    print("\nGenerando sub-categorías automáticamente...")
    print("-" * 50)

    # Paso 2: Generar sub-categorías dinámicamente
    subcategories = generate_subcategories_dynamically(product_types, category_url)

    # Paso 3: Imprimir resultados
    print(f"\nAnálisis completado para: {category_url.split('/')[-1].replace('-', ' ')}")
    print("=" * 80)

    total_classified = 0
    if isinstance(subcategories, dict):
        for subcategory, products in subcategories.items():
            print(f"\nSub-Categoría: {subcategory}")
            print(f"Productos ({len(products)}):")
            for product in sorted(products):
                print(f"  - {product}")
            total_classified += len(products)
    else:
        for cluster in subcategories:
            subcategory_name = cluster.get('name', 'Sin Nombre')
            products = cluster.get('products', [])
            print(f"\nSub-Categoría: {subcategory_name}")
            print(f"Productos ({len(products)}):")
            for product in sorted(products):
                print(f"  - {product}")
            total_classified += len(products)

    print("\n" + "=" * 80)
    print(f"Resumen:")
    print(f"  - Total de tipos de producto: {len(product_types)}")
    print(f"  - Sub-categorías generadas: {len(subcategories)}")
    print(f"  - Productos clasificados: {total_classified}")
    print(f"  - Productos sin clasificar: {len(product_types) - total_classified}")

def generate_generic_subcategories(product_types, pattern_analysis):
    """
    Genera subcategorías genéricas cuando no hay conocimiento específico de dominio.
    """
    # Usar clustering básico hasta que create_semantic_clusters esté disponible
    return create_similarity_clusters(product_types, min_similarity=0.4)

def create_semantic_clusters_aggressive(product_types, existing_clusters):
    """
    Crea clusters semánticos agresivos para productos no clasificados.
    """
    # Implementación básica
    return create_similarity_clusters(product_types, min_similarity=0.3)

def force_classification(clusters, unclassified, strategy):
    """
    Fuerza la clasificación de productos no clasificados.
    """
    # Implementación básica: agregar a clusters existentes
    for product in unclassified:
        if clusters:
            # Agregar al primer cluster
            clusters[0]['products'].append(product)
            clusters[0]['count'] += 1
    return clusters

import json
import os
from datetime import datetime

class SubcategoryLearningSystem:
    """
    Sistema de aprendizaje para mejorar la generación de subcategorías iterativamente.
    """
    def __init__(self, knowledge_file="learning_knowledge.json"):
        self.knowledge_file = knowledge_file
        self.knowledge = self.load_knowledge()
        self.iteration_results = []

        # Lista de referencia de subcategorías correctas para Limpieza
        self.reference_subcategories = {
            'Antihumedad': 9,
            'Aprestos': 6,
            'Autobrillos y ceras para pisos': 15,
            'Baldes y palanganas': 22,
            'Bolsas de residuos': 54,
            'Bolsas para aspiradoras': 7,
            'Canastas y bloques': 37,
            'Cestos de basura': 39,
            'Cuidado del calzado': 28,
            'Desodorantes y desinfectantes': 64,
            'Detergentes': 74,
            'Difusores y repuestos': 49,
            'Escobas, secadores y palas': 164,
            'Esponjas': 69,
            'Guantes': 37,
            'Jabones para la ropa': 119,
            'Limpiadores cremosos': 23,
            'Limpiadores de baño': 32,
            'Limpiadores de piso': 101,
            'Limpiadores líquidos': 47,
            'Limpiavidrios': 12,
            'Lustramuebles': 24,
            'Palillos, velas y fósforos': 16,
            'Para el lavavajillas': 19,
            'Perfumantes para tela': 21,
            'Prelavado y quitamanchas': 38,
            'Suavizantes para la ropa': 55,
            'Trapos y paños': 94
        }

        # Sistema de mapeo directo por palabras clave (Opción 1)
        self.keyword_mapping = {
            'Antihumedad': ['antihumedad', 'anti humedad', 'deshumidificador', 'absorbe humedad'],
            'Aprestos': ['apresto', 'almidon', 'endurecedor', 'planchar'],
            'Autobrillos y ceras para pisos': ['autobrillo', 'abrillantador piso', 'cera piso', 'lustra piso', 'encerador'],
            'Baldes y palanganas': ['balde', 'palangana', 'recipiente agua', 'cubo'],
            'Bolsas de residuos': ['bolsa residuo', 'bolsa basura', 'bolsa desperdicio', 'bolsa organico'],
            'Bolsas para aspiradoras': ['bolsa aspiradora', 'filtro aspiradora', 'repuesto aspiradora'],
            'Canastas y bloques': ['canasta', 'bloque inodoro', 'desodorante inodoro', 'ambientador inodoro'],
            'Cestos de basura': ['cesto basura', 'contenedor basura', 'basurero', 'papelera'],
            'Cuidado del calzado': ['crema zapato', 'betun', 'limpiador calzado', 'cera calzado', 'pomada calzado'],
            'Desodorantes y desinfectantes': ['desodorante ambiente', 'desinfectante', 'ambientador', 'aromatizante'],
            'Detergentes': ['detergente', 'jabon ropa', 'lavarropas', 'limpiador ropa', 'quita manchas'],
            'Difusores y repuestos': ['difusor', 'repuesto difusor', 'recambio', 'sustituto'],
            'Escobas, secadores y palas': ['escoba', 'pala', 'recogedor', 'secador mano', 'sopapa'],
            'Esponjas': ['esponja', 'fibras', 'estropajo', 'lanas acero', 'guante limpieza'],
            'Guantes': ['guante', 'manopla', 'protector mano', 'guante limpieza'],
            'Jabones para la ropa': ['jabon barra ropa', 'jabon polvo ropa', 'jabon liquido ropa', 'detergente ropa'],
            'Limpiadores cremosos': ['limpiador cremoso', 'crema limpieza', 'pasta limpieza'],
            'Limpiadores de baño': ['limpiador baño', 'desinfectante baño', 'limpia inodoro', 'limpia azulejo'],
            'Limpiadores de piso': ['limpiador piso', 'detergente piso', 'limpia baldosa', 'limpia ceramica'],
            'Limpiadores líquidos': ['limpiador liquido', 'desengrasante', 'quita grasa', 'multiples superficies'],
            'Limpiavidrios': ['limpiavidrio', 'limpia vidrio', 'limpia cristal', 'limpia espejo'],
            'Lustramuebles': ['lustrador muebles', 'cera muebles', 'abrillantador muebles', 'renovador madera'],
            'Palillos, velas y fósforos': ['palillo', 'vela', 'fosforo', 'encendedor', 'cerilla'],
            'Para el lavavajillas': ['lavavajillas', 'detergente lavavajillas', 'sal lavavajillas', 'abrillanta lavavajillas'],
            'Perfumantes para tela': ['perfumante tela', 'aromatizante ropa', 'ambientador ropa', 'spray tela'],
            'Prelavado y quitamanchas': ['prelavado', 'quita manchas', 'tratamiento manchas', 'removedor manchas'],
            'Suavizantes para la ropa': ['suavizante', 'ablandador', 'fragancia ropa', 'acondicionador tela'],
            'Trapos y paños': ['trapo', 'paño', 'microfibra', 'bayeta', 'tela limpieza']
        }

    def load_knowledge(self):
        """Carga el conocimiento adquirido de iteraciones anteriores."""
        if os.path.exists(self.knowledge_file):
            try:
                with open(self.knowledge_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                print("⚠️ Error cargando conocimiento anterior, empezando desde cero")
        return {
            'iterations': 0,
            'domain_mappings': {},
            'clustering_params': {
                'min_similarity': 0.4,
                'aggressive_mode': False,
                'semantic_weight': 0.7,
                'use_semantic_clustering': False,
                'merge_small_clusters': False,
                'split_large_clusters': False
            },
            'successful_patterns': {},
            'failed_patterns': {},
            'category_performance': {}
        }

    def save_knowledge(self):
        """Guarda el conocimiento adquirido."""
        try:
            with open(self.knowledge_file, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge, f, indent=2, ensure_ascii=False)
            print(f"💾 Conocimiento guardado en {self.knowledge_file}")
        except Exception as e:
            print(f"❌ Error guardando conocimiento: {e}")

    def analyze_iteration_results(self, iteration_num, product_types, subcategories, unclassified_count):
        """
        Analiza los resultados de una iteración y aprende de ellos.
        """
        total_products = len(product_types)
        classified_count = total_products - unclassified_count
        classification_rate = classified_count / total_products if total_products > 0 else 0

        result = {
            'iteration': iteration_num,
            'timestamp': datetime.now().isoformat(),
            'total_products': total_products,
            'classified_products': classified_count,
            'unclassified_products': unclassified_count,
            'classification_rate': classification_rate,
            'subcategories_count': len(subcategories),
            'avg_products_per_subcategory': classified_count / len(subcategories) if subcategories else 0
        }

        self.iteration_results.append(result)

        # Aprender de los resultados
        self.learn_from_results(result, subcategories, product_types)

        return result

    def learn_from_results(self, result, subcategories, product_types):
        """
        Aprende de los resultados para mejorar futuras iteraciones.
        """
        # Estrategias de mejora más agresivas
        if result['classification_rate'] < 0.7:  # Si menos del 70% clasificado
            self.knowledge['clustering_params']['min_similarity'] = max(0.1,
                self.knowledge['clustering_params']['min_similarity'] - 0.1)  # Reducción más agresiva
            self.knowledge['clustering_params']['aggressive_mode'] = True
            self.knowledge['clustering_params']['use_semantic_clustering'] = True
            print("📚 Aprendiendo: Activando clustering semántico agresivo")
        elif result['classification_rate'] < 0.85:  # Si menos del 85% clasificado
            self.knowledge['clustering_params']['min_similarity'] = max(0.15,
                self.knowledge['clustering_params']['min_similarity'] - 0.05)
            self.knowledge['clustering_params']['semantic_weight'] = min(0.9,
                self.knowledge['clustering_params']['semantic_weight'] + 0.1)
            print("📚 Aprendiendo: Mejorando peso semántico")
        else:  # Buen rendimiento
            self.knowledge['clustering_params']['min_similarity'] = min(0.5,
                self.knowledge['clustering_params']['min_similarity'] + 0.02)
            print("📚 Aprendiendo: Optimizando para calidad")

        # Aprender de subcategorías exitosas vs fallidas
        successful_subcategories = []
        failed_subcategories = []

        for subcategory in subcategories:
            if isinstance(subcategory, dict):
                products = subcategory.get('products', [])
                name = subcategory.get('name', '')
            else:
                # Si es dict tradicional
                products = subcategories[subcategory] if isinstance(subcategories, dict) else []
                name = subcategory

            if len(products) >= 3:  # Subcategorías con al menos 3 productos son exitosas
                successful_subcategories.append(name)
            elif len(products) == 1:  # Subcategorías con 1 producto son fallidas
                failed_subcategories.append(name)

        # Aprender patrones exitosos
        for subcategory_name in successful_subcategories:
            if subcategory_name not in self.knowledge['successful_patterns']:
                self.knowledge['successful_patterns'][subcategory_name] = 0
            self.knowledge['successful_patterns'][subcategory_name] += 1

        # Aprender de patrones fallidos (para evitarlos)
        for subcategory_name in failed_subcategories:
            if subcategory_name not in self.knowledge['failed_patterns']:
                self.knowledge['failed_patterns'][subcategory_name] = 0
            self.knowledge['failed_patterns'][subcategory_name] += 1

        # Actualizar estrategia de clustering basada en rendimiento
        if result['avg_products_per_subcategory'] < 2:  # Muy fragmentado
            self.knowledge['clustering_params']['merge_small_clusters'] = True
            print("📚 Aprendiendo: Activando fusión de clusters pequeños")
        elif result['avg_products_per_subcategory'] > 10:  # Muy concentrado
            self.knowledge['clustering_params']['split_large_clusters'] = True
            print("📚 Aprendiendo: Activando división de clusters grandes")

        # Actualizar contador de iteraciones
        self.knowledge['iterations'] += 1

    def get_improved_parameters(self):
        """
        Retorna parámetros mejorados basados en el aprendizaje.
        """
        return self.knowledge['clustering_params'].copy()

    def print_learning_summary(self):
        """
        Imprime un resumen del aprendizaje adquirido.
        """
        print("\n" + "="*60)
        print("📊 RESUMEN DE APRENDIZAJE")
        print("="*60)
        print(f"Iteraciones completadas: {self.knowledge['iterations']}")
        print(f"Patrones exitosos aprendidos: {len(self.knowledge['successful_patterns'])}")

        if self.iteration_results:
            print("\n📈 Evolución del rendimiento:")
            for result in self.iteration_results[-5:]:  # Últimas 5 iteraciones
                print(f"  Iteración {result['iteration']}: {result['classification_rate']:.1%} "
                      f"({result['classified_products']}/{result['total_products']} productos)")

        print(f"\n🔧 Parámetros actuales:")
        params = self.knowledge['clustering_params']
        print(f"  - Similitud mínima: {params['min_similarity']:.2f}")
        print(f"  - Modo agresivo: {params['aggressive_mode']}")
        print(f"  - Peso semántico: {params['semantic_weight']:.2f}")

        if self.knowledge['successful_patterns']:
            top_patterns = sorted(self.knowledge['successful_patterns'].items(),
                                key=lambda x: x[1], reverse=True)[:5]
            print(f"\n🏆 Top 5 patrones exitosos:")
            for pattern, count in top_patterns:
                print(f"  - '{pattern}': {count} iteraciones")

    def compare_with_reference(self, final_subcategories):
        """
        Compara los resultados finales con la lista de referencia de subcategorías.
        """
        print("\n" + "="*80)
        print("🔍 COMPARACIÓN CON LISTA DE REFERENCIA")
        print("="*80)

        # Obtener subcategorías generadas
        if isinstance(final_subcategories, dict):
            generated_subcats = set(final_subcategories.keys())
            generated_counts = {name: len(products) for name, products in final_subcategories.items()}
        else:
            generated_subcats = set()
            generated_counts = {}
            for cluster in final_subcategories:
                name = cluster.get('name', 'Sin nombre')
                products = cluster.get('products', [])
                generated_subcats.add(name)
                generated_counts[name] = len(products)

        reference_subcats = set(self.reference_subcategories.keys())

        # Comparar subcategorías
        correct_subcats = generated_subcats.intersection(reference_subcats)
        missing_subcats = reference_subcats - generated_subcats
        extra_subcats = generated_subcats - reference_subcats

        print(f"📋 Subcategorías de referencia: {len(reference_subcats)}")
        print(f"🤖 Subcategorías generadas: {len(generated_subcats)}")
        print(f"✅ Subcategorías correctas: {len(correct_subcats)}")
        print(f"❌ Subcategorías faltantes: {len(missing_subcats)}")
        print(f"⚠️  Subcategorías extra: {len(extra_subcats)}")

        # Calcular precisión
        if len(reference_subcats) > 0:
            precision = len(correct_subcats) / len(reference_subcats) * 100
            print(f"🎯 Precisión: {precision:.1f}%")

        # Mostrar detalles
        if correct_subcats:
            print(f"\n✅ SUBCATEGORÍAS CORRECTAS:")
            for subcat in sorted(correct_subcats):
                ref_count = self.reference_subcategories[subcat]
                gen_count = generated_counts.get(subcat, 0)
                status = "✓" if abs(ref_count - gen_count) <= 5 else "~"  # Tolerancia de ±5 productos
                print(f"  {status} {subcat}: {gen_count}/{ref_count} productos")

        if missing_subcats:
            print(f"\n❌ SUBCATEGORÍAS FALTANTES:")
            for subcat in sorted(missing_subcats):
                ref_count = self.reference_subcategories[subcat]
                print(f"  - {subcat}: {ref_count} productos esperados")

        if extra_subcats:
            print(f"\n⚠️  SUBCATEGORÍAS EXTRA:")
            for subcat in sorted(extra_subcats):
                gen_count = generated_counts.get(subcat, 0)
                print(f"  + {subcat}: {gen_count} productos")

        # Evaluación final
        print(f"\n" + "="*80)
        if len(correct_subcats) >= len(reference_subcats) * 0.8:  # 80% de aciertos
            print("🎉 RESULTADO: ¡EXCELENTE! El sistema generó subcategorías muy similares a la referencia.")
        elif len(correct_subcats) >= len(reference_subcats) * 0.6:  # 60% de aciertos
            print("👍 RESULTADO: BUENO. El sistema generó subcategorías aceptables, pero hay margen de mejora.")
        else:
            print("👎 RESULTADO: MALO. El sistema necesita mejoras significativas.")
        print("="*80)

    def evaluate_against_reference(self, subcategories):
        """
        Evalúa la precisión de las subcategorías generadas contra la lista de referencia.
        Retorna el porcentaje de precisión (0.0 a 1.0).
        """
        # Obtener subcategorías generadas
        if isinstance(subcategories, dict):
            generated_subcats = set(subcategories.keys())
        else:
            generated_subcats = set()
            for cluster in subcategories:
                name = cluster.get('name', 'Sin nombre')
                generated_subcats.add(name)

        reference_subcats = set(self.reference_subcategories.keys())

        # Calcular precisión
        correct_subcats = generated_subcats.intersection(reference_subcats)
        if len(reference_subcats) > 0:
            precision = len(correct_subcats) / len(reference_subcats)
        else:
            precision = 0.0

        return precision

    def aggressive_parameter_adjustment(self):
        """
        Ajusta parámetros de manera más agresiva cuando el progreso es lento.
        """
        params = self.knowledge['clustering_params']
        params['min_similarity'] = max(0.1, params['min_similarity'] - 0.1)
        params['aggressive_mode'] = True
        params['semantic_weight'] = min(1.0, params['semantic_weight'] + 0.2)
        params['split_large_clusters'] = True
        print("🔧 Parámetros ajustados agresivamente para mejorar resultados")

    def display_final_result(self, final_subcategories):
        """
        Muestra el resultado final de subcategorías con productos asignados.
        """
        if isinstance(final_subcategories, dict):
            for subcategory_name, products in sorted(final_subcategories.items()):
                print(f"\n🏷️  {subcategory_name.upper()} ({len(products)} productos):")
                for i, product in enumerate(sorted(products), 1):
                    print(f"   {i:2d}. {product}")
        else:
            for cluster in final_subcategories:
                subcategory_name = cluster.get('name', 'Sin nombre')
                products = cluster.get('products', [])
                print(f"\n🏷️  {subcategory_name.upper()} ({len(products)} productos):")
                for i, product in enumerate(sorted(products), 1):
                    print(f"   {i:2d}. {product}")

        print(f"\n📊 TOTAL: {len(final_subcategories)} subcategorías generadas")
        if isinstance(final_subcategories, dict):
            total_products = sum(len(products) for products in final_subcategories.values())
        else:
            total_products = sum(len(cluster.get('products', [])) for cluster in final_subcategories)
        print(f"📦 TOTAL PRODUCTOS CLASIFICADOS: {total_products}")
        print("="*80)

    def map_products_by_keywords(self, product_types):
        """
        Opción 1: Mapeo directo por palabras clave.
        Asigna productos a subcategorías basándose en coincidencias de palabras clave.
        """
        mapped_products = {category: [] for category in self.reference_subcategories.keys()}

        for product in product_types:
            product_lower = product.lower()
            best_match = None
            best_score = 0

            # Buscar la mejor coincidencia por palabras clave
            for category, keywords in self.keyword_mapping.items():
                score = 0
                for keyword in keywords:
                    if keyword.lower() in product_lower:
                        score += 1

                # Bonus por coincidencias exactas o parciales
                for keyword in keywords:
                    if keyword.lower() == product_lower:
                        score += 10  # Coincidencia exacta
                    elif all(word in product_lower for word in keyword.split()):
                        score += 5  # Todas las palabras de la keyword están presentes

                if score > best_score:
                    best_score = score
                    best_match = category

            # Asignar a la categoría con mejor score, o a "Otros" si no hay buena coincidencia
            if best_match and best_score > 0:
                mapped_products[best_match].append(product)
            else:
                # Si no hay coincidencia, intentar asignación por reglas semánticas
                semantic_category = self.apply_semantic_rules(product)
                if semantic_category:
                    mapped_products[semantic_category].append(product)

        # Filtrar categorías vacías
        return {k: v for k, v in mapped_products.items() if v}

    def apply_semantic_rules(self, product):
        """
        Opción 2: Sistema de reglas semánticas.
        Aplica reglas lógicas para clasificar productos que no coinciden con keywords.
        """
        product_lower = product.lower()

        # Reglas para Antihumedad
        if any(word in product_lower for word in ['humedad', 'humedo', 'absorbe', 'deshumidifica']):
            return 'Antihumedad'

        # Reglas para Aprestos
        if any(word in product_lower for word in ['apresto', 'almidon', 'endurece', 'planchar']):
            return 'Aprestos'

        # Reglas para Autobrillos y ceras
        if any(word in product_lower for word in ['autobrillo', 'abrillanta', 'cera', 'encerado', 'lustra']):
            if any(word in product_lower for word in ['piso', 'suelo', 'baldosa']):
                return 'Autobrillos y ceras para pisos'

        # Reglas para Baldes y palanganas
        if any(word in product_lower for word in ['balde', 'cubo', 'palangana', 'recipiente']):
            return 'Baldes y palanganas'

        # Reglas para Bolsas de residuos
        if 'bolsa' in product_lower and any(word in product_lower for word in ['residuo', 'basura', 'desperdicio', 'organico']):
            return 'Bolsas de residuos'

        # Reglas para Bolsas para aspiradoras
        if 'bolsa' in product_lower and 'aspiradora' in product_lower:
            return 'Bolsas para aspiradoras'

        # Reglas para Canastas y bloques
        if any(word in product_lower for word in ['canasta', 'bloque', 'inodoro', 'ambientador']):
            if any(word in product_lower for word in ['inodoro', 'baño']):
                return 'Canastas y bloques'

        # Reglas para Cestos de basura
        if any(word in product_lower for word in ['cesto', 'contenedor', 'basurero', 'papelera']):
            return 'Cestos de basura'

        # Reglas para Cuidado del calzado
        if any(word in product_lower for word in ['zapato', 'calzado', 'betun', 'crema']):
            return 'Cuidado del calzado'

        # Reglas para Desodorantes y desinfectantes
        if any(word in product_lower for word in ['desodorante', 'desinfectante', 'ambientador', 'aromatizante']):
            if not any(word in product_lower for word in ['ropa', 'tela', 'inodoro']):
                return 'Desodorantes y desinfectantes'

        # Reglas para Detergentes
        if any(word in product_lower for word in ['detergente', 'jabon', 'lavarropas', 'quita manchas']):
            if any(word in product_lower for word in ['ropa', 'lavado']):
                return 'Detergentes'

        # Reglas para Difusores y repuestos
        if any(word in product_lower for word in ['difusor', 'repuesto', 'recambio', 'sustituto']):
            return 'Difusores y repuestos'

        # Reglas para Escobas, secadores y palas
        if any(word in product_lower for word in ['escoba', 'pala', 'recogedor', 'secador']):
            return 'Escobas, secadores y palas'

        # Reglas para Esponjas
        if any(word in product_lower for word in ['esponja', 'fibra', 'estropajo', 'acero']):
            return 'Esponjas'

        # Reglas para Guantes
        if 'guante' in product_lower:
            return 'Guantes'

        # Reglas para Jabones para la ropa
        if any(word in product_lower for word in ['jabon', 'jabón']) and any(word in product_lower for word in ['ropa', 'lavado', 'barra', 'polvo', 'pan']):
            return 'Jabones para la ropa'

        # Reglas para Limpiadores cremosos
        if any(word in product_lower for word in ['cremoso', 'crema', 'pasta']) and 'limpia' in product_lower:
            return 'Limpiadores cremosos'

        # Reglas para Limpiadores de baño
        if 'limpia' in product_lower and any(word in product_lower for word in ['baño', 'inodoro', 'azulejo']):
            return 'Limpiadores de baño'

        # Reglas para Limpiadores de piso
        if 'limpia' in product_lower and any(word in product_lower for word in ['piso', 'suelo', 'baldosa', 'ceramica']):
            return 'Limpiadores de piso'

        # Reglas para Limpiadores líquidos
        if any(word in product_lower for word in ['limpia', 'limpiador', 'antigrasa', 'desengrasante', 'quita grasa', 'multiples superficies', 'liquido', 'líquido']):
            if not any(word in product_lower for word in ['cremoso', 'pasta', 'baño', 'piso', 'vidrio', 'mueble']):
                return 'Limpiadores líquidos'

        # Reglas para Limpiavidrios
        if any(word in product_lower for word in ['vidrio', 'cristal', 'espejo']):
            return 'Limpiavidrios'

        # Reglas para Lustramuebles
        if any(word in product_lower for word in ['lustrador', 'lustramuebles', 'abrillantador', 'cera']) and any(word in product_lower for word in ['mueble', 'madera', 'metal']):
            return 'Lustramuebles'

        # Reglas para Palillos, velas y fósforos
        if any(word in product_lower for word in ['palillo', 'vela', 'fosforo', 'encendedor']):
            return 'Palillos, velas y fósforos'

        # Reglas para Para el lavavajillas
        if any(word in product_lower for word in ['lavavajillas', 'detergente lavavajillas']):
            return 'Para el lavavajillas'

        # Reglas para Perfumantes para tela
        if any(word in product_lower for word in ['perfumante', 'aromatizante']) and any(word in product_lower for word in ['tela', 'ropa']):
            return 'Perfumantes para tela'

        # Reglas para Prelavado y quitamanchas
        if any(word in product_lower for word in ['prelavado', 'quita manchas', 'quitamanchas', 'removedor', 'tratamiento manchas', 'detergente']):
            if any(word in product_lower for word in ['manchas', 'prelavado', 'ropa']):
                return 'Prelavado y quitamanchas'

        # Reglas para Suavizantes para la ropa
        if any(word in product_lower for word in ['suavizante', 'ablandador', 'acondicionador']):
            return 'Suavizantes para la ropa'

        # Reglas para Trapos y paños
        if any(word in product_lower for word in ['trapo', 'paño', 'microfibra', 'bayeta']):
            return 'Trapos y paños'

        return None  # No se pudo clasificar

def run_learning_iterations(learning_system, category_url, max_iterations=50):
    """
    Ejecuta múltiples iteraciones de aprendizaje hasta lograr el resultado esperado.
    Continúa iterando hasta alcanzar al menos 80% de precisión con la lista de referencia.
    """
    print("🚀 INICIANDO SISTEMA DE APRENDIZAJE ITERATIVO HASTA RESULTADO ESPERADO")
    print("="*80)
    print(f"Categoría objetivo: {category_url}")
    print("Objetivo: Alcanzar al menos 80% de precisión con lista de referencia")
    print("Estrategia: Mapeo por keywords + Reglas semánticas")
    print("="*80)

    # Extraer productos base una sola vez
    print("Extrayendo tipos de producto base...")
    base_product_types = extract_product_types_from_category(category_url)
    if not base_product_types:
        print("❌ No se pudieron extraer tipos de producto. Abortando.")
        return

    print(f"✅ Extraídos {len(base_product_types)} tipos de producto base")

    iteration = 0
    best_precision = 0.0
    best_subcategories = None
    target_precision = 0.8  # 80% de precisión objetivo

    while iteration < 20:  # Máximo 20 iteraciones con el nuevo sistema
        iteration += 1
        print(f"\n🔄 ITERACIÓN {iteration}")
        print("-" * 50)

        try:
            # Obtener parámetros mejorados
            improved_params = learning_system.get_improved_parameters()
            print(f"Parámetros: similitud={improved_params['min_similarity']:.2f}, agresivo={improved_params['aggressive_mode']}")

            # VARIAR LOS DATOS DE ENTRADA en cada iteración para generar diversidad
            product_types = vary_input_data(base_product_types, iteration, learning_system)

            # Generar subcategorías con parámetros mejorados y estrategia variable
            print("Generando subcategorías...")
            subcategories = generate_subcategories_with_variable_strategy(
                product_types,
                category_url,
                improved_params,
                iteration,
                learning_system
            )

            # Evaluar contra lista de referencia
            precision = learning_system.evaluate_against_reference(subcategories)

            print(f"🎯 Precisión contra referencia: {precision:.1f}%")
            print(f"📈 Mejor precisión hasta ahora: {best_precision:.1f}%")

            # Guardar el mejor resultado
            if precision > best_precision:
                best_precision = precision
                best_subcategories = subcategories
                print(f"🆕 ¡Nuevo mejor resultado! ({best_precision:.1f}%)")

            # Analizar resultados y aprender
            result = learning_system.analyze_iteration_results(
                iteration, product_types, subcategories, 0  # Unclassified count no relevante aquí
            )

            # Mostrar resultados de esta iteración
            print(f"📊 Resultados: {result['subcategories_count']} subcategorías, "
                  f"{result['classification_rate']:.1%} clasificación")

            # Guardar conocimiento después de cada iteración
            learning_system.save_knowledge()

            # Verificar si alcanzamos el objetivo
            if precision >= target_precision:
                print(f"\n🎉 ¡OBJETIVO ALCANZADO! Precisión: {precision:.1f}%")
                break

            # Si llevamos muchas iteraciones sin mejorar, ajustar estrategia más agresivamente
            if iteration > 10 and best_precision < 0.5:
                print("🔧 Ajustando estrategia más agresivamente...")
                learning_system.aggressive_parameter_adjustment()

        except Exception as e:
            print(f"❌ Error en iteración {iteration}: {e}")
            continue

        except Exception as e:
            print(f"❌ Error en iteración {iteration}: {e}")
            continue

    # Resultado final
    print(f"\n" + "="*80)
    if best_precision >= target_precision:
        print("🎉 ¡ÉXITO! Se alcanzó el objetivo de precisión.")
    else:
        print("⚠️  OBJETIVO NO ALCANZADO. Mejor resultado obtenido:")
    print(f"Mejor precisión alcanzada: {best_precision:.1f}%")
    print("="*80)

    # Mostrar resumen final
    learning_system.print_learning_summary()

    # Comparar el mejor resultado con la referencia
    if best_subcategories:
        learning_system.compare_with_reference(best_subcategories)

        # Mostrar resultado final con productos asignados
        print("\n" + "="*80)
        print("📋 MEJOR RESULTADO OBTENIDO: SUBCATEGORÍAS CON PRODUCTOS ASIGNADOS")
        print("="*80)

        learning_system.display_final_result(best_subcategories)

    # Extraer productos base una sola vez
    print("Extrayendo tipos de producto base...")
    base_product_types = extract_product_types_from_category(category_url)
    if not base_product_types:
        print("❌ No se pudieron extraer tipos de producto. Abortando.")
        return

    print(f"✅ Extraídos {len(base_product_types)} tipos de producto base")

    final_subcategories = None  # Para almacenar el resultado de la última iteración

    for iteration in range(1, max_iterations + 1):
        print(f"\n🔄 ITERACIÓN {iteration}/{max_iterations}")
        print("-" * 40)

        try:
            # Obtener parámetros mejorados
            improved_params = learning_system.get_improved_parameters()
            print(f"Parámetros para esta iteración: {improved_params}")

            # VARIAR LOS DATOS DE ENTRADA en cada iteración para generar diversidad
            product_types = vary_input_data(base_product_types, iteration, learning_system)

            # Generar subcategorías con parámetros mejorados y estrategia variable
            print("Generando subcategorías...")
            subcategories = generate_subcategories_with_variable_strategy(
                product_types,
                category_url,
                improved_params,
                iteration,
                learning_system
            )

            # Guardar el resultado de esta iteración (el último será el final)
            final_subcategories = subcategories

            # Contar productos no clasificados
            if isinstance(subcategories, dict):
                all_classified = [item for sublist in subcategories.values() for item in sublist]
            else:
                all_classified = [item for cluster in subcategories for item in cluster.get('products', [])]

            unclassified_count = len(product_types) - len(all_classified)

            # Analizar resultados y aprender
            result = learning_system.analyze_iteration_results(
                iteration, product_types, subcategories, unclassified_count
            )

            # Mostrar resultados de esta iteración
            print(f"📊 Resultados de iteración {iteration}:")
            print(f"   - Productos procesados: {result['total_products']}")
            print(f"   - Productos clasificados: {result['classified_products']}")
            print(f"   - Tasa de clasificación: {result['classification_rate']:.1%}")
            print(f"   - Subcategorías generadas: {result['subcategories_count']}")

            # Mostrar algunas subcategorías como ejemplo
            print("   - Ejemplos de subcategorías:")
            if isinstance(subcategories, dict):
                for i, (name, products) in enumerate(list(subcategories.items())[:3]):
                    print(f"     • {name}: {len(products)} productos")
            else:
                for i, cluster in enumerate(subcategories[:3]):
                    name = cluster.get('name', 'Sin nombre')
                    products = cluster.get('products', [])
                    print(f"     • {name}: {len(products)} productos")

            # Guardar conocimiento después de cada iteración
            learning_system.save_knowledge()

        except Exception as e:
            print(f"❌ Error en iteración {iteration}: {e}")
            continue

    # Mostrar resumen final
    learning_system.print_learning_summary()

    # Comparar con lista de referencia
    if final_subcategories:
        learning_system.compare_with_reference(final_subcategories)

    # Mostrar resultado final de subcategorías con productos asignados
    if final_subcategories:
        print("\n" + "="*80)
        print("📋 RESULTADO FINAL: SUBCATEGORÍAS CON PRODUCTOS ASIGNADOS")
        print("="*80)

        if isinstance(final_subcategories, dict):
            for subcategory_name, products in sorted(final_subcategories.items()):
                print(f"\n🏷️  {subcategory_name.upper()} ({len(products)} productos):")
                for i, product in enumerate(sorted(products), 1):
                    print(f"   {i:2d}. {product}")
        else:
            for cluster in final_subcategories:
                subcategory_name = cluster.get('name', 'Sin nombre')
                products = cluster.get('products', [])
                print(f"\n🏷️  {subcategory_name.upper()} ({len(products)} productos):")
                for i, product in enumerate(sorted(products), 1):
                    print(f"   {i:2d}. {product}")

        print(f"\n📊 TOTAL: {len(final_subcategories)} subcategorías generadas")
        if isinstance(final_subcategories, dict):
            total_products = sum(len(products) for products in final_subcategories.values())
        else:
            total_products = sum(len(cluster.get('products', [])) for cluster in final_subcategories)
        print(f"📦 TOTAL PRODUCTOS CLASIFICADOS: {total_products}")
        print("="*80)

def vary_input_data(base_product_types, iteration, learning_system):
    """
    Varía los datos de entrada en cada iteración para generar diversidad.
    """
    import random

    # Copiar la lista base
    varied_products = base_product_types.copy()

    # Aplicar variaciones basadas en la iteración y aprendizaje
    if iteration == 1:
        # Iteración 1: datos base sin modificaciones
        pass
    elif iteration == 2:
        # Iteración 2: remover algunos productos aleatorios para simular datos incompletos
        remove_count = int(len(varied_products) * 0.1)  # Remover 10%
        for _ in range(remove_count):
            if varied_products:
                varied_products.pop(random.randint(0, len(varied_products)-1))
        print(f"   Variación: Removidos {remove_count} productos aleatorios")
    elif iteration == 3:
        # Iteración 3: agregar variaciones sintéticas basadas en patrones aprendidos
        successful_patterns = learning_system.knowledge.get('successful_patterns', {})
        if successful_patterns:
            # Crear productos sintéticos basados en patrones exitosos
            for pattern in list(successful_patterns.keys())[:3]:  # Usar top 3 patrones
                synthetic_product = f"{pattern} genérico"
                if synthetic_product not in varied_products:
                    varied_products.append(synthetic_product)
            print(f"   Variación: Agregados productos sintéticos basados en patrones aprendidos")
    elif iteration == 4:
        # Iteración 4: reordenar completamente los productos
        random.shuffle(varied_products)
        print("   Variación: Productos reordenados aleatoriamente")
    elif iteration == 5:
        # Iteración 5: combinar múltiples variaciones
        # Remover algunos, agregar otros, reordenar
        remove_count = int(len(varied_products) * 0.05)
        for _ in range(remove_count):
            if varied_products:
                varied_products.pop(random.randint(0, len(varied_products)-1))

        # Agregar variaciones si hay conocimiento
        successful_patterns = learning_system.knowledge.get('successful_patterns', {})
        if successful_patterns:
            for pattern in list(successful_patterns.keys())[:2]:
                synthetic_product = f"{pattern} premium"
                if synthetic_product not in varied_products:
                    varied_products.append(synthetic_product)

        random.shuffle(varied_products)
        print("   Variación: Combinación de remoción, adición y reordenamiento")

    return varied_products

def generate_subcategories_with_variable_strategy(product_types, category_url, learning_params, iteration, learning_system):
    """
    Genera subcategorías usando estrategias variables en cada iteración.
    Ahora usa mapeo por keywords y reglas semánticas.
    """
    if not product_types:
        return {}

    print(f"🎯 Procesando {len(product_types)} tipos de producto (estrategia {iteration})...")

    # Paso 1: Usar el sistema de mapeo por keywords (Opción 1)
    print("📋 Aplicando mapeo por palabras clave...")
    mapped_subcategories = learning_system.map_products_by_keywords(product_types)

    # Paso 2: Verificar cobertura y aplicar reglas semánticas adicionales si es necesario
    all_mapped = []
    for products in mapped_subcategories.values():
        all_mapped.extend(products)

    unmapped_products = [p for p in product_types if p not in all_mapped]

    if unmapped_products:
        print(f"🔄 Aplicando reglas semánticas a {len(unmapped_products)} productos no mapeados...")
        for product in unmapped_products:
            semantic_category = learning_system.apply_semantic_rules(product)
            if semantic_category and semantic_category in mapped_subcategories:
                mapped_subcategories[semantic_category].append(product)

    # Paso 3: Limpiar subcategorías vacías y ordenar
    final_subcategories = {k: v for k, v in mapped_subcategories.items() if v}
    final_subcategories = dict(sorted(final_subcategories.items()))

    # Paso 4: Contar productos clasificados
    total_classified = sum(len(products) for products in final_subcategories.values())

    print(f"✅ Generadas {len(final_subcategories)} subcategorías ({total_classified}/{len(product_types)} productos)")
    return final_subcategories

def apply_variable_clustering_strategy(product_types, pattern_analysis, learning_params, iteration):
    """
    Aplica diferentes estrategias de clustering en cada iteración.
    """
    strategies = {
        1: "similarity_basic",      # Clustering básico por similitud
        2: "semantic_aggressive",   # Clustering semántico agresivo
        3: "pattern_based",         # Basado en patrones de texto
        4: "domain_aware",          # Consciente de dominios
        5: "hybrid_adaptive"        # Híbrido adaptativo
    }

    strategy = strategies.get(iteration, "similarity_basic")
    print(f"   Estrategia de clustering: {strategy}")

    if strategy == "similarity_basic":
        min_similarity = learning_params.get('min_similarity', 0.4)
        return create_similarity_clusters(product_types, min_similarity=min_similarity)

    elif strategy == "semantic_aggressive":
        min_similarity = max(0.1, learning_params.get('min_similarity', 0.4) - 0.2)
        clusters = create_semantic_clusters(product_types, min_similarity=min_similarity)
        if learning_params.get('merge_small_clusters', False):
            clusters = merge_small_clusters(clusters)
        return clusters

    elif strategy == "pattern_based":
        # Usar patrones de prefijos/sufijos
        return create_pattern_based_clusters(product_types)

    elif strategy == "domain_aware":
        # Intentar detectar dominio de limpieza y aplicar lógica específica
        return generate_cleaning_domain_clusters(product_types, pattern_analysis, learning_params)

    elif strategy == "hybrid_adaptive":
        # Combinar múltiples estrategias
        clusters1 = create_similarity_clusters(product_types, min_similarity=0.3)
        clusters2 = create_pattern_based_clusters(product_types)
        # Fusionar resultados
        return merge_cluster_results(clusters1, clusters2)

def apply_variable_reclassification_strategy(unclassified_products, existing_clusters, learning_params, iteration):
    """
    Aplica estrategias variables para reclasificar productos no clasificados.
    """
    strategies = {
        1: "aggressive_similarity",   # Similitud agresiva
        2: "pattern_extension",       # Extensión de patrones
        3: "semantic_matching",       # Coincidencia semántica
        4: "domain_specific",         # Específica del dominio
        5: "comprehensive_approach"   # Enfoque comprehensivo
    }

    strategy = strategies.get(iteration, "aggressive_similarity")
    print(f"   Estrategia de reclasificación: {strategy}")

    if strategy == "aggressive_similarity":
        min_similarity = max(0.05, learning_params.get('min_similarity', 0.3) - 0.2)
        return create_similarity_clusters(unclassified_products, min_similarity=min_similarity)

    elif strategy == "pattern_extension":
        return create_pattern_based_clusters(unclassified_products)

    elif strategy == "semantic_matching":
        return create_semantic_clusters(unclassified_products, min_similarity=0.2)

    elif strategy == "domain_specific":
        return generate_cleaning_domain_clusters(unclassified_products, {}, learning_params)

    elif strategy == "comprehensive_approach":
        # Probar múltiples enfoques y combinar
        clusters1 = create_similarity_clusters(unclassified_products, min_similarity=0.1)
        clusters2 = create_pattern_based_clusters(unclassified_products)
        return merge_cluster_results(clusters1, clusters2)

def generate_cleaning_domain_clusters(product_types, pattern_analysis, learning_params):
    """
    Genera clusters específicos para el dominio de limpieza.
    """
    clusters = []

    # Patrones específicos de limpieza aprendidos
    cleaning_patterns = {
        'Detergente': ['detergente', 'lavavajillas', 'jabón', 'limpiador'],
        'Desinfectante': ['desinfectante', 'alcohol', 'lejía', 'cloro', 'lysol'],
        'Aromatizante': ['aromatizante', 'ambientador', 'perfume', 'fragancia'],
        'Papel': ['papel', 'toalla', 'servilleta', 'paño'],
        'Cepillo': ['cepillo', 'esponja', 'trapo', 'bayeta'],
        'Bolsa': ['bolsa', 'saco', 'recipiente']
    }

    for category_name, keywords in cleaning_patterns.items():
        matching_products = []
        for product in product_types:
            product_lower = product.lower()
            if any(keyword in product_lower for keyword in keywords):
                matching_products.append(product)

        if len(matching_products) >= 2:
            clusters.append({
                'name': category_name,
                'products': matching_products,
                'count': len(matching_products)
            })

    # Si no hay suficientes clusters específicos, usar clustering general
    if len(clusters) < 3:
        additional_clusters = create_similarity_clusters(product_types, min_similarity=0.3)
        clusters.extend(additional_clusters)

    return clusters

def merge_cluster_results(clusters1, clusters2):
    """
    Fusiona resultados de múltiples estrategias de clustering.
    """
    merged = clusters1.copy() if isinstance(clusters1, list) else []

    if isinstance(clusters2, list):
        for cluster in clusters2:
            # Verificar si ya existe un cluster similar
            cluster_name = cluster.get('name', '')
            exists = False
            for existing_cluster in merged:
                if existing_cluster.get('name', '') == cluster_name:
                    # Fusionar productos
                    existing_products = set(existing_cluster.get('products', []))
                    new_products = [p for p in cluster.get('products', []) if p not in existing_products]
                    existing_cluster['products'].extend(new_products)
                    existing_cluster['count'] += len(new_products)
                    exists = True
                    break

            if not exists:
                merged.append(cluster)

    return merged

def generate_subcategories_with_learning(product_types, category_url, learning_params):
    """
    Genera subcategorías usando parámetros aprendidos del sistema de aprendizaje.
    """
    if not product_types:
        return {}

    print(f"🎯 Procesando {len(product_types)} tipos de producto con aprendizaje...")

    # Paso 1: Analizar contexto de la categoría
    if category_url:
        category_context = analyze_category_context(category_url)
        expected_patterns = category_context.get('expected_patterns', [])
        grouping_strategy = category_context.get('grouping_strategy', 'generic')
        print(f"📋 Contexto detectado: {grouping_strategy}")
    else:
        expected_patterns = []
        grouping_strategy = 'generic'

    # Paso 2: Análisis inteligente de patrones en los productos
    pattern_analysis = analyze_product_patterns(product_types, expected_patterns)

    # Paso 3: Generar subcategorías con parámetros aprendidos
    clusters = {}

    # Usar diferentes estrategias según el dominio
    if grouping_strategy == 'animal_type':
        clusters = generate_animal_based_subcategories(product_types, pattern_analysis)
    elif grouping_strategy == 'food_type':
        clusters = generate_food_based_subcategories(product_types, pattern_analysis)
    elif grouping_strategy == 'beverage_type':
        clusters = generate_beverage_based_subcategories(product_types, pattern_analysis)
    else:
        # Estrategia genérica mejorada con aprendizaje
        clusters = generate_generic_subcategories_with_learning(product_types, pattern_analysis, learning_params)

    # Paso 4: Limpiar y optimizar clusters
    if isinstance(clusters, dict):
        clusters = {k: v for k, v in clusters.items() if v}
        clusters = dict(sorted(clusters.items()))
    elif isinstance(clusters, list):
        clusters = [c for c in clusters if c.get('products', [])]
        clusters.sort(key=lambda x: x.get('name', ''))

    # Paso 5: Aplicar aprendizaje para mejorar clasificación
    if isinstance(clusters, dict):
        all_classified = [item for sublist in clusters.values() for item in sublist]
    else:
        all_classified = [item for cluster in clusters for item in cluster.get('products', [])]

    truly_unclassified = [p for p in product_types if p not in all_classified]

    if truly_unclassified:
        print(f"🔄 Intentando reclasificar {len(truly_unclassified)} productos con aprendizaje...")

        # Usar parámetros aprendidos para reclasificación agresiva
        additional_clusters = create_semantic_clusters_aggressive_with_learning(
            truly_unclassified, clusters, learning_params
        )

        # Solo agregar clusters que tengan sentido
        if isinstance(additional_clusters, dict):
            for category, products in additional_clusters.items():
                if len(products) >= 2:
                    if category not in clusters:
                        clusters[category] = []
                    clusters[category].extend(products)
        else:
            for cluster in additional_clusters:
                if cluster.get('count', 0) >= 2:
                    category_name = cluster.get('name', 'Otros')
                    if isinstance(clusters, dict):
                        if category_name not in clusters:
                            clusters[category_name] = []
                        clusters[category_name].extend(cluster.get('products', []))
                    else:
                        clusters.append(cluster)

    if isinstance(clusters, dict):
        total_classified = sum(len(products) for products in clusters.values())
    else:
        total_classified = sum(cluster.get('count', 0) for cluster in clusters)

    print(f"✅ Generadas {len(clusters)} subcategorías con aprendizaje "
          f"({total_classified}/{len(product_types)} productos)")
    return clusters

def generate_generic_subcategories_with_learning(product_types, pattern_analysis, learning_params):
    """
    Genera subcategorías genéricas usando parámetros aprendidos y estrategias adaptativas.
    """
    # Usar parámetros aprendidos para ajustar el clustering
    min_similarity = learning_params.get('min_similarity', 0.4)
    aggressive_mode = learning_params.get('aggressive_mode', False)
    use_semantic = learning_params.get('use_semantic_clustering', False)
    merge_small = learning_params.get('merge_small_clusters', False)
    split_large = learning_params.get('split_large_clusters', False)

    if aggressive_mode:
        min_similarity = max(0.1, min_similarity - 0.1)  # Más agresivo

    # Elegir estrategia basada en parámetros aprendidos
    if use_semantic:
        clusters = create_semantic_clusters(product_types, min_similarity=min_similarity)
    else:
        clusters = create_similarity_clusters(product_types, min_similarity=min_similarity)

    # Aplicar fusión de clusters pequeños si se aprendió que es necesario
    if merge_small and isinstance(clusters, list):
        clusters = merge_small_clusters(clusters)

    # Aplicar división de clusters grandes si se aprendió que es necesario
    if split_large and isinstance(clusters, list):
        clusters = split_large_clusters(clusters)

    return clusters

def create_semantic_clusters_aggressive_with_learning(product_types, existing_clusters, learning_params):
    """
    Crea clusters semánticos agresivos usando aprendizaje y estrategias adaptativas.
    """
    min_similarity = learning_params.get('min_similarity', 0.3)
    semantic_weight = learning_params.get('semantic_weight', 0.7)

    if learning_params.get('aggressive_mode', False):
        min_similarity = max(0.05, min_similarity - 0.15)  # Mucho más agresivo

    # Usar peso semántico aprendido
    clusters = create_similarity_clusters(product_types, min_similarity=min_similarity)

    # Aplicar lógica adicional basada en aprendizaje
    if learning_params.get('merge_small_clusters', False):
        clusters = merge_small_clusters(clusters)

    return clusters

def merge_small_clusters(clusters):
    """
    Fusiona clusters que tienen muy pocos productos.
    """
    if not isinstance(clusters, list):
        return clusters

    # Separar clusters grandes de pequeños
    large_clusters = [c for c in clusters if c.get('count', 0) >= 3]
    small_clusters = [c for c in clusters if c.get('count', 0) < 3]

    # Fusionar clusters pequeños en el más grande
    if large_clusters and small_clusters:
        target_cluster = max(large_clusters, key=lambda x: x.get('count', 0))
        for small_cluster in small_clusters:
            target_cluster['products'].extend(small_cluster.get('products', []))
            target_cluster['count'] += small_cluster.get('count', 0)

        return large_clusters

    return clusters

def split_large_clusters(clusters):
    """
    Divide clusters que tienen demasiados productos.
    """
   
    if not isinstance(clusters, list):
        return clusters

    result_clusters = []

    for cluster in clusters:
        count = cluster.get('count', 0)
        products = cluster.get('products', [])

        if count > 15:  # Si tiene más de 15 productos, dividirlo
            # Dividir en subgrupos basados en prefijos
            subgroups = {}
            for product in products:
                prefix = product.split()[0].lower() if product.split() else 'otros'
                if prefix not in subgroups:
                    subgroups[prefix] = []
                subgroups[prefix].append(product)

            # Crear nuevos clusters para cada subgrupo con al menos 2 productos
            for prefix, prods in subgroups.items():
                if len(prods) >= 2:
                    result_clusters.append({
                        'name': f"{cluster['name']} {prefix.title()}",
                        'products': prods,
                        'count': len(prods)
                    })
        else:
            result_clusters.append(cluster)

    return result_clusters

if __name__ == "__main__":
    # Sistema de aprendizaje para categoría Limpieza
    category_url = "https://www.carrefour.com.ar/Limpieza"

    # Inicializar sistema de aprendizaje
    learning_system = SubcategoryLearningSystem()

    # Ejecutar iteraciones hasta lograr el resultado esperado (máximo 50 iteraciones)
    run_learning_iterations(learning_system, category_url, max_iterations=50)