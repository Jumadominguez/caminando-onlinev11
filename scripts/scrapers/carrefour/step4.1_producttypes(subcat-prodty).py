#!/usr/bin/env python3
"""
Script completo para extraer TODOS los productos de TODOS los tipos de producto
Incluye paginación completa - procesa múltiples páginas por tipo de producto
"""
import time
import logging
import json
import os
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pymongo import MongoClient
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Checkpoint file path
CHECKPOINT_FILE = "carrefour_scraper_checkpoint.json"

def save_checkpoint(last_processed_category_idx, categories_since_restart):
    """Save progress checkpoint to file"""
    checkpoint_data = {
        "last_processed_category_idx": last_processed_category_idx,
        "categories_since_restart": categories_since_restart,
        "timestamp": datetime.now().isoformat(),
        "total_categories": None  # Will be set when saving
    }

    try:
        with open(CHECKPOINT_FILE, 'w', encoding='utf-8') as f:
            json.dump(checkpoint_data, f, indent=2, ensure_ascii=False)
        logging.info(f"💾 Checkpoint saved: category {last_processed_category_idx}")
    except Exception as e:
        logging.error(f"Error saving checkpoint: {e}")

def load_checkpoint():
    """Load progress checkpoint from file"""
    if not os.path.exists(CHECKPOINT_FILE):
        logging.info("📄 No checkpoint file found, starting from beginning")
        return None

    try:
        with open(CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
            checkpoint_data = json.load(f)

        last_idx = checkpoint_data.get("last_processed_category_idx", 0)
        categories_since_restart = checkpoint_data.get("categories_since_restart", 0)
        timestamp = checkpoint_data.get("timestamp", "unknown")

        logging.info(f"📂 Checkpoint loaded: resuming from category {last_idx + 1} (saved at {timestamp})")
        return last_idx, categories_since_restart

    except Exception as e:
        logging.error(f"Error loading checkpoint: {e}")
        return None

def clear_checkpoint():
    """Clear checkpoint file"""
    if os.path.exists(CHECKPOINT_FILE):
        try:
            os.remove(CHECKPOINT_FILE)
            logging.info("🗑️ Checkpoint file cleared")
        except Exception as e:
            logging.error(f"Error clearing checkpoint: {e}")

def clear_producttypes_arrays():
    """Clear all products arrays in the producttypes collection"""
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['carrefour']
        collection = db['producttypes']

        # Clear products arrays for all documents
        result = collection.update_many(
            {},  # All documents
            {"$set": {"products": []}}  # Set products array to empty
        )

        client.close()

        logging.info(f"✓ Cleared products arrays for {result.modified_count} documents in producttypes collection")
        return result.modified_count

    except Exception as e:
        logging.error(f"Error clearing producttypes arrays: {e}")
        return 0

def setup_driver():
    """Setup Firefox WebDriver (NO HEADLESS para que el usuario pueda ver)"""
    firefox_options = Options()
    # NO headless - el usuario quiere ver el proceso
    firefox_options.add_argument("--no-sandbox")
    firefox_options.add_argument("--disable-dev-shm-usage")
    firefox_options.add_argument("--window-size=1920,1080")

    geckodriver_path = r"d:\dev\caminando-onlinev8\geckodriver_temp\geckodriver.exe"
    service = Service(geckodriver_path)
    driver = webdriver.Firefox(service=service, options=firefox_options)
    logging.info("WebDriver initialized successfully (NO HEADLESS)")
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
        time.sleep(2)
    except:
        logging.info("Filters panel already open or no button found")

def scroll_to_load_filters(driver):
    """Scroll down to ensure filters are loaded"""
    driver.execute_script("window.scrollTo(0, 500);")
    time.sleep(3)
    logging.info("Scrolled down to load filters")

def get_all_categories():
    """Get all categories from MongoDB categories collection"""
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['carrefour']
        collection = db['categories']

        # Get all categories
        categories = list(collection.find({}, {'name': 1, 'url': 1, '_id': 0}))

        client.close()

        if categories:
            logging.info(f"✓ Retrieved {len(categories)} categories from database")
            for cat in categories[:3]:  # Show first 3
                logging.info(f"  - {cat.get('name')}: {cat.get('url')}")
            return categories
        else:
            logging.error("No categories found in database")
            return []

    except Exception as e:
        logging.error(f"Error retrieving categories from database: {e}")
        return []

def expand_product_type_menu(driver):
    """Buscar el menú 'Tipo de Producto' en el contenedor de filtros y expandirlo"""
    try:
        # Find the product types container with multiple selectors for robustness
        product_types_container = None
        selectors = [
            "div.valtech-carrefourar-search-result-3-x-filter__container--tipo-de-producto",
            "div[data-testid*='tipo-de-producto']",
            "div.filter__container--tipo-de-producto",
            "div.valtech-carrefourar-search-result-3-x-filter__container"
        ]

        for selector in selectors:
            try:
                product_types_container = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                # Verify it contains product type elements
                checkboxes = product_types_container.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
                if checkboxes:
                    logging.info(f"Found product types container with selector: {selector} ({len(checkboxes)} checkboxes)")
                    break
            except:
                continue

        if not product_types_container:
            logging.error("No product types container found with any selector")
            return None

        # Check if there's an expand button
        try:
            expand_button = product_types_container.find_element(By.CSS_SELECTOR, "div[role='button']")
            if expand_button and expand_button.is_displayed():
                driver.execute_script("arguments[0].scrollIntoView();", expand_button)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", expand_button)
                logging.info("✓ Expanded product types menu")
                time.sleep(2)
            else:
                logging.info("Product types menu already expanded")
        except Exception as e:
            logging.info(f"No expand button found for product types (already expanded): {e}")

        return product_types_container

    except Exception as e:
        logging.error(f"Error expanding product types menu: {e}")
        return None

def scroll_and_click_ver_mas_product_types(driver, product_types_container):
    """Hacer scroll hasta el final de 'Tipo de Producto' y hacer clic en botón 'Ver Mas' una vez, luego verificar que toda la lista sea visible"""
    try:
        # Scroll to the bottom of the container
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", product_types_container)
        time.sleep(2)
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

        button_clicked = False
        for selector in ver_mas_selectors:
            try:
                if selector.startswith("//"):
                    buttons = driver.find_elements(By.XPATH, selector)
                else:
                    buttons = driver.find_elements(By.CSS_SELECTOR, selector)

                for btn in buttons:
                    text = btn.text.lower()
                    if "ver más" in text or "ver mas" in text:
                        # Check if button is visible and enabled
                        if btn.is_displayed() and btn.is_enabled():
                            driver.execute_script("arguments[0].scrollIntoView();", btn)
                            time.sleep(1)
                            driver.execute_script("arguments[0].click();", btn)
                            logging.info(f"✓ Clicked 'Ver más' button for product types: '{btn.text}'")
                            button_clicked = True
                            time.sleep(2)  # Wait for all items to load
                            break

                if button_clicked:
                    break

            except Exception as e:
                logging.debug(f"Selector {selector} failed: {e}")
                continue

        if not button_clicked:
            logging.info("No 'Ver más' button found for product types (all items may already be visible)")

        # Scroll again to ensure all items are visible
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", product_types_container)
        time.sleep(2)
        logging.info("✓ Product types list should now be fully visible")

        return True

    except Exception as e:
        logging.error(f"Error scrolling and clicking 'Ver más' for product types: {e}")
        return False

def get_all_product_types(driver):
    """Get all available product types from the filter"""
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

        product_types = []
        for checkbox in checkboxes:
            try:
                input_id = checkbox.get_attribute("id")
                if input_id:
                    label = driver.find_element(By.CSS_SELECTOR, f"label[for='{input_id}']")
                    label_text = label.get_attribute("textContent").strip()
                    # Remove count in parentheses if present
                    clean_label = label_text.split('(')[0].strip()

                    if clean_label and clean_label not in product_types:
                        product_types.append(clean_label)
                        logging.debug(f"Found product type: '{clean_label}'")
            except Exception as e:
                logging.debug(f"Error checking checkbox: {e}")
                continue

        logging.info(f"✓ Found {len(product_types)} product types")
        return product_types

    except Exception as e:
        logging.error(f"Error getting all product types: {e}")
        return []

def apply_filter(driver):
    """Aplicar el filtro después de seleccionar el tipo de producto"""
    try:
        aplicar_selectors = [
            "div.vtex-button__label",
            "button[class*='Aplicar']",
            "button:contains('Aplicar')",
            "//button[contains(text(), 'Aplicar')]",
            "//div[contains(text(), 'Aplicar')]",
            "//span[contains(text(), 'Aplicar')]"
        ]

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
                        logging.info("✓ Filter applied")
                        time.sleep(3)  # Wait for filter to be applied
                        return True

            except Exception as e:
                logging.debug(f"Selector {selector} failed: {e}")
                continue

        logging.error("No 'Aplicar' button found")
        return False

    except Exception as e:
        logging.error(f"Error applying filter: {e}")
        return False

def extract_products(driver, product_type_name):
    """Extraer productos de la página filtrada"""
    try:
        # Wait for products to load
        time.sleep(3)

        # Try multiple selectors for product containers
        product_selectors = [
            "div.valtech-carrefourar-search-result-3-x-galleryItem",
            "div[data-testid*='product']",
            "div.vtex-product-summary",
            "div.product-item",
            ".product-container"
        ]

        products = []
        for selector in product_selectors:
            try:
                product_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if product_elements:
                    logging.info(f"Found {len(product_elements)} products with selector: {selector}")
                    break
            except Exception as e:
                logging.debug(f"Selector {selector} failed: {e}")
                continue

        if not product_elements:
            logging.warning("No product elements found")
            return []

        logging.info(f"Extracting data from {len(product_elements)} products")

        for i, product_elem in enumerate(product_elements):  # Extract ALL products, no limit
            try:
                # Extract product name - try multiple selectors
                name_selectors = [
                    "span.vtex-product-summary-2-x-productName",
                    "span.vtex-store-components-3-x-productName",
                    "h3.vtex-product-summary-2-x-productName",
                    "a.vtex-product-summary-2-x-productName",
                    "[data-testid*='product-name']",
                    ".vtex-product-summary-2-x-productName",
                    "span:contains('Aire')",  # Specific for air conditioners
                    "span:contains('Split')",  # Specific for air conditioners
                    "h3",  # Generic h3
                    "a[href*='/p']"  # Product links
                ]

                product_name = None
                for name_sel in name_selectors:
                    try:
                        if ":contains" in name_sel:
                            # Handle :contains pseudo-selector with XPath
                            text_to_find = name_sel.split("'")[1]
                            name_elem = product_elem.find_element(By.XPATH, f".//*[contains(text(), '{text_to_find}')]")
                        else:
                            name_elem = product_elem.find_element(By.CSS_SELECTOR, name_sel)

                        name_text = name_elem.text.strip()
                        if name_text and len(name_text) > 3:  # Avoid very short texts
                            product_name = name_text
                            break
                    except:
                        continue

                if not product_name:
                    # Try to get text from the entire product element
                    try:
                        product_name = product_elem.text.split('\n')[0].strip()
                        if len(product_name) < 3:
                            product_name = f"Product_{i+1}"
                    except:
                        product_name = f"Product_{i+1}"

                # Extract price - try multiple selectors
                price_selectors = [
                    "span.vtex-product-price-1-x-sellingPrice",
                    "span.vtex-product-price-1-x-currencyContainer",
                    "span.vtex-store-components-3-x-price",
                    ".vtex-product-price-1-x-sellingPrice",
                    ".vtex-product-price-1-x-currencyContainer",
                    "[data-testid*='price']",
                    ".product-price",
                    "span:contains('$')",  # Look for price with dollar sign
                    "span:contains('ARS')",  # Look for ARS currency
                    "div:contains('$')",  # Price in div
                    "span.valtex-carrefourar"  # Carrefour specific
                ]

                product_price = None
                for price_sel in price_selectors:
                    try:
                        if ":contains" in price_sel:
                            # Handle :contains pseudo-selector with XPath
                            text_to_find = price_sel.split("'")[1]
                            price_elem = product_elem.find_element(By.XPATH, f".//*[contains(text(), '{text_to_find}')]")
                        else:
                            price_elem = product_elem.find_element(By.CSS_SELECTOR, price_sel)

                        price_text = price_elem.text.strip()
                        if price_text and ('$' in price_text or 'ARS' in price_text or any(char.isdigit() for char in price_text)):
                            product_price = price_text
                            break
                    except:
                        continue

                if not product_price:
                    # Try to find any text that looks like a price in the product element
                    try:
                        product_text = product_elem.text
                        import re
                        # Look for price patterns like $123, $123.456, 123.456, etc.
                        price_match = re.search(r'\$?\d{1,3}(?:\.\d{3})*(?:,\d{2})?', product_text)
                        if price_match:
                            product_price = price_match.group()
                        else:
                            product_price = "Price not found"
                    except:
                        product_price = "Price not found"

                product_data = {
                    'name': product_name,
                    'price': product_price,
                    'product_type': product_type_name,
                    'extracted_at': datetime.now()
                }

                products.append(product_data)
                logging.info(f"✓ Extracted product {i+1}: {product_name} - {product_price}")

            except Exception as e:
                logging.debug(f"Error extracting product {i+1}: {e}")
                continue

        logging.info(f"✓ Successfully extracted {len(products)} products")
        return products

    except Exception as e:
        logging.error(f"Error extracting products: {e}")
        return []

def get_total_pages(driver):
    """Detect pagination and return total number of pages"""
    try:
        # Look for pagination container
        pagination_selectors = [
            "div.valtech-carrefourar-search-result-3-x-paginationContainer",
            "div.flex.justify-center.items-center.ma6",
            ".paginationContainer",
            "[class*='pagination']"
        ]

        pagination_container = None
        for selector in pagination_selectors:
            try:
                pagination_container = driver.find_element(By.CSS_SELECTOR, selector)
                if pagination_container and pagination_container.is_displayed():
                    logging.info(f"Found pagination container with selector: {selector}")
                    break
            except:
                continue

        if not pagination_container:
            logging.info("No pagination container found - only one page")
            return 1

        # Find all page buttons
        page_buttons = pagination_container.find_elements(By.CSS_SELECTOR, "button[value]")

        if not page_buttons:
            logging.info("No page buttons found - only one page")
            return 1

        # Get the highest page number
        max_page = 1
        for btn in page_buttons:
            try:
                page_value = btn.get_attribute("value")
                if page_value and page_value.isdigit():
                    page_num = int(page_value)
                    max_page = max(max_page, page_num)
            except:
                continue

        logging.info(f"✓ Found {max_page} pages total")
        return max_page

    except Exception as e:
        logging.warning(f"Error detecting pagination: {e}")
        return 1

def navigate_to_page(driver, page_number):
    """Navigate to a specific page by clicking the page button or using Next button"""
    try:
        if page_number == 1:
            logging.info("Already on page 1")
            return True

        # First, try to find the specific page button
        try:
            # Find pagination container
            pagination_selectors = [
                "div.valtech-carrefourar-search-result-3-x-paginationContainer",
                "div.flex.justify-center.items-center.ma6",
                ".paginationContainer",
                "[class*='pagination']"
            ]

            pagination_container = None
            for selector in pagination_selectors:
                try:
                    pagination_container = driver.find_element(By.CSS_SELECTOR, selector)
                    if pagination_container and pagination_container.is_displayed():
                        break
                except:
                    continue

            if pagination_container:
                # Try to find the specific page button
                page_button = pagination_container.find_element(By.CSS_SELECTOR, f"button[value='{page_number}']")
                if page_button and page_button.is_displayed():
                    # Scroll to and click the page button
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", page_button)
                    time.sleep(1)

                    # Wait until the button is clickable
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(page_button))

                    driver.execute_script("arguments[0].click();", page_button)
                    logging.info(f"✓ Navigated to page {page_number} using page button")
                    time.sleep(3)
                    return True
        except:
            logging.debug(f"Could not find page {page_number} button, trying Next button approach")

        # Fallback: Use Next button to navigate page by page
        # This is more reliable when there are many pages
        current_page = 1  # Assume we're starting from page 1 or know current page

        while current_page < page_number:
            try:
                # Find Next button
                next_selectors = [
                    "button.valtech-carrefourar-search-result-3-x-paginationButtonChangePageNext",
                    "button:contains('Siguiente')",
                    "button:contains('Next')",
                    "//button[contains(text(), 'Siguiente')]",
                    "//button[contains(text(), 'Next')]"
                ]

                next_button = None
                for selector in next_selectors:
                    try:
                        if selector.startswith("//"):
                            next_button = driver.find_element(By.XPATH, selector)
                        else:
                            next_button = driver.find_element(By.CSS_SELECTOR, selector)
                        if next_button and next_button.is_displayed() and next_button.is_enabled():
                            break
                    except:
                        continue

                if not next_button:
                    logging.error(f"Next button not found or not clickable at page {current_page}")
                    return False

                # Click Next button
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", next_button)
                logging.info(f"✓ Clicked Next button to go from page {current_page} to {current_page + 1}")
                current_page += 1
                time.sleep(3)

            except Exception as e:
                logging.error(f"Error clicking Next button at page {current_page}: {e}")
                return False

        logging.info(f"✓ Successfully navigated to page {page_number}")
        return True

    except Exception as e:
        logging.error(f"Error navigating to page {page_number}: {e}")
        return False

