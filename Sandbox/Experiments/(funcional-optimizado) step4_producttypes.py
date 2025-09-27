#!/usr/bin/env python3
"""
Script para procesar la                 accept_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Aceptar') or contains(text(), 'Accept') or contains(text(), 'OK')]")
        for btn in accept_buttons:
            try:
                btn.click()
                logging.info("Clicked cookie accept button")
                time.sleep(1)
                break categoría de Carrefour sigu                return False
            else:
                logging.warning(f"Intento {attempt + 1}: No se pudo re-expandir menú de subcategorías")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continuelas instrucciones detalladas
VERSIÓN LIMITADA PARA TESTING: Solo procesa categoría "Bebidas" y primeras 3 subcategorías
Basado en el proceso documentado en proceso-detallado-carrefour-step4.md
"""
import time
import logging
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pymongo import MongoClient
from datetime import datetime
import re
import unicodedata

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_slug(text):
    """Generate a URL-friendly slug from text"""
    # Normalize unicode characters (remove accents)
    text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8')
    # Convert to lowercase
    text = text.lower()
    # Replace spaces and non-alphanumeric characters with hyphens
    text = re.sub(r'[^a-z0-9]+', '-', text)
    # Remove multiple consecutive hyphens
    text = re.sub(r'-+', '-', text)
    # Strip leading/trailing hyphens
    text = text.strip('-')
    return text

def setup_driver():
    """Setup Firefox WebDriver in HEADLESS mode for production"""
    firefox_options = Options()
    # HEADLESS mode for production - no GUI
    firefox_options.add_argument("--headless")
    firefox_options.add_argument("--no-sandbox")
    firefox_options.add_argument("--disable-dev-shm-usage")
    firefox_options.add_argument("--window-size=1920,1080")

    geckodriver_path = r"d:\dev\caminando-onlinev10\geckodriver_temp\geckodriver.exe"
    service = Service(geckodriver_path)
    driver = webdriver.Firefox(service=service, options=firefox_options)
    logging.info("WebDriver initialized successfully (HEADLESS mode)")
    return driver

def handle_cookies(driver):
    """Handle cookie popup if present"""
    try:
        accept_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Aceptar') or contains(text(), 'Accept') or contains(text(), 'OK')]")
        for btn in accept_buttons:
            try:
                btn.click()
                logging.info("Clicked cookie accept button")
                time.sleep(2)
                break
            except:
                continue
    except Exception as e:
        logging.warning(f"Could not handle cookie popup: {e}")

def open_filters_panel(driver):
    """Open the filters panel if not already open"""
    try:
        filters_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Filtrar')]"))
        )
        filters_button.click()
        logging.info("Opened filters panel")
        time.sleep(1)
    except:
        logging.info("Filters panel already open or no button found")

def scroll_to_load_filters(driver):
    """Scroll down to ensure filters are loaded"""
    driver.execute_script("window.scrollTo(0, 500);")
    time.sleep(2)

def get_all_categories():
    """Get all categories from MongoDB categories collection"""
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['carrefour']
        collection = db['categories']

        # Get all categories sorted by _id
        categories = list(collection.find({}, {'name': 1, 'url': 1, '_id': 0}, sort=[('_id', 1)]))

        client.close()

        if categories:
            logging.info(f"✓ Retrieved {len(categories)} categories from database:")
            for i, cat in enumerate(categories, 1):
                logging.info(f"  {i}. {cat.get('name')} -> {cat.get('url')}")
            return categories
        else:
            logging.error("No categories found in database")
            return []

    except Exception as e:
        logging.error(f"Error retrieving categories from database: {e}")
        return []

def expand_subcategory_menu_if_collapsed(driver):
    """Expandir el menú de subcategorías usando la función genérica"""
    return expand_menu_if_collapsed(
        driver,
        "div.valtech-carrefourar-search-result-3-x-filter__container--category-3, div[data-testid*='category'], div.filter__container--category"
    )

