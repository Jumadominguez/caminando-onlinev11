import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

def extract_and_analyze_product_types(category_url):
    """
    Extrae y analiza todos los tipos de producto de la categoría Limpieza de Carrefour.
    Muestra estadísticas detalladas para diagnosticar por qué no se clasifican ciertas subcategorías.
    """
    # Configurar opciones de Firefox
    options = Options()
    options.headless = False

    driver = webdriver.Firefox(options=options)
    product_types = []

    try:
        driver.get(category_url)

        # Esperar a que la página cargue
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "valtech-carrefourar-search-result-3-x-filter__container--tipo-de-producto"))
        )

        # Expandir filtro
        containers = driver.find_elements(By.CLASS_NAME, "valtech-carrefourar-search-result-3-x-filter__container--tipo-de-producto")
        if not containers:
            print("❌ No se encontró contenedor de tipos de producto")
            return []

        container = containers[0]

        # Cerrar modal si existe
        try:
            modal_close = driver.find_element(By.CLASS_NAME, "dy-modal-close")
            modal_close.click()
            time.sleep(1)
        except:
            pass

        # Expandir filtro
        try:
            filter_title = container.find_element(By.XPATH, ".//span[contains(text(), 'Tipo de producto')]")
            driver.execute_script("arguments[0].click();", filter_title)
            time.sleep(3)
        except:
            try:
                driver.execute_script("arguments[0].click();", container)
                time.sleep(3)
            except:
                pass

        # Ver más si existe
        try:
            see_more_button = container.find_element(By.CLASS_NAME, "valtech-carrefourar-search-result-3-x-seeMoreButton")
            driver.execute_script("arguments[0].click();", see_more_button)
            time.sleep(3)
        except:
            pass

        # Extraer productos
        labels = container.find_elements(By.CLASS_NAME, "vtex-checkbox__label")

        for label in labels:
            text = label.text
            clean_text = re.sub(r'\s*\(\d+\)$', '', text).strip()
            if clean_text:
                product_types.append(clean_text)

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        driver.quit()

    return product_types

def analyze_missing_subcategories(product_types):
    """
    Analiza por qué no se clasifican las subcategorías faltantes.
    """
    print("\n" + "="*80)
    print("🔍 ANÁLISIS DE SUBCATEGORÍAS FALTANTES")
    print("="*80)

    missing_categories = {
        'Jabones para la ropa': {
            'keywords': ['jabon', 'jabón', 'ropa', 'lavado', 'barra', 'polvo', 'pan'],
            'semantic_rules': lambda p: any(word in p.lower() for word in ['jabon', 'jabón']) and any(word in p.lower() for word in ['ropa', 'lavado', 'barra', 'polvo', 'pan'])
        },
        'Limpiadores líquidos': {
            'keywords': ['limpia', 'limpiador', 'antigrasa', 'desengrasante', 'quita grasa', 'multiples superficies', 'liquido', 'líquido'],
            'semantic_rules': lambda p: any(word in p.lower() for word in ['limpia', 'limpiador', 'antigrasa', 'desengrasante', 'quita grasa', 'multiples superficies', 'liquido', 'líquido']) and not any(word in p.lower() for word in ['cremoso', 'pasta', 'baño', 'piso', 'vidrio', 'mueble'])
        },
        'Lustramuebles': {
            'keywords': ['lustrador', 'lustramuebles', 'abrillantador', 'cera', 'mueble', 'madera', 'metal'],
            'semantic_rules': lambda p: any(word in p.lower() for word in ['lustrador', 'lustramuebles', 'abrillantador', 'cera']) and any(word in p.lower() for word in ['mueble', 'madera', 'metal'])
        },
        'Prelavado y quitamanchas': {
            'keywords': ['prelavado', 'quita manchas', 'quitamanchas', 'removedor', 'tratamiento manchas', 'detergente', 'manchas', 'prelavado', 'ropa'],
            'semantic_rules': lambda p: any(word in p.lower() for word in ['prelavado', 'quita manchas', 'quitamanchas', 'removedor', 'tratamiento manchas', 'detergente']) and any(word in p.lower() for word in ['manchas', 'prelavado', 'ropa'])
        }
    }

    print(f"📊 Total productos extraídos: {len(product_types)}")
    print(f"📋 Productos encontrados: {product_types[:10]}{'...' if len(product_types) > 10 else ''}")

    for category, rules in missing_categories.items():
        print(f"\n🔎 Analizando: {category}")
        print("-" * 50)

        # Buscar productos que coincidan con keywords
        keyword_matches = []
        semantic_matches = []

        for product in product_types:
            product_lower = product.lower()

            # Verificar keywords
            keyword_score = 0
            for keyword in rules['keywords']:
                if keyword in product_lower:
                    keyword_score += 1

            if keyword_score > 0:
                keyword_matches.append((product, keyword_score))

            # Verificar reglas semánticas
            if rules['semantic_rules'](product):
                semantic_matches.append(product)

        print(f"  📝 Productos con keywords ({len(keyword_matches)}):")
        for product, score in sorted(keyword_matches, key=lambda x: x[1], reverse=True)[:5]:
            print(f"    • {product} (score: {score})")

        print(f"  🧠 Productos por reglas semánticas ({len(semantic_matches)}):")
        for product in semantic_matches[:5]:
            print(f"    • {product}")

        if not keyword_matches and not semantic_matches:
            print("  ❌ NINGÚN PRODUCTO ENCONTRADO PARA ESTA SUBCATEGORÍA")

# URL de la categoría Limpieza de Carrefour
limpieza_url = "https://www.carrefour.com.ar/limpieza"

print("🚀 Extrayendo productos de la categoría Limpieza de Carrefour...")
product_types = extract_and_analyze_product_types(limpieza_url)

if product_types:
    analyze_missing_subcategories(product_types)
else:
    print("❌ No se pudieron extraer productos")