def select_product_type(driver, target_product_type):
    """Seleccionar un tipo de producto específico usando las mismas funciones que funcionan al inicio del script"""
    try:
        # Use the same expansion logic as the initial setup
        logging.info("Expanding product type filter using proven method...")

        # PASO 1: Expandir menú de "Tipo de Producto" usando la función probada
        product_types_container = expand_product_type_menu(driver)
        if not product_types_container:
            logging.error("Failed to expand product types menu")
            return None

        # PASO 2: Hacer scroll y buscar botón "Ver más" usando la función probada
        scroll_and_click_ver_mas_product_types(driver, product_types_container)

        # Now try to find the target product type
        # Try multiple selectors for product type checkboxes
        checkbox_selectors = [
            "input[type='checkbox'][id^='tipo-de-producto-']",
            "input[type='checkbox']",
            ".valtech-carrefourar-search-result-3-x-filter__checkbox input[type='checkbox']",
            "input[id*='tipo-de-producto']"
        ]

        # Function to find checkboxes
        def find_checkboxes():
            for selector in checkbox_selectors:
                try:
                    elements = product_types_container.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        return elements
                except Exception as e:
                    logging.debug(f"Selector {selector} failed: {e}")
                    continue
            return []

        # Function to find target checkbox
        def find_target_checkbox(checkboxes):
            for checkbox in checkboxes:
                try:
                    input_id = checkbox.get_attribute("id")
                    if input_id:
                        label = driver.find_element(By.CSS_SELECTOR, f"label[for='{input_id}']")
                        label_text = label.get_attribute("textContent").strip()
                        # Remove count in parentheses if present
                        clean_label = label_text.split('(')[0].strip()

                        logging.debug(f"Found product type: '{clean_label}'")

                        if clean_label.lower() == target_product_type.lower():
                            return checkbox, clean_label
                except Exception as e:
                    logging.debug(f"Error checking checkbox: {e}")
                    continue
            return None, None

        # First attempt to find the checkbox
        checkboxes = find_checkboxes()
        if not checkboxes:
            logging.warning("No product type checkboxes found after expansion")
            return None

        target_checkbox, target_label = find_target_checkbox(checkboxes)

        if not target_checkbox:
            logging.error(f"Product type '{target_product_type}' not found even after full expansion")
            return None

        logging.info(f"Selecting product type: '{target_label}'")

        # Scroll to and select the checkbox
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", target_checkbox)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", target_checkbox)
        logging.info(f"✓ Selected product type: {target_label}")

        return target_label

    except Exception as e:
        logging.error(f"Error selecting product type '{target_product_type}': {e}")
        return None

