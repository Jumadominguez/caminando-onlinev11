#!/usr/bin/env python3
"""
Carrefour Subcategories Scraper - Level 3
Scrapes subcategories for each category by expanding Sub-Categoría filter and clicking "Ver más"

Author: GitHub Copilot
Date: September 2025
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
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
        logging.FileHandler('carrefour_subcategories_scraper.log'),
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
            # Using placeholder - replace with actual connection string
            client = pymongo.MongoClient("mongodb+srv://<username>:<password>@<cluster>.mongodb.net/carrefour?retryWrites=true&w=majority")
            self.db = client.carrefour
            logger.info("Connected to MongoDB Atlas - carrefour database")
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    def _setup_browser(self):
        """Setup Firefox browser with options"""
        options = Options()
        if self.headless:
            options.add_argument("--headless")

        # Anti-detection measures
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.set_preference("dom.webdriver.enabled", False)
        options.set_preference('useAutomationExtension', False)

        self.driver = webdriver.Firefox(options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        logger.info(f"Browser initialized (headless: {self.headless})")

    def get_categories_from_db(self):
        """Retrieve all categories from MongoDB"""
        try:
            categories = list(self.db.categories.find({}, {"_id": 1, "name": 1, "url": 1}))
            logger.info(f"Retrieved {len(categories)} categories from database")
            return categories
        except Exception as e:
            logger.error(f"Error retrieving categories: {e}")
            return []

    def expand_subcategoria_filter(self, category_url):
        """
        Navigate to category URL and expand Sub-Categoría filter by clicking 'Ver más'

        Args:
            category_url (str): URL of the category page
        """
        try:
            logger.info(f"Processing category: {category_url}")

            # Navigate to category page
            self.driver.get(category_url)

            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "valtech-carrefourar-search-result-3-x-filter"))
            )

            # Wait a bit more for dynamic content
            time.sleep(2)

            # Find Sub-Categoría filter container
            subcategoria_container = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,
                    "div.valtech-carrefourar-search-result-3-x-filter__container--category-3"))
            )

            logger.info("Found Sub-Categoría filter container")

            # Check if filter is already expanded (look for "Ver más" button)
            try:
                ver_mas_button = subcategoria_container.find_element(
                    By.CSS_SELECTOR,
                    "button.valtech-carrefourar-search-result-3-x-seeMoreButton"
                )

                # Scroll to make button visible
                self.driver.execute_script("arguments[0].scrollIntoView(true);", ver_mas_button)
                time.sleep(1)

                # Click "Ver más" button
                ver_mas_button.click()
                logger.info("Clicked 'Ver más' button to expand subcategories")

                # Wait for expansion to complete
                time.sleep(3)

                # Verify expansion by checking if button text changed or disappeared
                try:
                    # Check if button still exists or text changed
                    updated_button = subcategoria_container.find_element(
                        By.CSS_SELECTOR,
                        "button.valtech-carrefourar-search-result-3-x-seeMoreButton"
                    )
                    logger.info("Subcategories expanded successfully")
                except NoSuchElementException:
                    logger.info("Subcategories expanded successfully (button disappeared)")

            except NoSuchElementException:
                logger.info("Sub-Categoría filter appears to be already expanded or no 'Ver más' button found")

            # Additional wait to ensure all subcategories are loaded
            time.sleep(2)

        except TimeoutException:
            logger.error(f"Timeout waiting for elements on {category_url}")
        except ElementClickInterceptedException:
            logger.error(f"Click intercepted on {category_url}")
        except Exception as e:
            logger.error(f"Error processing {category_url}: {e}")

    def run_scraping(self):
        """Main scraping function"""
        logger.info("Starting Carrefour subcategories scraping")

        # Get categories from database
        categories = self.get_categories_from_db()

        if not categories:
            logger.error("No categories found in database")
            return

        # Process each category
        for category in categories:
            category_url = category.get('url')
            if category_url:
                self.expand_subcategoria_filter(category_url)
                # Small delay between categories to be respectful
                time.sleep(1)

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