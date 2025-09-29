#!/usr/bin/env python3
"""
Carrefour Subcategories Scraper
Complete implementation based on carrefour_subcategories_scraping_process.md

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
file_handler = logging.FileHandler('logs/3-carrefour-subcategories.log', mode='w')
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
        mongo_uri = os.getenv('MONGO_CARREFOUR_URI')

        if not mongo_uri:
            raise ValueError("MONGO_CARREFOUR_URI environment variable not set")

        client = pymongo.MongoClient(mongo_uri)
        db = client.carrefour

        # Test the connection
        client.admin.command('ping')
        print_success("Connected to MongoDB Atlas - carrefour database")
        return db

    except ConnectionFailure as e:
        print_error(f"Failed to connect to MongoDB: {e}")
        raise
    except Exception as e:
        print_error(f"Unexpected MongoDB error: {e}")
        raise

class CarrefourSubcategoriesScraper:
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
            logger.debug(f"Looking for Sub-Categoría filter container in category {category_slug}")
            subcategoria_container = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,
                    "div.valtech-carrefourar-search-result-3-x-filter__container--category-3"))
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
                        'url': f'https://www.carrefour.com.ar/{category_slug}?initialMap=c&initialQuery={category_slug}&map=category-1,category-3&query=/{category_slug}/{slug}&searchState',
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
            category_url = category.get('url') or f"https://www.carrefour.com.ar/{category_slug}"

            # Navigate to category page
            driver.get(category_url)

            # Wait for page to load
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "valtech-carrefourar-search-result-3-x-filter"))
            )

            # Additional wait for dynamic content
            time.sleep(3)

            # Find Sub-Categoría filter container
            subcategoria_container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,
                    "div.valtech-carrefourar-search-result-3-x-filter__container--category-3"))
            )

            # Try to expand the filter if needed
            try:
                # Look for "Ver más" button
                ver_mas_button = subcategoria_container.find_element(
                    By.CSS_SELECTOR,
                    "button.valtech-carrefourar-search-result-3-x-seeMoreButton"
                )

                # Scroll to make button visible and ensure it's in viewport
                driver.execute_script("""
                    arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});
                    arguments[0].focus();
                """, ver_mas_button)
                time.sleep(2)

                # Try JavaScript click first (more reliable)
                try:
                    driver.execute_script("arguments[0].click();", ver_mas_button)
                except Exception:
                    # Fallback to regular click
                    ver_mas_button.click()

                # Wait for expansion to complete
                time.sleep(4)

            except NoSuchElementException:
                logger.info(f"Thread {thread_id}: Sub-Categoría filter appears to be already expanded for {category_slug}")

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
                'url': f'https://www.carrefour.com.ar/{category_slug}?initialMap=c&initialQuery={category_slug}&map=category-1&query=/{category_slug}&searchState',
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

    def _extract_subcategories_threaded(self, driver, category_slug):
        """
        Extract subcategories using a specific driver instance
        Thread-safe version of extract_subcategories
        """
        extracted_subcategories = []

        try:
            # Find the specific Sub-Categoría filter container first
            logger.debug(f"Looking for Sub-Categoría filter container in category {category_slug}")
            subcategoria_container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,
                    "div.valtech-carrefourar-search-result-3-x-filter__container--category-3"))
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
                        'url': f'https://www.carrefour.com.ar/{category_slug}?initialMap=c&initialQuery={category_slug}&map=category-1,category-3&query=/{category_slug}/{slug}&searchState',
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
            logger.error(f"Timeout waiting for subcategory labels in category {category_slug}")
            # Debug: try to find any checkbox labels on the page
            try:
                all_labels = driver.find_elements(By.CSS_SELECTOR, "label")
                logger.info(f"Found {len(all_labels)} total labels on page")
                for i, lbl in enumerate(all_labels[:5]):  # Show first 5
                    logger.info(f"Label {i}: '{lbl.text}' (class: {lbl.get_attribute('class')})")
            except Exception as e:
                logger.error(f"Error in debug logging: {e}")
        except Exception as e:
            logger.error(f"Error extracting subcategories for {category_slug}: {e}")

        return extracted_subcategories

    def run_scraping(self):
        """Main scraping function with concurrent processing (3 categories at a time)"""
        print_header("Carrefour Subcategories Scraper", "🛒")
        print_info("Starting Carrefour subcategories scraping with concurrent processing (8 categories simultaneously)")

        # Get categories from database
        categories = self.get_categories_from_db()

        if not categories:
            print_error("No categories found in database")
            return

        # Filter out "Indumentaria" category
        categories = [cat for cat in categories if cat.get('name', '').lower() != 'indumentaria']
        filtered_count = len(categories)

        if len(categories) == 0:
            print_warning("No categories to process after filtering out 'Indumentaria'")
            return

                # Process all categories concurrently (8 at a time)
        print_info(f"Filtered out 'Indumentaria' category. Processing {filtered_count} categories concurrently (8 at a time)")

        completed_count = 0
        failed_count = 0

        # Use ThreadPoolExecutor with 8 workers for concurrent processing
        # WARNING: High concurrency may cause:
        # - High memory/CPU usage
        # - Potential blocking by target website
        # - System instability
        # Consider reducing max_workers if issues occur
        with ThreadPoolExecutor(max_workers=8) as executor:
            # Submit all tasks
            future_to_category = {
                executor.submit(self.process_single_category, category, i % 8 + 1): category
                for i, category in enumerate(categories)
            }

            # Process completed tasks as they finish
            for future in as_completed(future_to_category):
                category = future_to_category[future]
                category_slug = category.get('slug', 'unknown')

                try:
                    slug, success = future.result()
                    completed_count += 1

                    if success:
                        print_success(f"Completed category {slug} ({completed_count}/{len(categories)})")
                    else:
                        failed_count += 1
                        print_warning(f"Failed to process category {slug}")

                except Exception as e:
                    failed_count += 1
                    print_error(f"Exception processing category {category_slug}: {str(e)[:100]}...")

        print_success(f"Completed subcategories scraping: {completed_count} successful, {failed_count} failed")
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
        scraper = CarrefourSubcategoriesScraper(headless=True)

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