def verify_single_product_type_selection(driver, expected_product_type):
    """Verify that only the expected product type is selected in the selected filters container"""
    try:
        # Find selected filters container specifically
        selected_container_selectors = [
            "div.valtech-carrefourar-search-result-3-x-filter__container--selectedFilters",
            "div.valtech-carrefourar-search-result-3-x-selectedFilters",
            "[class*='selectedFilters']",
            "[class*='selected-filters']"
        ]

        selected_container = None
        for selector in selected_container_selectors:
            try:
                selected_container = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                logging.debug(f"Found selected filters container with selector: {selector}")
                break
            except:
                continue

        if not selected_container:
            logging.warning(f"⚠️ No selected filters container found with any selector")
            # Try to check if we're on the right page by looking for product results
            try:
                product_count_elem = driver.find_element(By.CSS_SELECTOR, "div.valtech-carrefourar-search-result-3-x-totalProducts--layout")
                if product_count_elem:
                    logging.info("✓ Found product results, filter may have been applied successfully despite missing selected filters container")
                    return True
            except:
                logging.warning("⚠️ No product results found either")
            return False

        # Find all selected filter labels within this container
        selected_labels = selected_container.find_elements(By.CSS_SELECTOR, "label.vtex-checkbox__label")

        selected_product_types = []
        for label in selected_labels:
            try:
                text = label.get_attribute("textContent").strip()
                # Remove count in parentheses if present
                clean_text = text.split('(')[0].strip()
                if clean_text:
                    selected_product_types.append(clean_text.lower())
            except:
                continue

        logging.info(f"Currently selected product types: {selected_product_types}")

        # Check if only the expected product type is selected
        expected_lower = expected_product_type.lower()
        if expected_lower == "none":
            # Should have no product types selected
            if len(selected_product_types) == 0:
                logging.info("✓ Verified no product types selected")
                return True
            else:
                logging.warning(f"⚠️ Found {len(selected_product_types)} product types selected when none expected: {selected_product_types}")
                return False
        elif len(selected_product_types) == 1 and selected_product_types[0] == expected_lower:
            logging.info(f"✓ Verified single selection: only '{expected_product_type}' is selected")
            return True
        elif len(selected_product_types) == 0:
            logging.warning(f"⚠️ No product types selected, expected '{expected_product_type}'")
            return False
        else:
            logging.warning(f"⚠️ Multiple or wrong product types selected: {selected_product_types}, expected only '{expected_product_type}'")
            return False

    except Exception as e:
        logging.warning(f"Error verifying single selection: {e}")
        return False

