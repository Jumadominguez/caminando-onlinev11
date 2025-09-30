#!/usr/bin/env python3
"""
Dia Single Category Scraper - Process only golosinas-y-alfajores

Este scraper es para procesar una sola categoria. Lo vamos a usar despues para el dashboard cuando quiera scrapear categorias individuales.
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

class DiaSingleCategoryScraper:
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

        logger = logging.getLogger(__name__)
        logger.info(f"Browser initialized (headless: {self.headless})")

    def generate_slug(self, text):
        """Generate slug from text (similar to Subcategory.js method)"""
        return re.sub(r'[^\w\-]+', '', text.lower().strip().replace(' ', '-')).replace('--+', '-').strip('-')

    def extract_product_count(self, label_text):
        """Extract product count from label text like 'Aceites comunes (13)'"""
        match = re.search(r'\((\d+)\)$', label_text.strip())
        return int(match.group(1)) if match else 0

    def process_single_category(self, category_slug):
        """
        Process a single category with its own browser instance
        """
        logger = logging.getLogger(__name__)

        # Get category from database
        category = self.db.categories.find_one({"slug": category_slug})
        if not category:
            print_error(f"Category {category_slug} not found in database")
            return False

        print_info(f"Processing category: {category_slug}")

        try:
            # Generate URL if not present
            category_url = category.get('url') or f"https://diaonline.supermercadosdia.com.ar/{category_slug}"

            print_info(f"Navigating to: {category_url}")

            # Navigate to category page
            self.driver.get(category_url)

            # Wait for page to load
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.diaio-search-result-0-x-filter__container"))
            )

            # Additional wait for dynamic content
            time.sleep(5)

            # Try to expand all subcategories by clicking "Ver más" button
            try:
                ver_mas_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.diaio-search-result-0-x-seeMoreButton"))
                )
                self.driver.execute_script("arguments[0].click();", ver_mas_button)
                time.sleep(3)  # Wait for expansion
                print_info("Expanded subcategory filter")
            except (TimeoutException, NoSuchElementException):
                print_info("No 'Ver más' button found or already expanded")

            # Extract subcategories
            extracted_subcategories = self._extract_subcategories()

            # If no subcategories found, create a default one
            if not extracted_subcategories:
                category_name = category.get('name', category_slug)
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
                print_info(f"Created default subcategory for category: {category_name}")

            # Process subcategories (insert/update in database)
            added_count = 0
            updated_count = 0

            for subcategory in extracted_subcategories:
                try:
                    result = self.db.subcategories.update_one(
                        {"slug": subcategory['slug'], "category": category_slug},
                        {"$set": subcategory},
                        upsert=True
                    )

                    if result.upserted_id:
                        added_count += 1
                    elif result.modified_count > 0:
                        updated_count += 1

                except Exception as e:
                    logger.error(f"Error inserting/updating subcategory {subcategory['slug']}: {e}")

            # Handle removed subcategories
            existing_subcategories = list(self.db.subcategories.find(
                {"category": category_slug},
                {"slug": 1, "_id": 0}
            ))
            existing_slugs = set(s['slug'] for s in existing_subcategories)
            extracted_slugs = set(s['slug'] for s in extracted_subcategories)
            removed_slugs = list(existing_slugs - extracted_slugs)

            removed_count = 0
            if removed_slugs:
                result = self.db.subcategories.update_many(
                    {"slug": {"$in": removed_slugs}, "category": category_slug},
                    {"$set": {
                        "featured": False,
                        "metadata.lastUpdated": datetime.now(timezone.utc)
                    }}
                )
                removed_count = result.modified_count

            print_success(f"Category {category_slug}: {added_count} added, {updated_count} updated, {removed_count} removed subcategories")
            return True, len(extracted_subcategories)

        except Exception as e:
            error_msg = str(e)
            if "RemoteError" in error_msg or "WebDriver" in error_msg:
                print_warning(f"WebDriver error for category {category_slug} - page may be temporarily unavailable")
            elif "TimeoutException" in error_msg:
                print_warning(f"Timeout loading category {category_slug} - page took too long to load")
            elif "NoSuchElementException" in error_msg:
                print_warning(f"Required elements not found for category {category_slug} - page structure may have changed")
            else:
                print_error(f"Unexpected error processing category {category_slug}: {error_msg[:50]}...")

            return False, 0

    def _extract_subcategories(self):
        """
        Extract subcategories from the current page
        """
        extracted_subcategories = []

        try:
            # Strategy: Find the specific subcategory container and extract labels from it
            logger = logging.getLogger(__name__)
            logger.debug("Looking for subcategory container")

            container = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,
                    "div.diaio-search-result-0-x-filter__container.diaio-search-result-0-x-filter__container--category-3"))
            )

            # Now find all subcategory labels specifically within this container
            logger.debug("Looking for subcategory labels within the container")
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

                    # Get category slug from current URL or database
                    current_url = self.driver.current_url
                    category_slug = current_url.split('/')[-1].split('?')[0]  # Extract from URL

                    subcategory = {
                        'name': name,
                        'slug': slug,
                        'url': f'https://diaonline.supermercadosdia.com.ar/{category_slug}?initialMap=c&initialQuery={category_slug}&map=category-1,category-3&query=/{category_slug}/{slug}&searchState',
                        'displayName': name,
                        'category': category_slug,
                        'priority': index,
                        'active': True,
                        'featured': True,
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

            print_success(f"Extracted {len(extracted_subcategories)} subcategories")

        except TimeoutException:
            print_warning("Timeout waiting for subcategory container")
        except Exception as e:
            print_error(f"Error extracting subcategories: {str(e)[:100]}...")

        return extracted_subcategories

    def close(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()
            print_info("Browser closed")
        if hasattr(self, 'db') and self.db is not None:
            self.db.client.close()
            logger = logging.getLogger(__name__)
            logger.info("MongoDB connection closed")

def main():
    """Main entry point"""
    scraper = None
    try:
        # Initialize scraper (headless=False for debugging the problematic category)
        scraper = DiaSingleCategoryScraper(headless=False)

        # Process only the golosinas-y-alfajores category
        print_header("Dia Single Category Scraper", "🍬")
        print_info("Processing only golosinas-y-alfajores category")

        success, subcategory_count = scraper.process_single_category("golosinas-y-alfajores")

        if success:
            print_success(f"Successfully processed golosinas-y-alfajores with {subcategory_count} subcategories")
        else:
            print_error("Failed to process golosinas-y-alfajores category")

        print_separator()

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