def scroll_and_click_ver_mas(driver, container, button_text="ver más"):
    """Función genérica para hacer scroll y click en botones 'Ver más'"""
    try:
        # Scroll to the bottom of the container
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", container)
        time.sleep(1)

        # Look for button with multiple selectors
        selectors = [
            "button.valtech-carrefourar-search-result-3-x-seeMoreButton",
            "span.vtex-button__label",
            f"button:contains('{button_text}')",
            f"//button[contains(text(), '{button_text}')]",
            f"//span[contains(text(), '{button_text}')]"
        ]

        for selector in selectors:
            try:
                if selector.startswith("//"):
                    buttons = driver.find_elements(By.XPATH, selector)
                else:
                    buttons = driver.find_elements(By.CSS_SELECTOR, selector)

                for btn in buttons:
                    text = btn.text.lower()
                    if button_text in text or button_text.replace("más", "mas") in text:
                        driver.execute_script("arguments[0].scrollIntoView();", btn)
                        time.sleep(0.5)
                        driver.execute_script("arguments[0].click();", btn)
                        time.sleep(3)
                        return True
            except:
                continue

        return False

    except Exception as e:
        logging.error(f"Error scrolling and clicking '{button_text}': {e}")
        return False

def expand_menu_if_collapsed(driver, container_selector, button_selector=None):
    """Función genérica para expandir cualquier menú si está colapsado"""
    try:
        # Find the container
        container = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, container_selector))
        )

        if not container:
            return None

        # Check if there's an expand button
        try:
            if button_selector:
                expand_button = container.find_element(By.CSS_SELECTOR, button_selector)
            else:
                expand_button = container.find_element(By.CSS_SELECTOR, "div[role='button']")

            if expand_button and expand_button.is_displayed():
                driver.execute_script("arguments[0].scrollIntoView();", expand_button)
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", expand_button)
                time.sleep(1)
                return container
        except:
            pass  # Menu already expanded

        return container

    except Exception as e:
        logging.error(f"Error expanding menu with selector {container_selector}: {e}")
        return None

def count_product_types(driver):
    """Contar el número total de opciones en el filtro 'Tipo de Producto'"""
    try:
        # Find the product types container
        product_types_container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.valtech-carrefourar-search-result-3-x-filter__container--tipo-de-producto"))
        )

        # Try multiple selectors for product type checkboxes
        checkbox_selectors = [
            "input[type='checkbox'][id^='tipo-de-producto-']",
            "input[type='checkbox']",
            ".valtech-carrefourar-search-result-3-x-filter__checkbox input[type='checkbox']",
            "input[id*='tipo-de-producto']"
        ]

        checkboxes = []
        for selector in checkbox_selectors:
            try:
                elements = product_types_container.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    checkboxes = elements
                    break
            except Exception as e:
                logging.debug(f"Selector {selector} failed: {e}")
                continue

        count = len(checkboxes)
        logging.info(f"✓ Counted {count} product type options")
        return count

    except Exception as e:
        logging.error(f"Error counting product types: {e}")
        return 0

