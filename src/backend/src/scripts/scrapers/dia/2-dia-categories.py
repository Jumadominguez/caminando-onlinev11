#!/usr/bin/env python3
"""
Dia Categories Scraper
Extract categories from menu and save to MongoDB
"""

import os
import json
import time
import logging
import re
from datetime import datetime, UTC
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pymongo import MongoClient
from dotenv import load_dotenv

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
file_handler = logging.FileHandler('logs/2-dia-categories.log', mode='w')
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

def generate_slug(url):
    """Extract slug from URL"""
    if not url:
        return ""
    # Split URL by '/' and get the last part
    url_parts = url.split('/')
    slug = url_parts[-1] or url_parts[-2] or ""
    # Remove query parameters and fragments
    slug = slug.split('?')[0].split('#')[0]
    return slug

def connect_mongodb():
    """Connect to MongoDB Atlas"""
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '.env'))

    mongo_uri = os.getenv('MONGO_DIA_URI')
    if not mongo_uri:
        print_error("MONGO_DIA_URI not found in environment variables")
        return None

    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        db = client.dia
        print_success("Connected to MongoDB Atlas successfully")
        return db
    except Exception as e:
        print_error(f"Failed to connect to MongoDB: {e}")
        return None

def save_categories_to_db(db, categories):
    """Save categories to MongoDB with removal tracking"""
    if db is None:
        print_error("No database connection available")
        return 0, 0, 0

    collection = db['categories']
    added_count = 0
    updated_count = 0
    removed_count = 0

    # Get current slugs from website
    current_slugs = {cat['slug'] for cat in categories}

    # Get existing categories that were featured
    existing_featured = list(collection.find({'featured': True}, {'slug': 1}))
    existing_featured_slugs = {cat['slug'] for cat in existing_featured}

    # Mark all categories as not featured initially
    collection.update_many({}, {'$set': {'featured': False}})

    # Process current categories from website
    for category in categories:
        try:
            # Use slug as unique identifier for upsert
            result = collection.update_one(
                {'slug': category['slug']},
                {'$set': category},
                upsert=True
            )
            if result.upserted_id:
                added_count += 1
            elif result.modified_count > 0:
                updated_count += 1
        except Exception as e:
            print_error(f"Error saving category {category.get('name', 'Unknown')}: {e}")

    # Count removed categories (those that were featured but not in current website)
    removed_slugs = existing_featured_slugs - current_slugs
    removed_count = len(removed_slugs)

    return added_count, updated_count, removed_count