def deselect_product_type(driver, product_type):
    """Deselect a product type by clicking on it in the selected filters container"""
    try:
        # Find selected filters container
        selected_container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.valtech-carrefourar-search-result-3-x-filter__container--selectedFilters"))
        )

        # Find all selected filter items
        selected_items = selected_container.find_elements(By.CSS_SELECTOR, "div.valtech-carrefourar-search-result-3-x-filterItem--selected")

        for item in selected_items:
            try:
                # Get the label text
                label = item.find_element(By.CSS_SELECTOR, "label.vtex-checkbox__label")
                label_text = label.get_attribute("textContent").strip()
                clean_text = label_text.split('(')[0].strip()

                if clean_text.lower() == product_type.lower():
                    # Found the item to deselect - click on it
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", item)
                    time.sleep(1)

                    # Click on the item or its checkbox
                    try:
                        # Try clicking the item directly
                        driver.execute_script("arguments[0].click();", item)
                    except:
                        # Try clicking the checkbox
                        try:
                            checkbox = item.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
                            driver.execute_script("arguments[0].click();", checkbox)
                        except:
                            # Try clicking the label
                            driver.execute_script("arguments[0].click();", label)

                    logging.info(f"✓ Deselected product type: {product_type}")
                    time.sleep(3)  # Wait for deselection to take effect

                    # Verify deselection
                    if verify_single_product_type_selection(driver, "none"):
                        logging.info("✓ Confirmed deselection - no product types selected")
                    else:
                        logging.warning("⚠️ Deselection may not have worked properly")

                    return True

            except Exception as e:
                logging.debug(f"Error checking selected item: {e}")
                continue

        logging.warning(f"Could not find selected filter item for '{product_type}'")
        return False

    except Exception as e:
        logging.error(f"Error deselecting product type '{product_type}': {e}")
        return False
    """Get total number of products from the total products element"""
    try:
        total_products_selectors = [
            "div.valtech-carrefourar-search-result-3-x-totalProducts--layout",
            ".totalProducts--layout",
            "[class*='totalProducts']"
        ]

        for selector in total_products_selectors:
            try:
                total_element = driver.find_element(By.CSS_SELECTOR, selector)
                if total_element and total_element.is_displayed():
                    text = total_element.text.strip()
                    # Extract number from text like "52 Productos" or "16 productos"
                    import re
                    match = re.search(r'(\d+)', text)
                    if match:
                        total = int(match.group(1))
                        logging.info(f"✓ Found total products: {total}")
                        return total
            except:
                continue

        logging.warning("Could not find total products element")
        return None

    except Exception as e:
        logging.error(f"Error getting total products: {e}")
        return None