def process_all_subcategories(driver, category_name, category_url):
    """Procesar todas las subcategorías de una categoría, extrayendo tipos de producto para cada una"""
    try:
        # NO guardamos las checkboxes al inicio porque se vuelven stale después del refresh
        # En su lugar, las obtendremos en cada iteración después del refresh

        # Obtener el número total de subcategorías UNA SOLA VEZ al inicio
        subcategory_container = expand_subcategory_menu_if_collapsed(driver)
        if not subcategory_container:
            logging.error("No se pudo encontrar el contenedor de subcategorías")
            return False

        temp_checkboxes = subcategory_container.find_elements(By.CSS_SELECTOR, "input[type='checkbox'][id^='category-3-']")
        total_subcategories = len(temp_checkboxes)
        logging.info(f"✓ Encontradas {total_subcategories} subcategorías para procesar")

        # LIMITAR A SOLO LAS PRIMERAS 3 SUBCATEGORÍAS
        max_subcategories = min(3, total_subcategories)
        logging.info(f"✓ Procesando solo las primeras {max_subcategories} subcategorías (limitado por configuración)")

        # Procesar cada subcategoría
        for subcategory_index in range(max_subcategories):
            logging.info(f"Procesando subcategoría {subcategory_index + 1}/{max_subcategories}")

            # DESPUÉS DE CADA REFRESH: VOLVER A OBTENER LAS CHECKBOXES DEL DOM ACTUALIZADO
            subcategory_container = expand_subcategory_menu_if_collapsed(driver)
            if not subcategory_container:
                logging.warning(f"No se pudo re-expandir el menú de subcategorías para subcategoría {subcategory_index + 1}")
                continue

            checkboxes = subcategory_container.find_elements(By.CSS_SELECTOR, "input[type='checkbox'][id^='category-3-']")
            if subcategory_index >= len(checkboxes):
                logging.warning(f"No se pudo acceder a la subcategoría {subcategory_index + 1} (índice fuera de rango)")
                continue

            # Limpiar cualquier selección previa
            for checkbox in checkboxes:
                if checkbox.is_selected():
                    driver.execute_script("arguments[0].click();", checkbox)
                    time.sleep(0.3)

            # Seleccionar la subcategoría actual
            current_checkbox = checkboxes[subcategory_index]
            input_id = current_checkbox.get_attribute("id")

            # Obtener nombre de la subcategoría
            try:
                label = driver.find_element(By.CSS_SELECTOR, f"label[for='{input_id}']")
                subcategory_name = label.get_attribute("textContent").strip()
                subcategory_name = subcategory_name.split('(')[0].strip()  # Remove count if present
            except:
                subcategory_name = f"Subcategory_{input_id}"

            logging.info(f"Seleccionando subcategoría: {subcategory_name}")

            # Hacer scroll y seleccionar
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", current_checkbox)
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", current_checkbox)
            logging.info(f"✓ Subcategoría '{subcategory_name}' seleccionada")

            # Aplicar el filtro
            aplicar_selectors = [
                "div.vtex-button__label",
                "button[class*='Aplicar']",
                "button:contains('Aplicar')",
                "//button[contains(text(), 'Aplicar')]",
                "//div[contains(text(), 'Aplicar')]",
                "//span[contains(text(), 'Aplicar')]"
            ]

            filter_applied = False
            for selector in aplicar_selectors:
                try:
                    if selector.startswith("//"):
                        elements = driver.find_elements(By.XPATH, selector)
                    else:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)

                    for element in elements:
                        text = element.text.lower()
                        if "aplicar" in text:
                            driver.execute_script("arguments[0].scrollIntoView();", element)
                            time.sleep(1)
                            driver.execute_script("arguments[0].click();", element)
                            logging.info("✓ Filtro aplicado")
                            time.sleep(2)  # Reducido de 3 a 2 segundos

                            # Usar la función segura para refresh y reabrir filtros
                            if not safe_refresh_and_reopen_filters(driver):
                                logging.error(f"No se pudo refrescar y reabrir filtros para subcategoría '{subcategory_name}'")
                                continue

                            filter_applied = True
                            break
                    if filter_applied:
                        break
                except Exception as e:
                    logging.debug(f"Selector {selector} failed: {e}")
                    continue

            if not filter_applied:
                logging.error(f"No se pudo aplicar el filtro para subcategoría '{subcategory_name}'")
                continue

            # Extraer y guardar tipos de producto para esta subcategoría
            logging.info(f"Extrayendo tipos de producto para subcategoría '{subcategory_name}'...")

            # Expandir menú de tipos de producto
            product_types_container = expand_product_type_menu(driver)
            if not product_types_container:
                logging.warning(f"No se pudo expandir menú de tipos de producto para '{subcategory_name}'")
                continue

            # ESPERAR un poco más para que se carguen dinámicamente todas las opciones después de expandir
            time.sleep(3)

            # Hacer scroll y buscar botón "Ver más"
            scroll_and_click_ver_mas_product_types(driver, product_types_container)

            # Extraer nombres de tipos de producto
            product_type_names = extract_product_type_names(driver)
            if not product_type_names:
                logging.warning(f"No se pudieron extraer tipos de producto para '{subcategory_name}'")
                continue

            # Extraer cantidad total de productos
            product_count = extract_product_count(driver)

            # Guardar en base de datos
            saved_count = save_product_types_to_db(product_type_names, category_name, subcategory_name, category_url, product_count)

        return True

    except Exception as e:
        logging.error(f"Error procesando subcategorías: {e}")
        return False

