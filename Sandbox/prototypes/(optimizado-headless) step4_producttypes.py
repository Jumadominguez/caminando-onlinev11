#!/usr/bin/env python3
"""
Script para procesar TODAS las categorías de Carrefour y extraer tipos de producto
VERSIÓN OPTIMIZADA: Procesamiento paralelo con múltiples navegadores basado en step6_products.py
Adaptado para extraer tipos de producto por subcategoría usando lógica robusta de reintentos
"""
import time
import logging
import json
import os
import random
import re
import threading
import unicodedata
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from pymongo import MongoClient
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('extraction_debug.log', mode='w', encoding='utf-8')
    ]
)

# Configuration constants
MAX_RETRIES = 3
BASE_RETRY_DELAY = 2.0
MAX_WORKERS = 8
HEADLESS_MODE = True

# Global counters for tracking
successful_subcategories = []
failed_subcategories = []

def retry_with_backoff(func, max_retries=MAX_RETRIES, base_delay=BASE_RETRY_DELAY, *args, **kwargs):
    """Execute a function with exponential backoff retry logic"""
    for attempt in range(max_retries + 1):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if attempt == max_retries:
                logging.error(f"Function {func.__name__} failed after {max_retries + 1} attempts: {e}")
                raise e

            delay = base_delay * (2 ** attempt) + random.uniform(0, 2)
            logging.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}. Retrying in {delay:.2f} seconds...")
            time.sleep(delay)

    return None

def simulate_human_behavior(driver):
    """Simulate human-like behavior to avoid detection"""
    try:
        # Random scroll to simulate reading
        scroll_amount = random.randint(200, 800)
        driver.execute_script(f"window.scrollTo(0, {scroll_amount});")

        # Random pause
        time.sleep(random.uniform(0.5, 2.0))

        # Simulate mouse movement
        actions = ActionChains(driver)
        actions.move_by_offset(random.randint(-100, 100), random.randint(-50, 50))
        actions.perform()

        # Another random pause
        time.sleep(random.uniform(0.3, 1.5))

    except Exception as e:
        logging.debug(f"Could not simulate human behavior: {e}")

def get_random_user_agent():
    """Get a random user agent"""
    return random.choice(USER_AGENTS)

def handle_modals_and_overlays(driver):
    """Handle modals, cookies banners, and overlays that block interactions - ENHANCED FOR HEADLESS"""
    try:
        # Scroll to ensure overlays are loaded
        driver.execute_script("window.scrollTo(0, 200);")
        time.sleep(0.5)

        # Common modal selectors
        modal_selectors = [
            "div.dy-modal-wrapper",
            ".cookie-banner",
            ".gdpr-banner",
            "[data-testid*='modal']",
            ".modal",
            ".popup",
            ".overlay",
            "div[role='dialog']",
            ".vtex-modal",
            "button[data-testid*='accept']",
            "button:contains('Aceptar')",
            "button:contains('Accept')",
            "button:contains('Cerrar')"
        ]

        for selector in modal_selectors:
            try:
                # Try CSS selector first
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    try:
                        # Try to click or hide the modal
                        if element.is_displayed():
                            driver.execute_script("arguments[0].style.display = 'none';", element)
                            logging.info(f"Hidden modal/overlay: {selector}")
                            time.sleep(0.5)
                    except Exception as e:
                        logging.debug(f"Could not hide modal {selector}: {e}")
            except:
                # Try XPath if CSS fails
                try:
                    elements = driver.find_elements(By.XPATH, f"//{selector}")
                    for element in elements:
                        try:
                            if element.is_displayed():
                                driver.execute_script("arguments[0].style.display = 'none';", element)
                                logging.info(f"Hidden modal/overlay with XPath: {selector}")
                                time.sleep(0.5)
                        except Exception as e:
                            logging.debug(f"Could not hide modal with XPath {selector}: {e}")
                except:
                    continue

        return False

    except Exception as e:
        logging.warning(f"Error handling modals: {e}")
        return False

# Anti-detection constants
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'
]

# Optimized delays for headless mode - slightly longer for better reliability
MIN_DELAY = 1.0
MAX_DELAY = 2.0

def random_delay():
    """Shorter random delay for faster processing"""
    time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))

