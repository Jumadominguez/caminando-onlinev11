#!/usr/bin/env python3
"""
Jumbo Categories Scraper
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
from selenium.webdriver.common.action_chains import ActionChains
from pymongo import MongoClient
from dotenv import load_dotenv

try:
    from colorama import init, Fore, Back, Style
    COLORAMA_AVAILABLE = True
    init(autoreset=True)
except ImportError:
    COLORAMA_AVAILABLE = False

# Configure logging (simple, without colors)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Colored print functions
def print_success(message):
    if COLORAMA_AVAILABLE:
        print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")
    else:
        print(f"[SUCCESS] {message}")

def print_warning(message):
    if COLORAMA_AVAILABLE:
        print(f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")
    else:
        print(f"[WARNING] {message}")

def print_error(message):
    if COLORAMA_AVAILABLE:
        print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")
    else:
        print(f"[ERROR] {message}")

def print_info(message):
    if COLORAMA_AVAILABLE:
        print(f"{Fore.CYAN}ℹ {message}{Style.RESET_ALL}")
    else:
        print(f"[INFO] {message}")

# Utility functions for better visualization
def print_separator(char='=', length=60):
    """Print a visual separator line"""
    if COLORAMA_AVAILABLE:
        print(f"{Fore.BLUE}{char * length}{Style.RESET_ALL}")
    else:
        print(f"{char * length}")

def print_header(text, emoji=''):
    """Print a formatted header"""
    print_separator()
    if COLORAMA_AVAILABLE:
        print(f"{Fore.GREEN}{emoji} {text.upper()} {emoji}{Style.RESET_ALL}")
    else:
        print(f"{emoji} {text.upper()} {emoji}")
    print_separator()

def generate_slug(name):
    """Generate slug from category name with proper Spanish character handling"""
    # Convert to lowercase
    slug = name.lower()
    # Replace Spanish characters
    slug = slug.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
    slug = slug.replace('ñ', 'n').replace('ü', 'u')
    # Replace " y " (word) with "-" but keep "y" in other contexts
    slug = slug.replace(' y ', '-').replace(' & ', '-').replace(' / ', '-')
    # Replace remaining spaces with hyphens
    slug = slug.replace(' ', '-')
    # Remove any remaining non-alphanumeric characters except hyphens
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    # Remove multiple consecutive hyphens and leading/trailing hyphens
    slug = re.sub(r'-+', '-', slug).strip('-')
    return slug

def connect_mongodb():
    """Connect to MongoDB Atlas"""
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '.env'))

    mongo_uri = os.getenv('MONGO_JUMBO_URI')
    if not mongo_uri:
        print_error("MONGO_JUMBO_URI not found in environment variables")
        return None

    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        db = client.jumbo
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
    print_header("Jumbo Categories Scraper", "🛒")
    print_info("Starting Jumbo categories extraction from menu")
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
        # Navigate to Jumbo homepage
        print_info("Navigating to Jumbo homepage...")
        driver.get("https://www.jumbo.com.ar")

        # Wait for page to load
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "title")))

        print_info("Page loaded. Waiting...")
        time.sleep(1)

        # Remove modal that blocks clicks (Jumbo specific)
        driver.execute_script("""
            // Try to remove common modal/overlay elements for Jumbo
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

        # Find the categories menu trigger element (Jumbo specific - uses hover)
        # Based on HTML analysis, Jumbo uses VTEX menu system with hover activation
        categories_trigger = driver.find_element(By.CSS_SELECTOR, 'li.vtex-menu-2-x-menuItem--header-category .vtex-menu-2-x-styledLink')

        # Use ActionChains to perform hover action
        actions = ActionChains(driver)
        actions.move_to_element(categories_trigger).perform()

        print_info("Menu hover activated! Waiting for menu to appear...")

        # Wait for menu to fully load after hover
        time.sleep(3)

        # Extract categories from the hovered menu (Jumbo specific selectors)
        categories_data = driver.execute_script(r"""
            // Jumbo specific menu container selectors after hover
            const menuSelectors = [
                '.vtex-menu-2-x-menuContainer--category-menu',
                '[class*="menu"] [class*="container"]'
            ];

            let menuContainer = null;
            for (const selector of menuSelectors) {
                menuContainer = document.querySelector(selector);
                if (menuContainer) {
                    console.log(`Found menu container with selector: ${selector}`);
                    break;
                }
            }

            if (!menuContainer) {
                console.log('Menu container not found, trying direct category link search');
                // Fallback: search for category links directly in the page
                const allCategoryLinks = document.querySelectorAll('a[href*="/"][class*="menu-item-secondary"]');
                console.log(`Found ${allCategoryLinks.length} potential category links`);
                menuContainer = { querySelectorAll: () => allCategoryLinks };
            }

            // Jumbo specific category link selectors
            const categoryLinks = menuContainer.querySelectorAll('li.vtex-menu-2-x-menuItem--menu-item-secondary a.vtex-menu-2-x-styledLink');

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
                const slug = generateSlug(name);

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

        # Filter out categories to ignore (Jumbo specific)
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

        print_success(f"Extracted {len(filtered_categories)} categories from menu")

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
        print_separator()
        if db is not None:
            print("Database connection closed")

if __name__ == "__main__":
    main()