def safe_refresh_and_reopen_filters(driver, max_retries=3):
    """Función segura para refrescar página y reabrir filtros con reintentos"""
    for attempt in range(max_retries):
        try:
            logging.info(f"✓ Actualizando página después de aplicar filtro (intento {attempt + 1}/{max_retries})...")
            driver.refresh()
            time.sleep(3)  # Reducido de 5 a 3 segundos
            logging.info("✓ Página actualizada - filtros deberían estar cargados dinámicamente")

            # Reabrir panel de filtros después del refresh
            logging.info("⏳ Reabriendo panel de filtros después del refresh...")
            open_filters_panel(driver)
            scroll_to_load_filters(driver)

            # Re-expandir el menú de subcategorías después del refresh
            subcategory_container = expand_subcategory_menu_if_collapsed(driver)
            if subcategory_container:
                scroll_and_click_ver_mas(driver, subcategory_container, "ver más")
                return True
            else:
                logging.warning(f"Intento {attempt + 1}: No se pudo re-expandir menú de subcategorías")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                return False

        except Exception as e:
            logging.warning(f"Intento {attempt + 1} falló: {e}")
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
            return False

    return False

def expand_product_type_menu(driver):
    """Expandir el menú de tipos de producto usando la función genérica"""
    return expand_menu_if_collapsed(
        driver,
        "div.valtech-carrefourar-search-result-3-x-filter__container--tipo-de-producto, div[data-testid*='tipo-de-producto'], div.filter__container--tipo-de-producto"
    )

def scroll_and_click_ver_mas_product_types(driver, product_types_container):
    """Hacer scroll hasta el final de 'Tipo de Producto' y encontrar botón 'Ver Mas N'"""
    try:
        # Scroll to the bottom of the container
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", product_types_container)
        time.sleep(1)
        logging.info("Scrolled to bottom of product types menu")

        # Look for "Ver más" or "Ver mas" button - try multiple selectors
        ver_mas_selectors = [
            "span.vtex-button__label",
            "button.valtech-carrefourar-search-result-3-x-seeMoreButton",
            "button:contains('Ver más')",
            "button:contains('Ver mas')",
            "//button[contains(text(), 'Ver más')]",
            "//button[contains(text(), 'Ver mas')]",
            "//span[contains(text(), 'Ver más')]",
            "//span[contains(text(), 'Ver mas')]"
        ]

        for selector in ver_mas_selectors:
            try:
                if selector.startswith("//"):
                    buttons = driver.find_elements(By.XPATH, selector)
                else:
                    buttons = driver.find_elements(By.CSS_SELECTOR, selector)

                for btn in buttons:
                    text = btn.text.lower()
                    if "ver más" in text or "ver mas" in text:
                        driver.execute_script("arguments[0].scrollIntoView();", btn)
                        time.sleep(0.5)
                        driver.execute_script("arguments[0].click();", btn)
                        logging.info(f"✓ Clicked 'Ver más' button for product types: '{btn.text}'")
                        time.sleep(3)
                        return True

            except Exception as e:
                logging.debug(f"Selector {selector} failed: {e}")
                continue

        logging.info("No 'Ver más' button found for product types")
        return False

    except Exception as e:
        logging.error(f"Error scrolling and clicking 'Ver más' for product types: {e}")
        return False