def get_total_products(driver):
    """Get total number of products from the total products element"""
    try:
        total_products_selectors = [
            "div.valtech-carrefourar-search-result-3-x-totalProducts--layout",
            ".totalProducts--layout",
            "[class*='totalProducts']"
        ]

        for selector in total_products_selectors:
            try:
                total_element = driver.find_element(By.CSS_SELECTOR, selector)
                if total_element and total_element.is_displayed():
                    text = total_element.text.strip()
                    # Extract number from text like "52 Productos" or "16 productos"
                    import re
                    match = re.search(r'(\d+)', text)
                    if match:
                        total = int(match.group(1))
                        logging.info(f"✓ Found total products: {total}")
                        return total
            except:
                continue

        logging.warning("Could not find total products element")
        return None

    except Exception as e:
        logging.error(f"Error getting total products: {e}")
        return None

def extract_all_products_from_pages(driver, product_type_name):
    """Extract products from all pages for a product type"""
    try:
        all_products = []

        # Get total expected products
        total_expected = get_total_products(driver)
        if total_expected:
            logging.info(f"Expecting to extract {total_expected} products total for '{product_type_name}'")
            # Calculate expected pages (16 products per page)
            expected_pages = (total_expected + 15) // 16  # Ceiling division
            logging.info(f"Calculated expected pages: {expected_pages} (16 products per page)")
        else:
            expected_pages = 1

        current_page = 1
        products_extracted = 0

        while True:
            logging.info(f"Extracting products from page {current_page}")

            # Extract products from current page
            page_products = extract_products(driver, product_type_name)
            page_count = len(page_products)
            logging.info(f"✓ Extracted {page_count} products from page {current_page}")

            if page_count == 0:
                logging.warning(f"No products found on page {current_page}, stopping")
                break

            # Add page number to products for tracking
            for product in page_products:
                product['page'] = current_page

            all_products.extend(page_products)
            products_extracted += page_count

            # Check if we have all expected products
            if total_expected and products_extracted >= total_expected:
                logging.info(f"✓ Reached expected total of {total_expected} products")
                break

            # Check if we should continue to next page
            # If we got less than 16 products, we're on the last page
            if page_count < 16:
                logging.info(f"✓ Got {page_count} products (< 16), this is the last page")
                break

            # Try to navigate to next page
            current_page += 1
            if not navigate_to_page(driver, current_page):
                logging.warning(f"Could not navigate to page {current_page}, stopping")
                break

            # Safety check: don't go beyond a reasonable number of pages
            if current_page > 50:  # Arbitrary limit to prevent infinite loops
                logging.warning("Reached page limit (50), stopping to prevent infinite loop")
                break

        logging.info(f"✓ Total extracted: {len(all_products)} products from {current_page} pages")

        return all_products

    except Exception as e:
        logging.error(f"Error extracting products from all pages: {e}")
        return []

