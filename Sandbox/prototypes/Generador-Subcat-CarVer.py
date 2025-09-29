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
    clusters = {}
    for product_type in product_types:
        # Crear cluster basado en primera palabra
        key = product_type.split()[0].lower()
        if key not in clusters:
            clusters[key] = []
        clusters[key].append(product_type)

    # Convertir a formato esperado
    result = []
    for key, items in clusters.items():
        if len(items) > 1:
            result.append({
                'name': key.title(),
                'products': items,
                'count': len(items)
            })

    return result

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

if __name__ == "__main__":
    # Ejemplo de uso - cambiar la URL según la categoría que se quiera analizar
    category_url = "https://www.carrefour.com.ar/Almacen"
    analyze_category_and_generate_subcategories(category_url)