# Retry configuration
MAX_RETRIES = 3
BASE_RETRY_DELAY = 5

# Global tracking lists for final report
successful_subcategories = []
failed_subcategories = []
tracking_lock = threading.Lock()

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

def setup_driver(user_agent=None):
    """Setup Firefox WebDriver with anti-detection measures - NOW HEADLESS"""
    firefox_options = Options()
    # HEADLESS MODE - No GUI
    firefox_options.add_argument("--headless")  # ENABLED FOR HEADLESS BROWSER
    firefox_options.add_argument("--no-sandbox")
    firefox_options.add_argument("--disable-dev-shm-usage")
    firefox_options.add_argument("--window-size=1366,768")  # Reduced for better headless compatibility

    # Additional headless optimizations
    firefox_options.add_argument("--disable-gpu")
    firefox_options.add_argument("--disable-extensions")
    firefox_options.add_argument("--disable-background-timer-throttling")
    firefox_options.add_argument("--disable-backgrounding-occluded-windows")
    firefox_options.add_argument("--disable-renderer-backgrounding")
    firefox_options.add_argument("--disable-features=VizDisplayCompositor")  # Additional headless stability

    # Anti-detection measures
    if user_agent:
        firefox_options.set_preference("general.useragent.override", user_agent)

    # Disable WebRTC to prevent IP leaks
    firefox_options.set_preference("media.peerconnection.enabled", False)

    # Randomize other preferences to avoid fingerprinting
    firefox_options.set_preference("dom.webdriver.enabled", False)
    firefox_options.set_preference('useAutomationExtension', False)

    # Headless-specific settings
    firefox_options.set_preference("dom.webnotifications.enabled", False)
    firefox_options.set_preference("media.volume_scale", "0.0")

    geckodriver_path = r"d:\dev\caminando-onlinev10\geckodriver_temp\geckodriver.exe"
    service = Service(geckodriver_path)
    driver = webdriver.Firefox(service=service, options=firefox_options)

    # Execute script to remove webdriver property
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

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
    """Open the filters panel if not already open - ENHANCED FOR HEADLESS"""
    try:
        filters_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Filtrar')]"))
        )
        filters_button.click()
        time.sleep(1.0)  # Longer delay for headless
    except:
        pass

def scroll_to_load_filters(driver):
    """Scroll down to ensure filters are loaded - ENHANCED FOR HEADLESS"""
    # Multiple scrolls to ensure loading in headless mode
    for i in range(5):  # Increased from 3
        driver.execute_script("window.scrollTo(0, 500);")
        time.sleep(0.5)
        driver.execute_script("window.scrollTo(0, 800);")
        time.sleep(0.5)
        driver.execute_script("window.scrollTo(0, 300);")  # Back up slightly
        time.sleep(0.3)

def get_all_categories():
    """Get all categories from MongoDB categories collection"""
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['carrefour']
        collection = db['categories']
        categories = list(collection.find({}, {'_id': 0}))
        logging.info(f"Retrieved {len(categories)} categories from database")
        return categories
    except Exception as e:
        logging.error(f"Error retrieving categories: {e}")
        return []

def expand_menu_if_collapsed(driver, menu_container, menu_name="subcategorías"):
    """Generic function to expand menu if collapsed"""
    try:
        # Check if menu is collapsed (has expand button)
        expand_buttons = menu_container.find_elements(By.XPATH, ".//button[contains(@aria-label, 'expand') or contains(@aria-label, 'desplegar') or contains(text(), '+') or contains(text(), 'Ver más')]")
        if expand_buttons:
            for btn in expand_buttons:
                try:
                    # Aggressive scroll to ensure button is visible
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'instant'});", btn)
                    driver.execute_script("window.scrollBy(0, -100);")  # Extra scroll up to avoid header
                    time.sleep(1)

                    # Try JavaScript click first
                    driver.execute_script("arguments[0].click();", btn)
                    logging.info(f"Expanded {menu_name} menu with JS click")
                    time.sleep(2)
                    break
                except Exception as e:
                    logging.warning(f"Could not click expand button: {e}")
                    continue
        else:
            logging.info(f"{menu_name} menu already expanded")
    except Exception as e:
        logging.warning(f"Error expanding {menu_name} menu: {e}")