def save_products_to_db(products, product_type_name, category_name):
    """Save products to producttypes collection by updating the products array"""
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['carrefour']
        collection = db['producttypes']

        # Remove duplicates from products array before saving
        # Use product name as unique identifier to avoid duplicates
        seen_names = set()
        unique_products = []
        for product in products:
            product_name = product.get('name', '').strip()
            if product_name and product_name not in seen_names:
                seen_names.add(product_name)
                unique_products.append(product)
            elif product_name in seen_names:
                logging.debug(f"Removed duplicate product: {product_name}")

        if len(unique_products) != len(products):
            logging.info(f"Removed {len(products) - len(unique_products)} duplicate products")

        # First, let's check if the document exists
        existing_doc = collection.find_one({"name": product_type_name})
        if not existing_doc:
            logging.warning(f"Document with name '{product_type_name}' not found in producttypes collection")
            # Try to find similar names
            similar_docs = list(collection.find({"name": {"$regex": product_type_name[:10], "$options": "i"}}).limit(5))
            if similar_docs:
                logging.info(f"Similar documents found: {[doc['name'] for doc in similar_docs]}")
            else:
                logging.warning("No similar documents found")
            client.close()
            return 0

        logging.info(f"Found existing document: {existing_doc['name']} (current products: {len(existing_doc.get('products', []))})")

        # Update the products array for the specific product type
        result = collection.update_one(
            {"name": product_type_name},  # Find document by product type name
            {
                "$set": {
                    "products": unique_products,  # Replace the entire products array with unique products
                    "last_updated": datetime.now()
                }
            }
        )

        client.close()

        if result.modified_count > 0:
            logging.info(f"✓ Updated products array for '{product_type_name}' with {len(unique_products)} unique products")
            return len(unique_products)
        else:
            logging.warning(f"No document was modified for product type '{product_type_name}'")
            return 0

    except Exception as e:
        logging.error(f"Error saving products to database: {e}")
        return 0