def extract_product_type_names(driver):
    """Extraer los nombres de todos los tipos de producto disponibles"""
    try:
        # Find the product types container
        product_types_container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.valtech-carrefourar-search-result-3-x-filter__container--tipo-de-producto"))
        )

        # Try multiple selectors for product type checkboxes
        checkbox_selectors = [
            "input[type='checkbox'][id^='tipo-de-producto-']",
            "input[type='checkbox']",
            ".valtech-carrefourar-search-result-3-x-filter__checkbox input[type='checkbox']",
            "input[id*='tipo-de-producto']"
        ]

        checkboxes = []
        for selector in checkbox_selectors:
            try:
                elements = product_types_container.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    checkboxes = elements
                    break
            except Exception as e:
                logging.debug(f"Selector {selector} failed: {e}")
                continue

        if not checkboxes:
            logging.warning("No product type checkboxes found")
            return []

        product_type_names = []
        logging.info(f"Extracting names from {len(checkboxes)} product type checkboxes")

        for i, checkbox in enumerate(checkboxes):
            try:
                input_id = checkbox.get_attribute("id")

                # Try to extract product type name from label
                try:
                    label = driver.find_element(By.CSS_SELECTOR, f"label[for='{input_id}']")
                    product_type_name = label.get_attribute("textContent").strip()

                    if product_type_name:
                        # Clean the name (remove extra spaces, etc.)
                        product_type_name = ' '.join(product_type_name.split())
                        # Remove the number in parentheses (e.g., "Cargador portátil (18)" -> "Cargador portátil")
                        if '(' in product_type_name and ')' in product_type_name:
                            product_type_name = product_type_name.split('(')[0].strip()
                        product_type_names.append(product_type_name)
                        logging.debug(f"Extracted product type {i+1}: '{product_type_name}'")

                except Exception as e:
                    logging.debug(f"Could not extract label for checkbox {input_id}: {e}")
                    continue

            except Exception as e:
                logging.debug(f"Error processing checkbox {i+1}: {e}")
                continue

        logging.info(f"✓ Successfully extracted {len(product_type_names)} product type names")
        return product_type_names

    except Exception as e:
        logging.error(f"Error extracting product type names: {e}")
        return []

def extract_product_count(driver):
    """Extraer la cantidad total de productos del elemento específico"""
    try:
        # Selector del elemento que contiene el conteo
        selector = "div.valtech-carrefourar-search-result-3-x-totalProducts--layout"
        
        # Esperar a que el elemento esté presente
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )
        
        # Extraer el texto del span interno
        span_element = element.find_element(By.CSS_SELECTOR, "span")
        text = span_element.text.strip()
        
        # Extraer el número (primer parte antes del espacio)
        count_str = text.split()[0]
        
        # Convertir a int
        try:
            product_count = int(count_str)
            logging.info(f"✓ Extracted product count: {product_count}")
            return product_count
        except ValueError:
            logging.warning(f"Could not convert '{count_str}' to integer")
            return 0
            
    except Exception as e:
        logging.warning(f"Could not extract product count: {e}")
        return 0

def save_product_type_to_db(product_type_name, subcategory_name, category_name, category_url, product_count):
    """Save or update the product type to MongoDB producttypes collection (avoid duplicates)"""
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['carrefour']
        collection = db['producttypes']

        # Create simplified name (name is already cleaned in extract_product_type_names)
        simplified_name = product_type_name

        # Generate slugs
        category_slug = generate_slug(category_name)
        type_slug = generate_slug(product_type_name)

        # Generate type_url
        type_url = f"https://www.carrefour.com.ar/{category_slug}?initialMap=c&initialQuery={category_slug}&map=category-1,tipo-de-producto&query=/{category_slug}/{type_slug}&searchState"

        # Use upsert to replace if exists or insert if not
        filter_query = {
            'name': product_type_name,
            'subcategory': subcategory_name,
            'category': category_name
        }

        document = {
            'name': product_type_name,
            'simplified_name': simplified_name,
            'subcategory': subcategory_name,
            'category': category_name,
            'type_slug': type_slug,
            'type_url': type_url,
            'product_count': product_count,
            'extracted_at': datetime.now()
        }

        result = collection.update_one(filter_query, {'$set': document}, upsert=True)
        if result.upserted_id:
            logging.info(f"✓ Inserted new product type '{product_type_name}' to database (ID: {result.upserted_id})")
        else:
            logging.info(f"✓ Updated existing product type '{product_type_name}' in database")

        client.close()
        return True

    except Exception as e:
        logging.error(f"Error saving/updating product type to database: {e}")
        return False

def save_product_types_to_db(product_type_names, category_name, subcategory_name, category_url, product_count):
    """Save multiple product types to database, returning count of successfully saved items"""
    if not product_type_names:
        logging.warning("No product type names to save")
        return 0

    saved_count = 0
    for product_type_name in product_type_names:
        if save_product_type_to_db(product_type_name, subcategory_name, category_name, category_url, product_count):
            saved_count += 1

    logging.info(f"✓ Successfully saved {saved_count} out of {len(product_type_names)} product types to database")
    return saved_count