def scroll_and_click_ver_mas(driver, container, button_text="ver más"):
    """Generic function to scroll and click 'ver más' buttons"""
    try:
        ver_mas_buttons = container.find_elements(By.XPATH, f".//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{button_text}')]")
        if ver_mas_buttons:
            for btn in ver_mas_buttons:
                try:
                    # Aggressive scroll to ensure button is visible
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'instant'});", btn)
                    driver.execute_script("window.scrollBy(0, -100);")  # Extra scroll up to avoid header
                    time.sleep(1)

                    # Try JavaScript click first
                    driver.execute_script("arguments[0].click();", btn)
                    logging.info(f"Clicked '{button_text}' button with JS click")
                    time.sleep(2)
                    break
                except Exception as e:
                    logging.warning(f"Could not click '{button_text}' button: {e}")
                    continue
        else:
            logging.info(f"No '{button_text}' button found")
    except Exception as e:
        logging.warning(f"Error clicking '{button_text}' button: {e}")

def process_subcategory_chunk(category_name, category_url, subcategory_chunk, chunk_idx, total_chunks):
    """Process a chunk of subcategories with its own browser instance - ROBUST VERSION"""
    thread_logger = logging.getLogger(f"Chunk-{chunk_idx}")
    thread_logger.setLevel(logging.INFO)

    # Initialize tracking for this chunk
    local_successful_subcategories = []
    local_failed_subcategories = []
    total_product_types_saved = 0

    # Create driver for this chunk
    user_agent = get_random_user_agent()
    driver = None

    try:
        thread_logger.info(f"🚀 Starting chunk {chunk_idx + 1}/{total_chunks} with {len(subcategory_chunk)} subcategories, User-Agent: {user_agent[:50]}...")

        # Initialize driver with random user agent
        driver = setup_driver(user_agent)

        # Add random delay before starting
        random_delay()

        # Navigate to category
        thread_logger.info(f"🚀 Loading category '{category_name}' for chunk {chunk_idx + 1}...")
        def navigate_with_retry():
            driver.get(category_url)
            time.sleep(0.5)
            handle_cookies(driver)

        retry_with_backoff(navigate_with_retry)
        time.sleep(1)

        # Process each subcategory in this chunk with robust retry mechanism
        for idx, subcategory in enumerate(subcategory_chunk, 1):
            max_retries_per_subcategory = 3
            subcategory_processed_successfully = False

            for attempt in range(max_retries_per_subcategory):
                try:
                    subcategory_name = subcategory['name']
                    checkbox_id = subcategory['checkbox_id']
                    subcategory_index = subcategory['index']

                    thread_logger.info(f"=== Chunk {chunk_idx + 1}: Processing subcategory {idx}/{len(subcategory_chunk)}: '{subcategory_name}' (ID: {checkbox_id}, Attempt {attempt + 1}/{max_retries_per_subcategory}) ===")

                    # If this is a retry attempt, restart the browser and reload category
                    if attempt > 0:
                        thread_logger.info(f"🔄 Restarting browser for retry attempt {attempt + 1}...")
                        if driver:
                            try:
                                driver.quit()
                            except:
                                pass

                        # Reinitialize driver and reload category
                        driver = setup_driver(get_random_user_agent())
                        random_delay()
                        retry_with_backoff(navigate_with_retry)
                        time.sleep(1)

                        # Create new driver with fresh session
                        driver = setup_driver(get_random_user_agent())
                        navigate_with_retry()
                        time.sleep(1)

                    # Click on the subcategory checkbox
                    thread_logger.info(f"📍 Clicking on subcategory checkbox '{checkbox_id}' for '{subcategory_name}'...")

                    def click_subcategory_checkbox():
                        # Open filters panel first
                        open_filters_panel(driver)
                        time.sleep(0.5)

                        # Find and click the specific checkbox
                        checkbox = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.ID, checkbox_id))
                        )

                        # Scroll to checkbox and click
                        driver.execute_script("arguments[0].scrollIntoView();", checkbox)
                        time.sleep(0.5)
                        driver.execute_script("arguments[0].click();", checkbox)

                        thread_logger.info(f"✅ Clicked checkbox {checkbox_id} for subcategory '{subcategory_name}'")
                        return True

                    retry_with_backoff(click_subcategory_checkbox)
                    time.sleep(2)  # Wait for page to update

                    # Handle modals and overlays - CRITICAL FOR HEADLESS
                    handle_modals_and_overlays(driver)
                    time.sleep(1)

                    # Setup filters with retry
                    def setup_filters_with_retry():
                        # Scroll to load filters if needed
                        scroll_to_load_filters(driver)
                        time.sleep(0.5)

                        # Find product types container
                        product_types_container = WebDriverWait(driver, 15).until(
                            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'product-type-filter')]"))
                        )
                        return product_types_container

                    product_types_container = retry_with_backoff(setup_filters_with_retry)
                    if not product_types_container:
                        raise Exception(f"Could not find product types container for subcategory '{subcategory_name}'")

                    # Expand product types menu if collapsed
                    expand_menu_if_collapsed(driver, product_types_container, "product types")
                    time.sleep(0.5)

                    # Click "ver más" to expand all product types
                    scroll_and_click_ver_mas(driver, product_types_container, "ver más")
                    time.sleep(1)

                    # Extract all product types
                    product_type_elements = product_types_container.find_elements(By.XPATH, ".//input[@type='checkbox']/following-sibling::label")
                    product_types = []

                    for elem in product_type_elements:
                        try:
                            product_type_name = elem.text.strip()
                            if product_type_name:
                                product_type_slug = generate_slug(product_type_name)
                                product_types.append({
                                    'name': product_type_name,
                                    'slug': product_type_slug,
                                    'subcategory': subcategory_name,
                                    'category': category_name,
                                    'url': category_url,  # Use category URL as base
                                    'checkbox_id': checkbox_id
                                })
                        except Exception as e:
                            thread_logger.warning(f"Error extracting product type: {e}")
                            continue

                    # Save to database
                    if product_types:
                        try:
                            client = MongoClient('mongodb://localhost:27017/')
                            db = client['carrefour']
                            collection = db['product_types']

                            # Insert product types
                            result = collection.insert_many(product_types)
                            thread_logger.info(f"✅ Saved {len(product_types)} product types for subcategory '{subcategory_name}'")
                            total_product_types_saved += len(product_types)
                            local_successful_subcategories.append(subcategory_name)
                            subcategory_processed_successfully = True

                        except Exception as e:
                            thread_logger.error(f"❌ Error saving product types to database: {e}")
                            raise e
                    else:
                        thread_logger.warning(f"⚠️ No product types found for subcategory '{subcategory_name}'")
                        local_failed_subcategories.append(subcategory_name)

                    # If we get here, processing was successful
                    if subcategory_processed_successfully:
                        break

                except Exception as e:
                    thread_logger.error(f"❌ Attempt {attempt + 1} failed for subcategory '{subcategory_name}': {e}")
                    if attempt == max_retries_per_subcategory - 1:
                        local_failed_subcategories.append(subcategory_name)
                    continue

        thread_logger.info(f"🎯 Chunk {chunk_idx + 1} completed - {len(local_successful_subcategories)} successful, {len(local_failed_subcategories)} failed")

    except Exception as e:
        thread_logger.error(f"💥 Critical error in chunk {chunk_idx + 1}: {e}")

    finally:
        # Close driver
        if driver:
            try:
                driver.quit()
            except:
                pass

    return local_successful_subcategories, local_failed_subcategories, total_product_types_saved