def main():
    """Main function - process ALL product types with full pagination support"""
    driver = None

    try:
        logging.info("=== INICIANDO EXTRACCIÓN COMPLETA DE PRODUCTOS ===")
        logging.info("PASO 0: Limpiando arrays de productos en base de datos...")

        # Clear products arrays first
        cleared_count = clear_producttypes_arrays()
        logging.info(f"✓ Limpiados arrays de productos para {cleared_count} tipos de producto")

        logging.info("Objetivo: Extraer TODOS los productos de TODOS los tipos de producto")
        logging.info("Incluye paginación completa para tipos con más de 16 productos")

        # PASO 1: Inicialización del WebDriver
        logging.info("PASO 1: Inicialización del WebDriver Firefox...")
        driver = setup_driver()

        # PASO 2: Obtener todas las categorías
        logging.info("PASO 2: Obtener todas las categorías de la base de datos...")
        all_categories = get_all_categories()
        if not all_categories:
            logging.error("No se pudieron obtener las categorías")
            return

        total_categories = len(all_categories)
        logging.info(f"✓ Encontradas {total_categories} categorías para procesar")

        # PASO 2.1: Verificar checkpoint para reanudar desde donde se quedó
        checkpoint = load_checkpoint()
        start_idx = 0
        categories_since_restart = 0

        if checkpoint:
            last_processed_idx, categories_since_restart = checkpoint
            start_idx = last_processed_idx + 1  # Continuar desde la siguiente categoría

            if start_idx >= total_categories:
                logging.info("🎉 Todas las categorías ya fueron procesadas completamente!")
                clear_checkpoint()  # Limpiar checkpoint ya que terminó
                return

            logging.info(f"▶️ Reanudando procesamiento desde categoría {start_idx + 1}/{total_categories}")
        else:
            logging.info("▶️ Iniciando procesamiento desde el principio")

        # Configuración para reinicio periódico del navegador
        CATEGORIES_BEFORE_RESTART = 3  # Reiniciar navegador cada 3 categorías

        # PASO 3: Procesar cada categoría
        for cat_idx in range(start_idx, total_categories):
            category = all_categories[cat_idx]
            # PASO 3.x: Procesar categoría con manejo de errores
            try:
                category_name = category.get('name')
                category_url = category.get('url')

                # Verificar si necesitamos reiniciar el navegador
                if categories_since_restart >= CATEGORIES_BEFORE_RESTART:
                    logging.info(f"🔄 Reiniciando navegador después de {categories_since_restart} categorías procesadas...")
                    try:
                        driver.quit()
                        time.sleep(2)
                        driver = setup_driver()
                        categories_since_restart = 0
                        logging.info("✅ Navegador reiniciado exitosamente")
                    except Exception as e:
                        logging.error(f"❌ Error al reiniciar navegador: {e}")
                        logging.info("Intentando continuar con el navegador actual...")

                logging.info(f"PASO 3.{cat_idx}: Procesando categoría '{category_name}'...")

                # PASO 3.x.1: Navegar a la categoría
                logging.info(f"Navegando a la categoría '{category_name}'...")
                driver.get(category_url)
                time.sleep(5)

                # Handle cookies
                handle_cookies(driver)

                # Incrementar contador de categorías procesadas
                categories_since_restart += 1

                # PASO 4.x: Abrir panel de filtros
                logging.info("PASO 4: Abriendo panel de filtros...")
                open_filters_panel(driver)

                # PASO 5.x: Cargar filtros
                logging.info("PASO 5: Cargando filtros...")
                scroll_to_load_filters(driver)

                # PASO 6.x: Expandir menú de "Tipo de Producto"
                logging.info("PASO 6: Expandiendo menú de 'Tipo de Producto'...")
                product_types_container = expand_product_type_menu(driver)
                if not product_types_container:
                    logging.error("No se pudo expandir el menú de tipos de producto")
                    continue

                # PASO 7.x: Hacer scroll y buscar botón "Ver más"
                logging.info("PASO 7: Buscando botón 'Ver más' en tipos de producto...")
                scroll_and_click_ver_mas_product_types(driver, product_types_container)

                # PASO 8.x: Obtener todos los tipos de producto disponibles
                logging.info("PASO 8: Obteniendo todos los tipos de producto disponibles...")
                all_product_types = get_all_product_types(driver)
                if not all_product_types:
                    logging.error("No se pudieron obtener los tipos de producto")
                    continue

                logging.info(f"✓ Encontrados {len(all_product_types)} tipos de producto")

                # PASO 9.x: Procesar cada tipo de producto
                total_types = len(all_product_types)
                for idx, product_type in enumerate(all_product_types, 1):
                    logging.info(f"=== PROCESANDO TIPO DE PRODUCTO {idx}/{total_types}: '{product_type}' ===")

                    # Verificar que no haya tipos seleccionados antes de empezar
                    if not verify_single_product_type_selection(driver, "none"):
                        logging.info("Des-seleccionando tipos previamente seleccionados...")
                        # Try to clear all selected filters
                        try:
                            clear_button = driver.find_element(By.CSS_SELECTOR, "a.valtech-carrefourar-search-result-3-x-clearFilter")
                            if clear_button and clear_button.is_displayed():
                                driver.execute_script("arguments[0].click();", clear_button)
                                logging.info("✓ Cleared all selected filters")
                                time.sleep(3)
                            else:
                                logging.warning("No clear filters button found")
                        except:
                            logging.warning("Could not clear selected filters")

                    # Seleccionar el tipo de producto
                    logging.info(f"Seleccionando tipo de producto: '{product_type}'...")
                    selected_type = select_product_type(driver, product_type)
                    if not selected_type:
                        logging.warning(f"No se pudo seleccionar '{product_type}', saltando...")
                        continue

                    # Aplicar el filtro
                    logging.info("Aplicando el filtro...")
                    if not apply_filter(driver):
                        logging.warning(f"No se pudo aplicar el filtro para '{product_type}', saltando...")
                        continue

                    # Esperar a que se aplique el filtro y se recargue la página
                    logging.info("Esperando a que se aplique el filtro...")
                    time.sleep(5)

                    # Verificar selección única
                    logging.info(f"Verificando selección única para '{selected_type}'...")
                    if not verify_single_product_type_selection(driver, selected_type):
                        logging.error(f"❌ No se pudo verificar selección única para '{selected_type}', saltando este tipo de producto...")
                        continue

                    # Extraer productos de todas las páginas
                    logging.info(f"Extrayendo productos para '{selected_type}'...")
                    products = extract_all_products_from_pages(driver, selected_type)
                    if not products:
                        logging.warning(f"No se pudieron extraer productos para '{selected_type}'")
                    else:
                        logging.info(f"✓ Extraídos productos del tipo '{selected_type}'")

                        # Guardar productos en base de datos
                        logging.info(f"Guardando productos de '{selected_type}' en base de datos...")
                        saved_count = save_products_to_db(products, selected_type, category_name)
                        logging.info(f"✓ Guardados productos en la base de datos")

                    # No need to deselect here anymore - we'll clear at the beginning of next iteration

            except Exception as e:
                logging.error(f"❌ Error procesando categoría '{category_name}': {e}")
                logging.warning(f"Saltando categoría '{category_name}' y continuando con la siguiente...")

                # Intentar reiniciar el navegador si hay problemas de conexión
                if "connection" in str(e).lower() or "webdriver" in str(e).lower():
                    try:
                        logging.info("🔄 Intentando reiniciar navegador debido a error de conexión...")
                        driver.quit()
                        time.sleep(3)
                        driver = setup_driver()
                        categories_since_restart = 0
                        logging.info("✅ Navegador reiniciado después de error de conexión")
                    except Exception as restart_error:
                        logging.error(f"❌ Error al reiniciar navegador: {restart_error}")
                        logging.warning("Continuando con el procesamiento...")

                continue

            # ✅ Categoría procesada exitosamente - guardar checkpoint
            save_checkpoint(cat_idx, categories_since_restart)
            logging.info(f"✅ Categoría '{category_name}' completada y checkpoint guardado")

        logging.info("=== EXTRACCIÓN COMPLETA FINALIZADA ===")
        logging.info(f"Procesadas {len(all_categories)} categorías exitosamente")
        logging.info("El navegador permanecerá abierto para que puedas ver el resultado")

        # Limpiar checkpoint ya que terminó completamente
        clear_checkpoint()

        # Keep browser open for 30 seconds so user can see the result
        time.sleep(30)

    except Exception as e:
        logging.error(f"Error en main: {e}")
        raise

    finally:
        if driver:
            driver.quit()
            logging.info("WebDriver closed")

if __name__ == "__main__":
    main()