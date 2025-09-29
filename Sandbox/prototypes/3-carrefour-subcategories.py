#!/usr/bin/env python3
"""
Carrefour Subcategories Scraper - Level 3
Complete implementation based on carrefour_subcategories_scraping_process.md

Author: GitHub Copilot
Date: September 29, 2025
"""

import time
import logging
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import pymongo
from pymongo.errors import ConnectionFailure

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('3-carrefour-subcategories.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

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
        try:
            # Replace with actual connection string
            client = pymongo.MongoClient("mongodb+srv://<username>:<password>@<cluster>.mongodb.net/carrefour?retryWrites=true&w=majority")
            self.db = client.carrefour
            logger.info("Connected to MongoDB Atlas - carrefour database")
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            # For testing without DB connection
            logger.warning("Running in TEST MODE - No database operations will be performed")
            self.db = None  # Set to None for test mode
        except Exception as e:
            logger.error(f"Unexpected MongoDB error: {e}")
            self.db = None

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
            # Test mode - return mock data
            mock_categories = [
                {"name": "Almacén", "slug": "almacen", "url": "https://www.carrefour.com.ar/almacen"},
                {"name": "Bebidas", "slug": "bebidas", "url": "https://www.carrefour.com.ar/bebidas"}
            ]
            logger.info(f"TEST MODE: Using {len(mock_categories)} mock categories")
            return mock_categories

        try:
            categories = list(self.db.categories.find(
                {"active": True},
                {"_id": 1, "name": 1, "slug": 1, "url": 1}
            ))
            logger.info(f"Retrieved {len(categories)} active categories from database")
            return categories
        except Exception as e:
            logger.error(f"Error retrieving categories: {e}")
            return []

    def extract_product_count(self, label_text):
        """Extract product count from label text like 'Aceites comunes (13)'"""
        match = re.search(r'\((\d+)\)$', label_text.strip())
        return int(match.group(1)) if match else 0

    def extract_subcategories(self, category_slug):
        """
        Extract all subcategories for a given category from the expanded Sub-Categoría filter

        Returns:
            list: List of extracted subcategory dictionaries
        """
        extracted_subcategories = []

        try:
            # Find the specific Sub-Categoría filter container first
            logger.info(f"Looking for Sub-Categoría filter container in category {category_slug}")
            subcategoria_container = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,
                    "div.valtech-carrefourar-search-result-3-x-filter__container--category-3"))
            )

            # Now find all subcategory labels specifically within this container
            logger.info(f"Looking for subcategory labels within Sub-Categoría container")
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
                        'url': f'/productos/{category_slug}/{slug}',
                        'displayName': name,
                        'category': category_slug,
                        'priority': index,
                        'active': True,
                        'featured': True,  # Always true when extracted/found
                        'metadata': {
                            'productCount': product_count,
                            'productTypeCount': 0,
                            'lastUpdated': datetime.utcnow()
                        }
                    }

                    extracted_subcategories.append(subcategory)

                except Exception as e:
                    logger.warning(f"Error processing subcategory label {index}: {e}")
                    continue

            logger.info(f"Extracted {len(extracted_subcategories)} subcategories for category {category_slug}")

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

    def process_subcategories_for_category(self, category):
        """
        Complete processing for a single category: extract, insert/update, and handle removals
        """
        category_slug = category.get('slug')
        if not category_slug:
            logger.error("Category without slug found, skipping")
            return

        logger.info(f"Processing subcategories for category: {category_slug}")

        # Step 3.2a: Get existing subcategories before processing
        if self.db is None:
            # Test mode - simulate existing subcategories
            existing_slugs = set()
            logger.info(f"TEST MODE: Simulating existing subcategories check for {category_slug}")
        else:
            try:
                existing_subcategories = list(self.db.subcategories.find(
                    {"category": category_slug, "active": True},
                    {"slug": 1, "_id": 0}
                ))
                existing_slugs = set(s['slug'] for s in existing_subcategories)
            except Exception as e:
                logger.error(f"Error getting existing subcategories for {category_slug}: {e}")
                existing_slugs = set()

        # Step 3.1 & 3.2b: Extract subcategories and process each one
        extracted_subcategories = self.extract_subcategories(category_slug)

        if self.db is None:
            # Test mode - simulate database operations
            added_count = len(extracted_subcategories)
            updated_count = 0
            removed_count = 0
            logger.info(f"TEST MODE: Would process {added_count} subcategories for {category_slug}")
        else:
            added_count = 0
            updated_count = 0

            for subcategory in extracted_subcategories:
                try:
                    result = self.db.subcategories.update_one(
                        {"slug": subcategory['slug'], "category": category_slug},
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
                    result = self.db.subcategories.update_many(
                        {"slug": {"$in": removed_slugs}, "category": category_slug},
                        {"$set": {
                            "featured": False,
                            "metadata.lastUpdated": datetime.utcnow()
                        }}
                    )
                    removed_count = result.modified_count
                except Exception as e:
                    logger.error(f"Error marking removed subcategories for {category_slug}: {e}")

        # Consolidated logging
        logger.info(f"Category {category_slug}: {added_count} added, {updated_count} updated, {removed_count} removed subcategories")

        # Step 3.3: Update category metadata
        if self.db is None:
            logger.info(f"TEST MODE: Would update category metadata for {category_slug}")
        else:
            try:
                total_subcategories = len(extracted_subcategories)
                self.db.categories.update_one(
                    {"slug": category_slug},
                    {"$set": {
                        "metadata.subcategoryCount": total_subcategories,
                        "metadata.lastUpdated": datetime.utcnow()
                    }}
                )
            except Exception as e:
                logger.error(f"Error updating category metadata for {category_slug}: {e}")

    def expand_subcategoria_filter(self, category_url, category_slug):
        """
        Navigate to category URL and expand Sub-Categoría filter by clicking 'Ver más'
        """
        try:
            logger.info(f"Navigating to category: {category_url}")

            # Navigate to category page
            self.driver.get(category_url)

            # Wait for page to load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "valtech-carrefourar-search-result-3-x-filter"))
            )

            # Additional wait for dynamic content
            time.sleep(3)

            # Find Sub-Categoría filter container
            subcategoria_container = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,
                    "div.valtech-carrefourar-search-result-3-x-filter__container--category-3"))
            )

            logger.info("Found Sub-Categoría filter container")

            # Try to expand the filter if needed
            try:
                # Look for "Ver más" button
                ver_mas_button = subcategoria_container.find_element(
                    By.CSS_SELECTOR,
                    "button.valtech-carrefourar-search-result-3-x-seeMoreButton"
                )

                # Scroll to make button visible and ensure it's in viewport
                self.driver.execute_script("""
                    arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});
                    arguments[0].focus();
                """, ver_mas_button)
                time.sleep(2)

                # Try JavaScript click first (more reliable)
                try:
                    self.driver.execute_script("arguments[0].click();", ver_mas_button)
                    logger.info("Clicked 'Ver más' button using JavaScript")
                except Exception:
                    # Fallback to regular click
                    ver_mas_button.click()
                    logger.info("Clicked 'Ver más' button using Selenium click")

                # Wait for expansion to complete
                time.sleep(4)

            except NoSuchElementException:
                logger.info("Sub-Categoría filter appears to be already expanded or no 'Ver más' button found")

            # Process subcategories
            self.process_subcategories_for_category({"slug": category_slug})

        except TimeoutException:
            logger.error(f"Timeout waiting for elements on {category_url}")
        except ElementClickInterceptedException:
            logger.error(f"Click intercepted on {category_url}")
        except Exception as e:
            logger.error(f"Error processing {category_url}: {e}")

    def run_scraping(self):
        """Main scraping function"""
        logger.info("Starting Carrefour subcategories scraping (Level 3)")

        # Get categories from database
        categories = self.get_categories_from_db()

        if not categories:
            logger.error("No categories found in database")
            return

        # Process each category
        for category in categories:
            category_slug = category.get('slug')
            if category_slug:
                # Generate URL if not present
                category_url = category.get('url') or f"https://www.carrefour.com.ar/{category_slug}"

                self.expand_subcategoria_filter(category_url, category_slug)

                # Respectful delay between categories
                time.sleep(2)

        logger.info("Completed subcategories scraping for all categories")

    def close(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()
            logger.info("Browser closed")
        if hasattr(self, 'db') and self.db:
            self.db.client.close()
            logger.info("MongoDB connection closed")

def main():
    """Main entry point"""
    scraper = None
    try:
        # Initialize scraper (headless=False for visual verification)
        scraper = CarrefourSubcategoriesScraper(headless=False)

        # Run scraping
        scraper.run_scraping()

    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        if scraper:
            scraper.close()

if __name__ == "__main__":
    main()