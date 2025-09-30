#!/usr/bin/env python3
"""
Disco Subcategories Scraper
Complete implementation based on dia_subcategories_scraping_process.md

Author: GitHub Copilot
Date: September 29, 2025
"""

import os
import json
import time
import logging
import re
import threading
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import pymongo
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv

# Load environment variables from .env file
try:
    # Load .env from src/backend/ directory (encrypted environment)
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', '..'))
    backend_env = os.path.join(project_root, 'src', 'backend', '.env')
    load_dotenv(dotenv_path=backend_env)
    print("Loaded environment variables from src/backend/.env file")
except ImportError:
    print("python-dotenv not installed. Using system environment variables only.")

# ANSI color codes for better terminal visualization
class Colors:
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'

# Custom formatter for colored logging
class ColoredFormatter(logging.Formatter):
    def format(self, record):
        if record.levelno == logging.ERROR:
            record.levelname = f"{Colors.RED}{record.levelname}{Colors.RESET}"
            record.msg = f"{Colors.RED}{record.msg}{Colors.RESET}"
        elif record.levelno == logging.WARNING:
            record.levelname = f"{Colors.YELLOW}{record.levelname}{Colors.RESET}"
            record.msg = f"{Colors.YELLOW}{record.msg}{Colors.RESET}"
        elif record.levelno == logging.INFO:
            record.levelname = f"{Colors.BLUE}{record.levelname}{Colors.RESET}"
            record.msg = f"{Colors.CYAN}{record.msg}{Colors.RESET}"
        elif record.levelno == logging.DEBUG:
            record.levelname = f"{Colors.MAGENTA}{record.levelname}{Colors.RESET}"
            record.msg = f"{Colors.MAGENTA}{record.msg}{Colors.RESET}"
        return super().format(record)

# Configure logging with colors
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)  # Reduced verbosity for cleaner output

# File handler (overwrite mode to avoid old logs) - keeps detailed logs
file_handler = logging.FileHandler('logs/3-disco-subcategories.log', mode='w')
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

# Console handler with colors - only essential messages
console_handler = logging.StreamHandler()
console_formatter = ColoredFormatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
console_handler.setLevel(logging.WARNING)  # Only warnings and errors on console

logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Utility functions for better visualization
def print_separator(char='=', length=60):
    """Print a visual separator line"""
    print(f"{Colors.BLUE}{char * length}{Colors.RESET}")

def print_header(text, emoji=''):
    """Print a formatted header"""
    print_separator()
    print(f"{Colors.BOLD}{Colors.GREEN}{emoji} {text.upper()} {emoji}{Colors.RESET}")
    print_separator()

def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_info(text):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.RESET}")

def print_action(text):
    """Print action message"""
    print(f"{Colors.CYAN}🔄 {text}{Colors.RESET}")

def generate_slug(text):
    """Generate slug from text (similar to Subcategory.js method)"""
    return re.sub(r'[^\w\-]+', '', text.lower().strip().replace(' ', '-')).replace('--+', '-').strip('-')

def connect_mongodb():
    """Connect to MongoDB Atlas"""
    try:
        # Get MongoDB credentials from environment variables
        mongo_uri = os.getenv('MONGO_DISCO_URI')

        if not mongo_uri:
            raise ValueError("MONGO_DIA_URI environment variable not set")

        client = pymongo.MongoClient(mongo_uri)
        db = client.disco

        # Test the connection
        client.admin.command('ping')
        print_success("Connected to MongoDB Atlas - disco database")
        return db

    except ConnectionFailure as e:
        print_error(f"Failed to connect to MongoDB: {e}")
        raise
    except Exception as e:
        print_error(f"Unexpected MongoDB error: {e}")
        raise

