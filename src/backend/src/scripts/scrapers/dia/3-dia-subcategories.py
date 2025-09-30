#!/usr/bin/env python3
"""
Dia Subcategories Scraper
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
logger.setLevel(logging.INFO)

# File handler (overwrite mode to avoid old logs)
file_handler = logging.FileHandler('logs/3-dia-subcategories.log', mode='w')
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

# Console handler with colors
console_handler = logging.StreamHandler()
console_formatter = ColoredFormatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)

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
        mongo_uri = os.getenv('MONGO_DIA_URI')

        if not mongo_uri:
            raise ValueError("MONGO_DIA_URI environment variable not set")

        client = pymongo.MongoClient(mongo_uri)
        db = client.dia

        # Test the connection
        client.admin.command('ping')
        print_success("Connected to MongoDB Atlas - dia database")
        return db

    except ConnectionFailure as e:
        print_error(f"Failed to connect to MongoDB: {e}")
        raise
    except Exception as e:
        print_error(f"Unexpected MongoDB error: {e}")
        raise

class DiaSubcategoriesScraper:
    def __init__(self, headless=False):
        """Initialize the scraper with MongoDB connection and browser setup"""
        self.headless = headless
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
        """Setup Firefox browser with options"""
        options = Options()
        if self.headless:
            options.add_argument("--headless")

        # Anti-detection measures
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.set_preference("dom.webdriver.enabled", False)
        options.set_preference('useAutomationExtension', False)

        # Use local GeckoDriver
        geckodriver_path = r"d:\dev\caminando-onlinev11\drivers\geckodriver.exe"
        service = Service(geckodriver_path)
        self.driver = webdriver.Firefox(service=service, options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        logger.info(f"Browser initialized (headless: {self.headless})")

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
            # Find the specific Sub-Categoría filter container first
            # TODO: Adapt this selector for Dia website structure
            logger.debug(f"Looking for Sub-Categoría filter container in category {category_slug}")
            subcategoria_container = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,
                    "div.diaio-search-result-0-x-accordionFilterContainer--categoria"))
            )

            # Now find all subcategory labels specifically within this container
            logger.debug(f"Looking for subcategory labels within Sub-Categoría container")
            subcategory_labels = subcategoria_container.find_elements(
                By.CSS_SELECTOR,
                "label.vtex-checkbox__label.w-100.c-on-base.pointer"
            )

            logger.info(f"Found {len(subcategory_labels)} subcategory labels in Sub-Categoría filter")

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
                        'url': f'https://diaonline.supermercadosdia.com.ar/{category_slug}?initialMap=c&initialQuery={category_slug}&map=category-1,category-3&query=/{category_slug}/{slug}&searchState',
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
                    logger.warning(f"Error processing subcategory label {index}: {e}")
                    continue

            print_success(f"Extracted {len(extracted_subcategories)} subcategories for category {category_slug}")

        except TimeoutException:
            logger.error(f"Timeout waiting for subcategory labels in category {category_slug}")
            # Debug: try to find any checkbox labels on the page
            try:
                all_labels = self.driver.find_elements(By.CSS_SELECTOR, "label")
                logger.info(f"Found {len(all_labels)} total labels on page")
                for i, lbl in enumerate(all_labels[:5]):  # Show first 5
                    logger.info(f"Label {i}: '{lbl.text}' (class: {lbl.get_attribute('class')})")
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
            options = Options()
            options.add_argument("--headless")

            # Anti-detection measures
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.set_preference("dom.webdriver.enabled", False)
            options.set_preference('useAutomationExtension', False)

            # Use local GeckoDriver
            geckodriver_path = r"d:\dev\caminando-onlinev11\drivers\geckodriver.exe"
            service = Service(geckodriver_path)
            driver = webdriver.Firefox(service=service, options=options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            # Generate URL if not present
            category_url = category.get('url') or f"https://diaonline.supermercadosdia.com.ar/{category_slug}"

            # Navigate to category page
            driver.get(category_url)

            # Wait for page to load
            # TODO: Adapt this selector for Dia website structure
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "diaio-search-result-0-x-filter"))
            )

            # Additional wait for dynamic content
            time.sleep(3)

            # Try to expand all subcategories by clicking "Ver más" button
            try:
                ver_mas_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.diaio-search-result-0-x-seeMoreButton"))
                )
                driver.execute_script("arguments[0].click();", ver_mas_button)
                time.sleep(3)  # Wait for expansion
            except (TimeoutException, NoSuchElementException):
                pass  # Button not found or already expanded, continue anyway

            # Process subcategories using the shared database connection
            self._process_subcategories_for_category_threaded(category, driver)

            logger.info(f"Thread {thread_id}: Completed category {category_slug}")
            return category_slug, True

        except Exception as e:
            # Handle specific Selenium errors with cleaner messages
            if "NoSuchElementError" in str(type(e)) or "NoSuchElementError" in str(e):
                logger.warning(f"Thread {thread_id}: Category {category_slug} has no subcategories or filter not found - skipping")
            else:
                logger.error(f"Thread {thread_id}: Failed to process category {category_slug}: {str(e)[:100]}...")
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
                'url': f'https://diaonline.supermercadosdia.com.ar/{category_slug}?initialMap=c&initialQuery={category_slug}&map=category-1&query=/{category_slug}&searchState',
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
        # Only mark as removed if we successfully extracted from the PRIMARY container (category-3)
        # If we used fallback (category-2) or extraction failed, keep existing subcategories active
        extracted_slugs = set(s['slug'] for s in extracted_subcategories)
        removed_count = 0

        # Check if we used fallback container (category-2) or had extraction issues
        used_fallback = False
        if extracted_subcategories:
            # Check if any extracted subcategory has metadata indicating fallback was used
            # or if we know category-3 wasn't available
            try:
                category_doc = self.db.categories.find_one({"slug": category_slug})
                category_name = category_doc.get("name", category_slug) if category_doc else category_slug

                # If there were previously extracted subcategories but we extracted from fallback,
                # don't mark anything as removed
                existing_prev_extracted = list(self.db.subcategories.find(
                    {"$or": [
                        {"category": category_slug, "metadata.prevExtracted": True},
                        {"category": category_name, "metadata.prevExtracted": True}
                    ]},
                    {"slug": 1, "_id": 0}
                ))

                if existing_prev_extracted and len(extracted_subcategories) < len(existing_prev_extracted):
                    # We extracted fewer subcategories than previously existed, likely used fallback
                    used_fallback = True
                    logger.info(f"Used fallback extraction for {category_slug}, keeping existing subcategories active")
            except Exception as e:
                logger.error(f"Error checking fallback status: {e}")

        if extracted_subcategories and not used_fallback:  # Only if we actually extracted from primary container
            removed_slugs = list(existing_slugs - extracted_slugs)
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
                    logger.info(f"Marked {removed_count} subcategories as removed for {category_slug}")
                except Exception as e:
                    logger.error(f"Error marking removed subcategories for {category_slug}: {e}")
        elif used_fallback:
            logger.info(f"Keeping all existing subcategories active for {category_slug} (fallback extraction used)")
            removed_count = 0  # Don't remove anything when using fallback
        elif not extracted_subcategories and existing_slugs:
            logger.info(f"Keeping {len(existing_slugs)} existing subcategories active for {category_slug} (extraction failed or empty)")
            removed_count = 0  # Don't remove anything if extraction failed

        # Consolidated logging
        logger.info(f"Category {category_slug}: {added_count} added, {updated_count} updated, {removed_count} removed subcategories")

    def _extract_subcategories_threaded(self, driver, category_slug):
        """
        Extract subcategories using a specific driver instance
        Thread-safe version of extract_subcategories
        """
        extracted_subcategories = []

        try:
            # Strategy: Find the specific subcategory container and extract labels from it
            logger.debug(f"Looking for subcategory container")
            container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,
                    "div.diaio-search-result-0-x-filter__container.diaio-search-result-0-x-filter__container--plp.bb.b--muted-4.diaio-search-result-0-x-filter__container--category-3"))
            )

            # Now find all subcategory labels specifically within this container
            logger.debug(f"Looking for subcategory labels within the container")
            subcategory_labels = container.find_elements(
                By.CSS_SELECTOR,
                "label.vtex-checkbox__label.w-100.c-on-base.pointer"
            )

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
                        'url': f'https://diaonline.supermercadosdia.com.ar/{category_slug}?initialMap=c&initialQuery={category_slug}&map=category-1,category-3&query=/{category_slug}/{slug}&searchState',
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

        # Create a new browser instance for this thread
        driver = None
        try:
            # Setup browser for this thread
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.set_preference("dom.webdriver.enabled", False)
            options.set_preference('useAutomationExtension', False)

            geckodriver_path = r"d:\dev\caminando-onlinev11\drivers\geckodriver.exe"
            service = Service(geckodriver_path)
            driver = webdriver.Firefox(service=service, options=options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            # Navigate to category page
            category_url = f"https://diaonline.supermercadosdia.com.ar/{category_slug}"
            driver.get(category_url)

            # Wait for page to load
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.diaio-search-result-0-x-filter__container"))
            )

            # Try to expand all subcategories by clicking "Ver más" button
            try:
                ver_mas_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.diaio-search-result-0-x-seeMoreButton"))
                )
                driver.execute_script("arguments[0].click();", ver_mas_button)
                time.sleep(3)  # Wait for expansion
            except (TimeoutException, NoSuchElementException):
                pass  # Button not found or already expanded, continue anyway

            # Extract subcategories using the thread's driver
            extracted_subcategories = self._extract_subcategories_threaded(driver, category_slug)

            # If no subcategories found, create a default one
            if not extracted_subcategories:
                category_doc = self.db.categories.find_one({"slug": category_slug}, {"name": 1})
                category_name = category_doc.get("name", category_slug) if category_doc else category_slug

                default_subcategory = {
                    'name': category_name,
                    'slug': category_slug,
                    'url': f'https://diaonline.supermercadosdia.com.ar/{category_slug}?initialMap=c&initialQuery={category_slug}&map=category-1&query=/{category_slug}&searchState',
                    'displayName': category_name,
                    'category': category_slug_for_db,
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

            # Process subcategories (insert/update in database)
            added_count = 0
            updated_count = 0

            for subcategory in extracted_subcategories:
                try:
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

                    if result.upserted_id:
                        added_count += 1
                    elif result.modified_count > 0:
                        updated_count += 1

                except Exception as e:
                    logger.error(f"Thread {index}: Error inserting/updating subcategory {subcategory['slug']}: {e}")

            # Handle removed subcategories
            try:
                existing_subcategories = list(self.db.subcategories.find(
                    {"category": {"$in": [category_slug, category_name]}},
                    {"slug": 1, "_id": 0}
                ))
                existing_slugs = set(s['slug'] for s in existing_subcategories)
                extracted_slugs = set(s['slug'] for s in extracted_subcategories)
                removed_slugs = list(existing_slugs - extracted_slugs)

                removed_count = 0
                if removed_slugs:
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

                logger.info(f"Thread {index}: Category {category_slug}: {added_count} added, {updated_count} updated, {removed_count} removed subcategories")
                return category_slug, True, len(extracted_subcategories)

            except Exception as e:
                logger.error(f"Thread {index}: Error handling removed subcategories for {category_slug}: {e}")
                return category_slug, True, len(extracted_subcategories)  # Still count as success

        except Exception as e:
            # Clean error handling - avoid noisy WebDriver stacktraces
            error_msg = str(e)
            if "RemoteError" in error_msg or "WebDriver" in error_msg:
                # WebDriver connectivity/page loading issues
                logger.warning(f"Thread {index}: WebDriver error for category {category_slug} - page may be temporarily unavailable")
                print_warning(f"WebDriver error for {category_slug} (temporary connectivity issue)")
            elif "TimeoutException" in error_msg:
                # Page loading timeout
                logger.warning(f"Thread {index}: Timeout loading category {category_slug} - page took too long to load")
                print_warning(f"Timeout loading {category_slug}")
            elif "NoSuchElementException" in error_msg:
                # Element not found
                logger.warning(f"Thread {index}: Required elements not found for category {category_slug} - page structure may have changed")
                print_warning(f"Page structure issue for {category_slug}")
            else:
                # Other unexpected errors - show first 100 chars only
                logger.error(f"Thread {index}: Unexpected error processing category {category_slug}: {error_msg[:100]}...")
                print_error(f"Unexpected error for {category_slug}: {error_msg[:50]}...")

            return category_slug, False, 0
        finally:
            if driver:
                driver.quit()

    def run_scraping(self):
        """Main scraping function - processes all categories in parallel"""
        print_header("Dia Subcategories Scraper", "🛒")
        print_info("Starting Dia subcategories scraping with parallel processing (8 concurrent categories)")

        # Get categories from database
        categories = self.get_categories_from_db()

        if not categories:
            print_error("No categories found in database")
            return

        if len(categories) == 0:
            print_warning("No categories to process")
            return

        # Process all categories in parallel with 8 workers
        completed_count = 0
        failed_count = 0
        total_subcategories = 0

        print_info(f"Processing {len(categories)} categories with 8 concurrent threads...")

        with ThreadPoolExecutor(max_workers=8) as executor:
            # Submit all tasks
            future_to_category = {
                executor.submit(self.process_category_parallel, (category, i)): (category, i)
                for i, category in enumerate(categories, 1)
            }

            # Process results as they complete
            for future in as_completed(future_to_category):
                category, index = future_to_category[future]
                try:
                    slug, success, subcategory_count = future.result()
                    if success:
                        completed_count += 1
                        total_subcategories += subcategory_count
                        print_success(f"Completed category {slug} ({completed_count}/{len(categories)}) - {subcategory_count} subcategories")
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
        # Initialize scraper (headless=True for production, change to False for debugging)
        scraper = DiaSubcategoriesScraper(headless=True)

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