def main():
    """Main function following the detailed process from the .md file - processes ALL categories"""
    driver = None

    try:
        logging.info("=== INICIANDO SCRIPT LIMITADO PARA TESTING ===")
        logging.info("Versión limitada: Solo procesa categoría 'Bebidas' y primeras 3 subcategorías")

        # PASO 1: Inicialización y Configuración
        logging.info("PASO 1: Inicialización y Configuración del WebDriver Firefox...")
        driver = setup_driver()

        # PASO 2: Obtención de TODAS las Categorías desde Base de Datos
        logging.info("PASO 2: Obtención de TODAS las Categorías desde Base de Datos...")
        all_categories = get_all_categories()
        if not all_categories:
            logging.error("No se pudieron obtener las categorías")
            return

        # FILTRAR SOLO LA CATEGORÍA "BEBIDAS"
        categories = [cat for cat in all_categories if cat.get('name', '').lower() == 'bebidas']
        if not categories:
            logging.error("No se encontró la categoría 'Bebidas' en la base de datos")
            logging.info("Categorías disponibles:")
            for cat in all_categories:
                logging.info(f"  - {cat.get('name')}")
            return

        logging.info(f"✓ Filtrada categoría 'Bebidas' para procesamiento limitado")
        total_categories = len(categories)
        logging.info(f"Iniciando procesamiento de {total_categories} categorías")

        # Procesar cada categoría
        for category_index, category in enumerate(categories, 1):
            category_name = category.get('name')
            category_url = category.get('url')

            logging.info(f"Procesando categoría {category_index}/{total_categories}: {category_name}")

            try:
                # PASO 3: Navegación a la Categoría
                logging.info(f"PASO 3: Navegación a la Categoría '{category_name}'...")
                driver.get(category_url)
                time.sleep(5)

                # Handle cookies (solo en la primera categoría)
                if category_index == 1:
                    handle_cookies(driver)

                # PASO 4: Apertura del Panel de Filtros
                logging.info("PASO 4: Apertura del Panel de Filtros...")
                open_filters_panel(driver)

                # PASO 5: Carga de Filtros
                logging.info("PASO 5: Carga de Filtros...")
                scroll_to_load_filters(driver)

                # PASO 6: Expansión del Menú de Subcategorías
                logging.info("PASO 6: Expansión del Menú de Subcategorías...")
                subcategory_container = expand_subcategory_menu_if_collapsed(driver)
                if not subcategory_container:
                    logging.error(f"No se pudo encontrar el contenedor de subcategorías para '{category_name}'")
                    continue

                # PASO 7: Expansión Completa de Subcategorías
                logging.info("PASO 7: Expansión Completa de Subcategorías (Ver más)...")
                scroll_and_click_ver_mas(driver, subcategory_container, "ver más")

                # PASO 8: Procesamiento de Todas las Subcategorías
                logging.info("PASO 8: Procesamiento de Todas las Subcategorías...")
                success = process_all_subcategories(driver, category_name, category_url)
                if not success:
                    logging.error(f"No se pudieron procesar las subcategorías para '{category_name}'")
                    continue

                logging.info(f"Categoría {category_index}/{total_categories} completada: {category_name}")

            except Exception as e:
                logging.error(f"Error procesando categoría '{category_name}': {e}")
                # Continuar con la siguiente categoría en caso de error
                continue

        logging.info("=== PROCESO LIMITADO COMPLETADO EXITOSAMENTE ===")
        logging.info("Procesadas: 1 categoría (Bebidas) con primeras 3 subcategorías")
        logging.info("El navegador permanecerá abierto para que puedas ver el resultado")

        # Keep browser open for 10 seconds so user can see the result (reduced for testing)
        time.sleep(10)

    except Exception as e:
        logging.error(f"Error en main: {e}")
        raise

    finally:
        if driver:
            driver.quit()
            logging.info("WebDriver closed")

if __name__ == "__main__":
    main()