def process_all_subcategories(category_name, category_url):
    """Process all subcategories for a category using parallel chunk processing - ROBUST VERSION"""
    try:
        # Create initial driver to get all subcategories
        user_agent = get_random_user_agent()
        driver = setup_driver(user_agent)

        try:
            # Navigate to category
            logging.info(f"🔍 Getting subcategories for category '{category_name}'...")
            logging.info(f"🌐 Navigating to URL: {category_url}")

            def navigate_with_retry():
                driver.get(category_url)
                time.sleep(0.5)
                handle_cookies(driver)
                logging.info(f"✅ Successfully navigated to {category_url}")

            retry_with_backoff(navigate_with_retry)
            time.sleep(1)

            # Handle modals and overlays
            handle_modals_and_overlays(driver)
            time.sleep(1)

            # Setup filters
            def setup_filters_with_retry():
                logging.info("🔧 Setting up filters panel...")
                open_filters_panel(driver)
                time.sleep(0.5)
                scroll_to_load_filters(driver)
                time.sleep(0.5)

                # Find subcategories container using multiple selectors
                subcategory_selectors = [
                    "div.valtech-carrefourar-search-result-3-x-filter__container--category-3",
                    "div[data-testid*='category']",
                    "div.filter__container--category"
                ]

                subcategories_container = None
                for selector in subcategory_selectors:
                    try:
                        subcategories_container = driver.find_element(By.CSS_SELECTOR, selector)
                        logging.info(f"✅ Found subcategories container with selector: {selector}")
                        break
                    except Exception as e:
                        logging.debug(f"❌ Selector '{selector}' failed: {e}")
                        continue

                if not subcategories_container:
                    logging.error(f"❌ No subcategories container found for category '{category_name}' with any selector")
                    # Debug: save page source for analysis
                    with open(f"debug_page_{category_name.replace(' ', '_')}.html", "w", encoding="utf-8") as f:
                        f.write(driver.page_source)
                    logging.info(f"📄 Saved debug page source to debug_page_{category_name.replace(' ', '_')}.html")
                    raise Exception(f"No subcategories container found for category '{category_name}'")

                return subcategories_container

            subcategories_container = retry_with_backoff(setup_filters_with_retry)
            if not subcategories_container:
                logging.error(f"Failed to setup filters for category '{category_name}'")
                return False

            # Expand subcategories menu if collapsed
            expand_menu_if_collapsed(driver, subcategories_container, "subcategorías")
            time.sleep(0.5)

            # Click "ver más" to expand all subcategories
            scroll_and_click_ver_mas(driver, subcategories_container, "ver más")
            time.sleep(1)

            # Extract all subcategories using the same approach as functional script
            logging.info("🔍 Extracting subcategories...")
            subcategory_checkboxes = subcategories_container.find_elements(By.CSS_SELECTOR, "input[type='checkbox'][id^='category-3-']")
            total_subcategories = len(subcategory_checkboxes)
            logging.info(f"✅ Found {total_subcategories} subcategory checkboxes")

            if total_subcategories == 0:
                logging.warning(f"No subcategories found for category '{category_name}'")
                return False

            subcategories = []
            for i, checkbox in enumerate(subcategory_checkboxes):
                try:
                    # Get checkbox ID to construct subcategory info
                    checkbox_id = checkbox.get_attribute('id')
                    if checkbox_id:
                        # Extract subcategory name from checkbox value or aria-label
                        subcategory_name = checkbox.get_attribute('value') or checkbox.get_attribute('aria-label') or f"Subcategory_{i+1}"

                        # Try to find associated label
                        try:
                            label = subcategories_container.find_element(By.CSS_SELECTOR, f"label[for='{checkbox_id}']")
                            if label and label.text.strip():
                                subcategory_name = label.text.strip()
                        except:
                            pass

                        if subcategory_name and len(subcategory_name) > 1 and len(subcategory_name) < 100:
                            subcategories.append({
                                'name': subcategory_name,
                                'checkbox_id': checkbox_id,
                                'index': i
                            })
                            logging.info(f"📝 Found subcategory: {subcategory_name}")

                except Exception as e:
                    logging.debug(f"Error processing subcategory checkbox {i}: {e}")
                    continue

            logging.info(f"✅ Extracted {len(subcategories)} valid subcategories")

            if not subcategories:
                logging.warning(f"No subcategories found for category '{category_name}'")
                return False

            logging.info(f"✅ Found {len(subcategories)} subcategories for category '{category_name}'")

            # LIMITAR A SOLO LAS PRIMERAS 8 SUBCATEGORÍAS
            max_subcategories = min(8, len(subcategories))
            subcategories = subcategories[:max_subcategories]
            logging.info(f"✓ Procesando solo las primeras {max_subcategories} subcategorías (limitado por configuración)")

            # Close the initial driver as we don't need it anymore
            driver.quit()
            driver = None

            # Divide subcategories into chunks for parallel processing
            num_chunks = 8  # Use 8 chunks like the original script
            chunk_size = len(subcategories) // num_chunks
            remainder = len(subcategories) % num_chunks

            chunks = []
            start_idx = 0
            for i in range(num_chunks):
                current_chunk_size = chunk_size + (1 if i < remainder else 0)
                end_idx = start_idx + current_chunk_size
                chunk = subcategories[start_idx:end_idx]
                chunks.append(chunk)
                start_idx = end_idx

            logging.info(f"🎯 Divided {len(subcategories)} subcategories into {num_chunks} chunks:")
            for i, chunk in enumerate(chunks):
                logging.info(f"  Chunk {i+1}: {len(chunk)} subcategories")

            # Process chunks simultaneously using threading
            threads = []
            chunk_results = []

            for chunk_idx, subcategory_chunk in enumerate(chunks):
                def process_chunk(chunk_idx=chunk_idx, subcategory_chunk=subcategory_chunk):
                    result = process_subcategory_chunk(category_name, category_url, subcategory_chunk, chunk_idx, num_chunks)
                    chunk_results.append((chunk_idx, result))

                thread = threading.Thread(target=process_chunk)
                threads.append(thread)
                thread.start()

            # Wait for all chunks to complete
            for thread in threads:
                thread.join()

            # Aggregate results from all chunks
            total_product_types_saved = 0
            all_successful = []
            all_failed = []

            for chunk_idx, (successful, failed, product_types_saved) in chunk_results:
                all_successful.extend(successful)
                all_failed.extend(failed)
                total_product_types_saved += product_types_saved

            logging.info(f"🎉 Category '{category_name}' completed - {total_product_types_saved} total product types saved")
            logging.info(f"✅ Successful subcategories: {len(all_successful)}")
            if all_failed:
                logging.warning(f"❌ Failed subcategories: {len(all_failed)} - {all_failed}")

            # Update global tracking lists
            with tracking_lock:
                successful_subcategories.extend(all_successful)
                failed_subcategories.extend(all_failed)

            return True

        finally:
            # Close driver if still open
            if driver:
                try:
                    driver.quit()
                except:
                    pass

    except Exception as e:
        logging.error(f"💥 Error processing subcategories for category '{category_name}': {e}")
        return False