class DiscoSubcategoriesScraper:
    def __init__(self, headless=True, max_workers=5):
        """Initialize the scraper with MongoDB connection and browser setup"""
        self.headless = headless
        self.max_workers = max_workers  # Optimized for parallel processing
        self.driver = None
        self.db = None

        # MongoDB connection
        self._connect_mongodb()

        # Browser setup
        self._setup_browser()

    def _connect_mongodb(self):
        """Connect to MongoDB Atlas"""
        self.db = connect_mongodb()
        if self.db is None:
            raise ConnectionError("Failed to connect to MongoDB")

    def _setup_browser(self):
        """Setup Firefox browser with optimized options for speed"""
        options = Options()
        if self.headless:
            options.add_argument("--headless")

        # Performance optimizations
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-images")  # Don't load images for speed
        options.add_argument("--disable-javascript")  # Wait, we need JS for VTEX, skip this
        options.set_preference("dom.webdriver.enabled", False)
        options.set_preference('useAutomationExtension', False)
        options.set_preference("network.http.pipelining", True)
        options.set_preference("network.http.proxy.pipelining", True)
        options.set_preference("network.http.pipelining.maxrequests", 8)
        options.set_preference("content.notify.interval", 500000)
        options.set_preference("content.notify.ontimer", True)
        options.set_preference("content.switch.threshold", 250000)
        options.set_preference("browser.cache.memory.capacity", 65536)  # Increase cache capacity
        options.set_preference("browser.cache.disk.capacity", 102400)  # Increase disk cache
        options.set_preference("browser.sessionhistory.max_total_viewers", 0)  # Disable session history

        # Anti-detection measures
        options.add_argument("--disable-blink-features=AutomationControlled")

        # Use local GeckoDriver
        geckodriver_path = r"d:\dev\caminando-onlinev11\drivers\geckodriver.exe"
        service = Service(geckodriver_path)
        self.driver = webdriver.Firefox(service=service, options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        logger.debug(f"Browser initialized (headless: {self.headless}) - OPTIMIZED MODE: Performance enhancements enabled")

    def generate_slug(self, text):
        """Generate slug from text (similar to Subcategory.js method)"""
        return re.sub(r'[^\w\-]+', '', text.lower().strip().replace(' ', '-')).replace('--+', '-').strip('-')

    def get_categories_from_db(self):
        """Retrieve all active categories from MongoDB"""
        if self.db is None:
            raise ConnectionError("No database connection available")

        try:
            categories = list(self.db.categories.find(
                {"active": True},
                {"_id": 1, "name": 1, "slug": 1, "url": 1}
            ))
            print_info(f"Retrieved {len(categories)} active categories from database")
            return categories
        except Exception as e:
            print_error(f"Error retrieving categories: {e}")
            raise

    def extract_product_count(self, label_text):
        """Extract product count from label text like 'Aceites comunes (13)'"""
        match = re.search(r'\((\d+)\)$', label_text.strip())
        return int(match.group(1)) if match else 0

    def extract_subcategories(self, category_slug, category_slug_for_db):
        """
        Extract all subcategories for a given category from the expanded Sub-Categoría filter

        Returns:
            list: List of extracted subcategory dictionaries
        """
        extracted_subcategories = []

        try:
            # First, click on the Sub-Categoría filter button to expand it
            logger.debug(f"Clicking on Sub-Categoría filter button for category {category_slug}")
            try:
                subcategoria_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR,
                        ".vtex-search-result-3-x-accordionFilterContainer--sub-categoria .vtex-search-result-3-x-accordionFilterItem"))
                )
                # Use JavaScript click to avoid interception issues
                self.driver.execute_script("arguments[0].click();", subcategoria_button)
                time.sleep(1)  # Wait for expansion
                logger.debug("Successfully clicked Sub-Categoría filter button")
            except Exception as e:
                logger.warning(f"Could not click Sub-Categoría button: {e}")
                # Continue anyway, maybe it's already expanded

            # Find the specific Sub-Categoría filter container
            logger.debug(f"Looking for Sub-Categoría filter container in category {category_slug}")
            subcategoria_container = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,
                    ".vtex-search-result-3-x-accordionFilterContainer--sub-categoria"))
            )

            # Now find all subcategory checkboxes/labels within this container
            logger.debug(f"Looking for subcategory options within Sub-Categoría container")
            subcategory_options = subcategoria_container.find_elements(
                By.CSS_SELECTOR,
                ".vtex-checkbox__container, .vtex-checkbox__label"
            )

            logger.debug(f"Found {len(subcategory_options)} subcategory options in Sub-Categoría filter")

            # Debug: Show what we found
            if len(subcategory_options) == 0:
                logger.warning("No subcategory options found. Checking what elements exist in the container...")
                all_elements = subcategoria_container.find_elements(By.CSS_SELECTOR, "*")
                logger.info(f"Container has {len(all_elements)} total elements")
                for i, elem in enumerate(all_elements[:10]):  # Show first 10
                    try:
                        tag = elem.tag_name
                        classes = elem.get_attribute('class') or ''
                        text = elem.text[:50] if elem.text else ''
                        logger.info(f"  Element {i}: <{tag} class='{classes}'> '{text}'")
                    except:
                        logger.info(f"  Element {i}: Could not analyze")

            for index, option in enumerate(subcategory_options):
                try:
                    # Try different methods to get text
                    full_text = ""
                    try:
                        # Try textContent first (includes text from hidden elements)
                        full_text = option.get_attribute('textContent') or ""
                        if not full_text.strip():
                            # Fallback to innerText
                            full_text = option.get_attribute('innerText') or ""
                        if not full_text.strip():
                            # Last resort: regular .text
                            full_text = option.text or ""
                    except Exception:
                        full_text = option.text or ""

                    full_text = full_text.strip()

                    if not full_text:
                        continue

                    # Clean name (remove count in parentheses if present)
                    name = re.sub(r'\s*\(\d+\)\s*$', '', full_text).strip()

                    if not name:
                        continue

                    # Extract product count (may not be available in Disco's format)
                    product_count = self.extract_product_count(full_text)

                    # Generate slug
                    slug = self.generate_slug(name)

                    subcategory = {
                        'name': name,
                        'slug': slug,
                        'url': f'https://www.disco.com.ar/{category_slug}/{slug}',
                        'displayName': name,
                        'category': category_slug_for_db,
                        'priority': index,
                        'active': True,
                        'featured': True,  # Always true when extracted/found
                        'metadata': {
                            'productCount': product_count,
                            'productTypeCount': 0,
                            'lastUpdated': datetime.now(timezone.utc)
                        },
                        'createdAt': datetime.now(timezone.utc),
                        'updatedAt': datetime.now(timezone.utc)
                    }

                    extracted_subcategories.append(subcategory)

                except Exception as e:
                    logger.warning(f"Error processing subcategory option {index}: {e}")
                    continue

            print_success(f"Extracted {len(extracted_subcategories)} subcategories for category {category_slug}")

        except TimeoutException:
            logger.error(f"Timeout waiting for subcategory options in category {category_slug}")
            # Debug: try to find any checkbox elements on the page
            try:
                all_checkboxes = self.driver.find_elements(By.CSS_SELECTOR, ".vtex-checkbox__container")
                logger.info(f"Found {len(all_checkboxes)} total checkbox containers on page")
                for i, cb in enumerate(all_checkboxes[:5]):  # Show first 5
                    try:
                        text = cb.get_attribute('textContent') or cb.text
                        logger.info(f"Checkbox {i}: '{text[:50]}...'")
                    except:
                        logger.info(f"Checkbox {i}: Could not get text")
            except Exception as e:
                logger.error(f"Error in debug logging: {e}")
        except Exception as e:
            logger.error(f"Error extracting subcategories for {category_slug}: {e}")

        return extracted_subcategories

    def process_single_category(self, category, thread_id):
        """
        Process a single category with its own browser instance
        Returns the category slug and processing result
        """
        category_slug = category.get('slug')
        if not category_slug:
            logger.error(f"Thread {thread_id}: Category without slug found, skipping")
            return category_slug, False

        logger.info(f"Thread {thread_id}: Processing category: {category_slug}")

        # Create a new browser instance for this thread
        driver = None
        try:
            logger.debug(f"Thread {thread_id}: Creating Firefox options...")
            options = Options()
            if self.headless:
                options.add_argument("--headless")
            logger.debug(f"Thread {thread_id}: Browser initialized (headless: {self.headless})")

            # Anti-detection measures
            logger.debug(f"Thread {thread_id}: Setting anti-detection measures...")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.set_preference("dom.webdriver.enabled", False)
            options.set_preference('useAutomationExtension', False)

            # Use local GeckoDriver
            logger.debug(f"Thread {thread_id}: Setting up GeckoDriver service...")
            geckodriver_path = r"d:\dev\caminando-onlinev11\drivers\geckodriver.exe"
            service = Service(geckodriver_path)
            logger.debug(f"Thread {thread_id}: Creating Firefox WebDriver instance...")
            driver = webdriver.Firefox(service=service, options=options)
            logger.debug(f"Thread {thread_id}: Firefox WebDriver created successfully")

            logger.debug(f"Thread {thread_id}: Setting webdriver property...")
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            logger.debug(f"Thread {thread_id}: WebDriver setup complete")

            # Generate URL if not present
            category_url = category.get('url') or f"https://www.disco.com.ar/{category_slug}"

            # Navigate to category page
            logger.debug(f"Thread {thread_id}: Testing basic connectivity with google.com...")
            try:
                driver.get("https://www.google.com")
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.NAME, "q"))
                )
                logger.debug(f"Thread {thread_id}: Google loaded successfully")
            except Exception as e:
                logger.error(f"Thread {thread_id}: Cannot load Google: {e}")
                raise Exception(f"Browser connectivity test failed: {e}")

            logger.debug(f"Thread {thread_id}: Now loading Disco category page...")
            driver.get(category_url)

            # Wait for page to load - try multiple selectors
            page_loaded = False
            load_selectors = [
                ".vtex-search-result-3-x-filter",
                ".vtex-store-components-3-x-container",
                "body",
                "[data-testid]",
                ".vtex-flex-layout-0-x-flexRow"
            ]

            for selector in load_selectors:
                try:
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    logger.debug(f"Page loaded successfully using selector: {selector}")
                    page_loaded = True
                    break
                except TimeoutException:
                    continue

            if not page_loaded:
                logger.warning(f"Could not verify page load for {category_slug}, continuing anyway")

            # Additional wait for dynamic content
            time.sleep(1)

            # Try to expand all subcategories by clicking "Ver más" button if it exists
            try:
                # Disco may not have a "Ver más" button, but try common selectors
                ver_mas_selectors = [
                    "button.vtex-search-result-3-x-seeMoreButton",
                    ".vtex-search-result-3-x-seeMoreButton",
                    "button:contains('Ver más')"
                ]
                ver_mas_button = None
                for selector in ver_mas_selectors:
                    try:
                        ver_mas_button = WebDriverWait(driver, 3).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                        break
                    except:
                        continue

                if ver_mas_button:
                    driver.execute_script("arguments[0].click();", ver_mas_button)
                    time.sleep(1)  # Wait for expansion
                    logger.debug("Clicked 'Ver más' button")
            except (TimeoutException, NoSuchElementException):
                logger.debug("No 'Ver más' button found or already expanded")

            # Process subcategories using the shared database connection
            self._process_subcategories_for_category_threaded(category, driver)

            logger.info(f"Thread {thread_id}: Completed category {category_slug}")
            return category_slug, True

        except Exception as e:
            # Handle specific Selenium errors with cleaner messages
            error_msg = str(e)
            if "NoSuchElementError" in error_msg or "NoSuchElementException" in error_msg:
                logger.warning(f"Thread {thread_id}: Category {category_slug} has no subcategories or filter not found - skipping")
            elif "TimeoutException" in error_msg:
                logger.warning(f"Thread {thread_id}: Timeout waiting for elements in category {category_slug}")
                # Debug: check what elements are actually present
                try:
                    body_text = driver.find_element(By.TAG_NAME, "body").text[:200]
                    logger.info(f"Thread {thread_id}: Page body preview: {body_text}")
                    title = driver.title
                    logger.info(f"Thread {thread_id}: Page title: {title}")
                except:
                    logger.info(f"Thread {thread_id}: Could not get page content for debugging")
            else:
                logger.error(f"Thread {thread_id}: Failed to process category {category_slug}: {error_msg[:100]}...")
            return category_slug, False
        finally:
            if driver:
                driver.quit()

    def _process_subcategories_for_category_threaded(self, category, driver):
        """
        Process subcategories for a category using a specific driver instance
        This is a thread-safe version that uses the shared database connection
        """
        category_slug = category.get('slug')
        if not category_slug:
            return

        # Initialize variables to avoid UnboundLocalError
        extracted_subcategories = []
        added_count = 0
        updated_count = 0
        removed_count = 0

        # Step 3.2a: Get existing subcategories before processing
        try:
            # Get category name for backward compatibility
            category_doc = self.db.categories.find_one({"slug": category_slug}, {"name": 1})
            category_name = category_doc.get("name", category_slug) if category_doc else category_slug

            # Search for existing subcategories by both slug and name (for backward compatibility)
            existing_subcategories = list(self.db.subcategories.find(
                {"$or": [
                    {"category": category_slug, "active": True},
                    {"category": category_name, "active": True}
                ]},
                {"slug": 1, "_id": 0}
            ))
            existing_slugs = set(s['slug'] for s in existing_subcategories)
        except Exception as e:
            logger.error(f"Error getting existing subcategories for {category_slug}: {e}")
            existing_slugs = set()

        # Step 3.1 & 3.2b: Extract subcategories and process each one
        extracted_subcategories = self._extract_subcategories_threaded(driver, category_slug)

        # If no subcategories found, create a default one with same name as category
        if not extracted_subcategories:
            # Get category name from database
            category_doc = self.db.categories.find_one({"slug": category_slug}, {"name": 1})
            category_name = category_doc.get("name", category_slug) if category_doc else category_slug

            default_subcategory = {
                'name': category_name,
                'slug': category_slug,
                'url': f'https://www.disco.com.ar/{category_slug}?initialMap=c&initialQuery={category_slug}&map=category-1&query=/{category_slug}&searchState',
                'displayName': category_name,
                'category': category_slug,
                'priority': 0,
                'active': True,
                'featured': True,
                'metadata': {
                    'productCount': 0,
                    'productTypeCount': 0,
                    'lastUpdated': datetime.now(timezone.utc)
                },
                'createdAt': datetime.now(timezone.utc),
                'updatedAt': datetime.now(timezone.utc)
            }
            extracted_subcategories = [default_subcategory]
            logger.info(f"Created default subcategory for category: {category_name}")

        added_count = 0
        updated_count = 0

        for subcategory in extracted_subcategories:
            try:
                # Get category name for backward compatibility in upsert filter
                category_doc = self.db.categories.find_one({"slug": category_slug}, {"name": 1})
                category_name = category_doc.get("name", category_slug) if category_doc else category_slug

                result = self.db.subcategories.update_one(
                    {"$or": [
                        {"slug": subcategory['slug'], "category": category_slug},
                        {"slug": subcategory['slug'], "category": category_name}
                    ]},
                    {"$set": subcategory},
                    upsert=True
                )

                # Count added vs updated
                if result.upserted_id:
                    added_count += 1
                elif result.modified_count > 0:
                    updated_count += 1

            except Exception as e:
                logger.error(f"Error inserting/updating subcategory {subcategory['slug']}: {e}")

        # Step 3.2c: Handle removed subcategories
        extracted_slugs = set(s['slug'] for s in extracted_subcategories)
        removed_slugs = list(existing_slugs - extracted_slugs)

        removed_count = 0
        if removed_slugs:
            try:
                # Get category name for backward compatibility
                category_doc = self.db.categories.find_one({"slug": category_slug}, {"name": 1})
                category_name = category_doc.get("name", category_slug) if category_doc else category_slug

                result = self.db.subcategories.update_many(
                    {"$or": [
                        {"slug": {"$in": removed_slugs}, "category": category_slug},
                        {"slug": {"$in": removed_slugs}, "category": category_name}
                    ]},
                    {"$set": {
                        "featured": False,
                        "metadata.lastUpdated": datetime.now(timezone.utc)
                    }}
                )
                removed_count = result.modified_count
            except Exception as e:
                logger.error(f"Error marking removed subcategories for {category_slug}: {e}")

        # Consolidated logging
        logger.info(f"Category {category_slug}: {added_count} added, {updated_count} updated, {removed_count} removed subcategories")

        return added_count, updated_count, removed_count

    def _extract_subcategories_threaded(self, driver, category_slug):
        """
        Extract subcategories using a specific driver instance
        Thread-safe version of extract_subcategories
        """
        extracted_subcategories = []

        try:
            # Strategy: Find the specific subcategory container and extract labels from it
            logger.debug(f"Looking for subcategory container")

            # First, try to expand the subcategory accordion if it's collapsed
            try:
                # Look for accordion header that might need to be clicked
                accordion_headers = driver.find_elements(By.CSS_SELECTOR,
                    ".vtex-search-result-3-x-accordionFilterItem--sub-categoria .vtex-search-result-3-x-accordionFilterItemTrigger")

                for header in accordion_headers:
                    try:
                        # Check if it's already expanded
                        if "vtex-search-result-3-x-accordionFilterItem--sub-categoria--expanded" not in header.get_attribute("class"):
                            driver.execute_script("arguments[0].click();", header)
                            time.sleep(1)
                            logger.debug("Expanded subcategory accordion")
                        else:
                            logger.debug("Subcategory accordion already expanded")
                    except Exception as e:
                        logger.debug(f"Could not expand accordion: {e}")
                        continue
            except Exception as e:
                logger.debug(f"No accordion headers found: {e}")

            # Use the correct Disco VTEX selector based on the HTML structure
            # Try category-3 first (subcategories), then fallback to category-2 (categories as subcategories)
            container = None
            container_selectors = [
                ".vtex-search-result-3-x-filter__container--category-3",  # Subcategories
                ".vtex-search-result-3-x-filter__container--category-2"   # Categories (fallback)
            ]

            for selector in container_selectors:
                try:
                    container = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    logger.debug(f"Found container using selector: {selector}")
                    break
                except TimeoutException:
                    logger.debug(f"Container not found with selector: {selector}, trying next...")
                    continue

            if container is None:
                logger.warning(f"No subcategory or category container found for {category_slug}")
                print_warning(f"No container found for {category_slug}")
                return extracted_subcategories

            # Try to click "Mostrar más" button if it exists
            try:
                show_more_button = container.find_element(By.CSS_SELECTOR, ".vtex-search-result-3-x-seeMoreButton")
                driver.execute_script("arguments[0].click();", show_more_button)
                time.sleep(1)  # Wait for more items to load
                logger.debug("Clicked 'Mostrar más' button to load all subcategories")
            except (NoSuchElementException, TimeoutException):
                logger.debug("No 'Mostrar más' button found or already all items loaded")

            # Now find all subcategory labels within the container
            logger.debug(f"Looking for subcategory labels within the container")
            subcategory_labels = container.find_elements(
                By.CSS_SELECTOR,
                "label.vtex-checkbox__label"
            )

            logger.debug(f"Found {len(subcategory_labels)} subcategory labels in the container")

            logger.info(f"Found {len(subcategory_labels)} subcategory labels in the container")

            for index, label in enumerate(subcategory_labels):
                try:
                    # Try different methods to get text
                    full_text = ""
                    try:
                        # Try textContent first (includes text from hidden elements)
                        full_text = label.get_attribute('textContent') or ""
                        if not full_text.strip():
                            # Fallback to innerText
                            full_text = label.get_attribute('innerText') or ""
                        if not full_text.strip():
                            # Last resort: regular .text
                            full_text = label.text or ""
                    except Exception:
                        full_text = label.text or ""

                    full_text = full_text.strip()

                    if not full_text:
                        continue

                    # Clean name (remove count in parentheses)
                    name = re.sub(r'\s*\(\d+\)\s*$', '', full_text).strip()

                    if not name:
                        continue

                    # Extract product count
                    product_count = self.extract_product_count(full_text)

                    # Generate slug
                    slug = self.generate_slug(name)

                    subcategory = {
                        'name': name,
                        'slug': slug,
                        'url': f'https://www.disco.com.ar/{category_slug}?initialMap=c&initialQuery={category_slug}&map=category-1,category-3&query=/{category_slug}/{slug}&searchState',
                        'displayName': name,
                        'category': category_slug,
                        'priority': index,
                        'active': True,
                        'featured': True,  # Always true when extracted/found
                        'metadata': {
                            'productCount': product_count,
                            'productTypeCount': 0,
                            'lastUpdated': datetime.now(timezone.utc)
                        },
                        'createdAt': datetime.now(timezone.utc),
                        'updatedAt': datetime.now(timezone.utc)
                    }

                    extracted_subcategories.append(subcategory)

                except Exception as e:
                    logger.warning(f"Error processing subcategory label {index}: {e}")
                    continue

            print_success(f"Extracted {len(extracted_subcategories)} subcategories for category {category_slug}")

        except TimeoutException:
            logger.warning(f"Timeout waiting for subcategory container in category {category_slug}")
            # Debug: list all available filter elements on the page
            try:
                all_filters = driver.find_elements(By.CSS_SELECTOR, "[class*='filter'], [class*='Filter'], [class*='accordion']")
                logger.debug(f"Found {len(all_filters)} potential filter elements on page")
                for i, filter_elem in enumerate(all_filters[:5]):  # Show first 5
                    classes = filter_elem.get_attribute("class")
                    text = filter_elem.text[:50] if filter_elem.text else "No text"
                    logger.debug(f"Filter {i}: classes='{classes}' text='{text}'")

                # Try alternative selectors
                alt_selectors = [
                    ".vtex-search-result-3-x-filter__container--category-3",
                    ".vtex-search-result-3-x-filterContainer",
                    ".vtex-search-result-3-x-accordionFilter",
                    "[data-filter-type='category-3']",
                    ".filter-group"
                ]

                for selector in alt_selectors:
                    try:
                        alt_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        if alt_elements:
                            logger.debug(f"Alternative selector '{selector}' found {len(alt_elements)} elements")
                            for elem in alt_elements[:2]:
                                logger.debug(f"  Element text: {elem.text[:100]}")
                    except:
                        continue

            except Exception as debug_e:
                logger.error(f"Could not debug page elements: {debug_e}")

            print_warning(f"Timeout loading subcategories for {category_slug}")
        except Exception as e:
            # Clean error handling for extraction issues
            error_msg = str(e)
            if "RemoteError" in error_msg or "WebDriver" in error_msg:
                logger.warning(f"WebDriver error during subcategory extraction for {category_slug}")
                print_warning(f"WebDriver error extracting subcategories for {category_slug}")
            else:
                logger.error(f"Error extracting subcategories for {category_slug}: {error_msg[:100]}...")
                print_error(f"Error extracting subcategories for {category_slug}")

        return extracted_subcategories

    def process_category_parallel(self, category_data):
        """
        Process a single category with its own browser instance
        Thread-safe method for parallel processing
        """
        category, index = category_data
        category_slug = category.get('slug', 'unknown')
        category_slug_for_db = category_slug

        logger.info(f"Thread {index}: Processing category: {category_slug}")

        # Create a new browser instance for this thread
        driver = None
        try:
            logger.info(f"Thread {index}: Creating Firefox options...")
            options = Options()
            if self.headless:
                options.add_argument("--headless")
            logger.info(f"Thread {index}: Browser initialized (headless: {self.headless})")

            # Anti-detection measures
            logger.info(f"Thread {index}: Setting anti-detection measures...")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.set_preference("dom.webdriver.enabled", False)
            options.set_preference('useAutomationExtension', False)

            # Use local GeckoDriver
            logger.info(f"Thread {index}: Setting up GeckoDriver service...")
            geckodriver_path = r"d:\dev\caminando-onlinev11\drivers\geckodriver.exe"
            service = Service(geckodriver_path)
            logger.info(f"Thread {index}: Creating Firefox WebDriver instance...")
            driver = webdriver.Firefox(service=service, options=options)
            logger.info(f"Thread {index}: Firefox WebDriver created successfully")

            logger.info(f"Thread {index}: Setting webdriver property...")
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            logger.info(f"Thread {index}: WebDriver setup complete")

            # Generate URL if not present
            category_url = category.get('url') or f"https://www.disco.com.ar/{category_slug}"

            # Navigate to category page
            logger.debug(f"Thread {index}: Testing basic connectivity with google.com...")
            try:
                driver.get("https://www.google.com")
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.NAME, "q"))
                )
                logger.debug(f"Thread {index}: Google loaded successfully")
            except Exception as e:
                logger.error(f"Thread {index}: Cannot load Google: {e}")
                raise Exception(f"Browser connectivity test failed: {e}")

            logger.debug(f"Thread {index}: Now loading Disco category page...")
            driver.get(category_url)

            # Wait for page to load - try multiple selectors
            page_loaded = False
            load_selectors = [
                ".vtex-search-result-3-x-filter",
                ".vtex-store-components-3-x-container",
                "body",
                "[data-testid]",
                ".vtex-flex-layout-0-x-flexRow"
            ]

            for selector in load_selectors:
                try:
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    logger.debug(f"Thread {index}: Page loaded successfully using selector: {selector}")
                    page_loaded = True
                    break
                except TimeoutException:
                    continue

            if not page_loaded:
                logger.warning(f"Thread {index}: Could not verify page load for {category_slug}, continuing anyway")

            # Additional wait for dynamic content
            time.sleep(1)

            # Try to expand all subcategories by clicking "Ver más" button if it exists
            try:
                # Disco may not have a "Ver más" button, but try common selectors
                ver_mas_selectors = [
                    "button.vtex-search-result-3-x-seeMoreButton",
                    ".vtex-search-result-3-x-seeMoreButton",
                    "button:contains('Ver más')"
                ]
                ver_mas_button = None
                for selector in ver_mas_selectors:
                    try:
                        ver_mas_button = WebDriverWait(driver, 3).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                        break
                    except:
                        continue

                if ver_mas_button:
                    driver.execute_script("arguments[0].click();", ver_mas_button)
                    time.sleep(1)  # Wait for expansion
                    logger.debug(f"Thread {index}: Clicked 'Ver más' button")
            except (TimeoutException, NoSuchElementException):
                logger.debug(f"Thread {index}: No 'Ver más' button found or already expanded")

            # Process subcategories using the shared database connection
            subcategory_result = self._process_subcategories_for_category_threaded(category, driver)

            logger.debug(f"Thread {index}: Completed category {category_slug}")
            return category_slug, True, subcategory_result

        except Exception as e:
            # Handle specific Selenium errors with cleaner messages
            error_msg = str(e)
            if "NoSuchElementError" in error_msg or "NoSuchElementException" in error_msg:
                logger.warning(f"Thread {index}: Category {category_slug} has no subcategories or filter not found - skipping")
            elif "TimeoutException" in error_msg:
                logger.warning(f"Thread {index}: Timeout waiting for elements in category {category_slug}")
                # Debug: check what elements are actually present
                try:
                    body_text = driver.find_element(By.TAG_NAME, "body").text[:200]
                    logger.info(f"Thread {index}: Page body preview: {body_text}")
                    title = driver.title
                    logger.info(f"Thread {index}: Page title: {title}")
                except:
                    logger.info(f"Thread {index}: Could not get page content for debugging")
            else:
                logger.error(f"Thread {index}: Failed to process category {category_slug}: {error_msg[:100]}...")
            return category_slug, False, (0, 0, 0)
        finally:
            if driver:
                driver.quit()

    def run_scraping(self):
        """Main scraping function - processes all categories in parallel"""
        print_header("Disco Subcategories Scraper", "🛒")
        print_info(f"Processing {len(self.get_categories_from_db())} categories with {self.max_workers} parallel threads")

        # Get categories from database
        categories = self.get_categories_from_db()

        if len(categories) == 0:
            print_warning("No categories to process")
            return

        # Process categories in parallel
        completed_count = 0
        failed_count = 0
        total_subcategories = 0

        print_info("Starting parallel processing...")

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_category = {
                executor.submit(self.process_category_parallel, (category, i)): (category, i)
                for i, category in enumerate(categories, 1)
            }

            # Process results as they complete
            for future in as_completed(future_to_category):
                category, index = future_to_category[future]
                try:
                    slug, success, subcategory_stats = future.result()
                    if success:
                        added, updated, removed = subcategory_stats
                        completed_count += 1
                        total_subcategories += added  # Solo contar las agregadas para el total
                        print_success(f"Completed category {slug} ({completed_count}/{len(categories)}) - {added} added, {updated} updated, {removed} removed")
                    else:
                        failed_count += 1
                        print_warning(f"Failed to process category {slug}")
                except Exception as e:
                    failed_count += 1
                    category_slug = category.get('slug', 'unknown')
                    # Clean error message for thread execution issues
                    error_msg = str(e)
                    if "RemoteError" in error_msg or "WebDriver" in error_msg:
                        print_warning(f"WebDriver error for {category_slug}")
                    else:
                        print_error(f"Thread error for {category_slug}: {error_msg[:50]}...")

        print_success(f"Completed parallel subcategories scraping: {completed_count} successful, {failed_count} failed")
        print_success(f"Total subcategories processed: {total_subcategories}")
        print_separator()

    def close(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()
            print_info("Browser closed")
        if hasattr(self, 'db') and self.db is not None:
            self.db.client.close()
            logger.info("MongoDB connection closed")

def main():
    """Main entry point"""
    scraper = None
    try:
        # Initialize scraper (headless=True for production performance)
        scraper = DiscoSubcategoriesScraper(headless=True)

        # Run scraping
        scraper.run_scraping()

    except KeyboardInterrupt:
        print_warning("Scraping interrupted by user")
    except Exception as e:
        print_error(f"Unexpected error: {e}")
    finally:
        if scraper:
            scraper.close()
        print_info("Scraping session ended")

if __name__ == "__main__":
    main()