def main():
    print_header("Dia Categories Scraper", "🛒")
    print_info("Starting Dia categories extraction from menu")
    # Configure Edge WebDriver
    options = Options()
    # Headless mode for production/scaling
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # Additional headless options
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-plugins")
    options.add_argument("--disable-images")  # Speed up loading
    # Reduce logging noise
    options.add_argument("--log-level=3")
    options.add_argument("--disable-logging")
    options.add_argument("--silent")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    # Set window size for headless
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Edge(options=options)
    # No need to maximize window in headless mode

    # Connect to MongoDB
    db = connect_mongodb()

    try:
        # Navigate to Dia homepage
        print_action("Navigating to Dia homepage...")
        driver.get("https://diaonline.supermercadosdia.com.ar")

        # Wait for page to load
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "title")))

        print_info("Page loaded. Waiting...")
        time.sleep(1)

        # Remove modal that blocks clicks (Dia specific)
        driver.execute_script("""
            // Try to remove common modal/overlay elements for Dia
            var modals = document.querySelectorAll('[class*="modal"], [class*="overlay"], .dy-modal-wrapper');
            modals.forEach(function(modal) {
                modal.remove();
                console.log('Modal removed');
            });

            // Also try to remove any popup or banner
            var popups = document.querySelectorAll('[class*="popup"], [class*="banner"]');
            popups.forEach(function(popup) {
                if (popup.style.display !== 'none') {
                    popup.style.display = 'none';
                }
            });
        """)

        # Find the categories menu button (Dia specific selector)
        # Based on HTML analysis, Dia uses VTEX menu system with custom mega menu
        categories_button = driver.find_element(By.CSS_SELECTOR, '.diaio-custom-mega-menu-0-x-custom-mega-menu-trigger__button')

        # Use JavaScript click instead of Selenium click
        driver.execute_script("arguments[0].click();", categories_button)

        print_action("Menu opened! Extracting categories...")

        # Wait for menu to fully load
        time.sleep(2)

        # Extract categories from the opened menu (Dia specific selectors)
        categories_data = driver.execute_script(r"""
            // Dia specific menu container selector
            const menuContainer = document.querySelector('.diaio-custom-mega-menu-0-x-category-list__container');

            if (!menuContainer) {
                console.log('Menu container not found');
                return [];
            }

            // Dia specific category link selectors
            const categoryLinks = menuContainer.querySelectorAll('a.diaio-custom-mega-menu-0-x-category-list-item__container.diaio-custom-mega-menu-0-x-category-list-item__container-level-1');

            const categories = [];

            function generateSlug(name) {
                let slug = name.toLowerCase();
                // Replace Spanish characters
                slug = slug.replace(/á/g, 'a').replace(/é/g, 'e').replace(/í/g, 'i').replace(/ó/g, 'o').replace(/ú/g, 'u');
                slug = slug.replace(/ñ/g, 'n').replace(/ü/g, 'u');
                // Replace " y " (word) with "-" but keep "y" in other contexts
                slug = slug.replace(/ y /g, '-').replace(/ & /g, '-').replace(/ \/ /g, '-');
                // Replace remaining spaces with hyphens
                slug = slug.replace(/\s+/g, '-');
                // Remove any remaining non-alphanumeric characters except hyphens
                slug = slug.replace(/[^a-z0-9-]/g, '');
                // Remove multiple consecutive hyphens and leading/trailing hyphens
                slug = slug.replace(/-+/g, '-').replace(/^-+|-+$/g, '');
                return slug;
            }

            categoryLinks.forEach(link => {
                const name = link.textContent.trim();
                const url = link.href;
                
                // Extract slug from URL
                const urlParts = url.split('/');
                const slugFromUrl = urlParts[urlParts.length - 1] || urlParts[urlParts.length - 2] || '';
                // Clean slug (remove query parameters and fragments)
                const slug = slugFromUrl.split('?')[0].split('#')[0];

                if (name && url && slug) {
                    categories.push({
                        name: name,
                        displayName: name,
                        slug: slug,
                        url: url,
                        subcategories: [],
                        active: true,
                        featured: true,
                        metadata: {
                            productCount: 0,
                            subcategoryCount: 0,
                            lastUpdated: null
                        }
                    });
                }
            });

            return categories;
        """)

        # Filter out categories to ignore (Dia specific)
        categories_to_ignore = ["ofertas", "destacados", "promociones", "inicio", "home", "contacto", "ayuda"]
        filtered_categories = [
            cat for cat in categories_data
            if cat['name'].lower() not in categories_to_ignore
        ]

        # Add timestamps to categories
        current_time = datetime.now(UTC)
        for category in filtered_categories:
            category['createdAt'] = current_time
            category['updatedAt'] = current_time

        print_info(f"Extracted {len(filtered_categories)} categories from menu")

        # Save to database
        if db is not None and filtered_categories:
            added_count, updated_count, removed_count = save_categories_to_db(db, filtered_categories)
            print_success(f"Categories processed: {added_count} added, {updated_count} updated, {removed_count} removed")
        else:
            print_warning("No database connection or no categories to save")

        print_success("Test completed successfully!")

    except Exception as e:
        print_error(f"Error: {e}")

    finally:
        driver.quit()
        if db is not None:
            print_info("Database connection closed")

    print_separator()

if __name__ == "__main__":
    main()