def main():
    """Main function - process specific categories sequentially with verification"""
    try:
        # Get all categories from database
        categories = get_all_categories()
        if not categories:
            logging.error("No categories found in database")
            return

        total_categories = len(categories)
        logging.info("=== 🚀 INICIANDO EXTRACCIÓN DE TIPOS DE PRODUCTO (PARALELO ROBUSTO) ===")
        logging.info(f"Procesando SOLO la primera categoría (limitado para debugging) usando chunks con reintentos")
        logging.info("Cada chunk procesará subcategorías con su propio navegador headless")

        # Process ONLY the first category for debugging
        categories_to_process = categories[:1]  # Only first category
        total_categories = len(categories_to_process)

        # Process each category
        for category_index, category in enumerate(categories_to_process, 1):
            try:
                category_name = category['name']
                category_url = category['url']
                logging.info(f"🎯 Procesando categoría {category_index}/{total_categories}: {category_name}")

                # Process all subcategories for this category
                success = process_all_subcategories(category_name, category_url)
                if not success:
                    logging.error(f"❌ Falló el procesamiento de la categoría '{category_name}'")
                    continue

                logging.info(f"✅ Categoría {category_index}/{total_categories} completada: {category_name}")

            except Exception as e:
                logging.error(f"💥 Error procesando categoría '{category_name}': {e}")
                continue

        # Generate final report
        logging.info("=== 📊 REPORTE FINAL ===")
        logging.info(f"✅ Subcategorías procesadas exitosamente: {len(successful_subcategories)}")
        if failed_subcategories:
            logging.warning(f"❌ Subcategorías que fallaron: {len(failed_subcategories)} - {failed_subcategories}")

        logging.info("🎉 PROCESO COMPLETADO EXITOSAMENTE")

    except Exception as e:
        logging.error(f"💥 Error en main: {e}")
        raise

if __name__ == "__main__":
    main()
