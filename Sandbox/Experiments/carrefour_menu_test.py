#!/usr/bin/env python3
"""
Carrefour Categories Scraper
Extract categories from menu and save to MongoDB
"""

import os
import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pymongo import MongoClient
from dotenv import load_dotenv

def generate_slug(name):
    """Generate slug from category name with proper Spanish character handling"""
    # Convert to lowercase
    slug = name.lower()
    # Replace Spanish characters
    slug = slug.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
    slug = slug.replace('ñ', 'n').replace('ü', 'u')
    # Replace spaces and special characters with hyphens
    slug = slug.replace(' ', '-').replace('y', '-').replace('&', '-').replace('/', '-')
    # Remove any remaining non-alphanumeric characters except hyphens
    import re
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    # Remove multiple consecutive hyphens and leading/trailing hyphens
    slug = re.sub(r'-+', '-', slug).strip('-')
    return slug

def connect_mongodb():
    """Connect to MongoDB Atlas"""
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'backend', '.env'))

    mongo_uri = os.getenv('MONGO_CARREFOUR_URI')
    if not mongo_uri:
        print("Error: MONGO_CARREFOUR_URI not found in environment variables")
        return None

    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        db = client.carrefour
        print("Connected to MongoDB Atlas successfully")
        return db
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        return None

def save_categories_to_db(db, categories):
    """Save categories to MongoDB"""
    if db is None:
        print("No database connection available")
        return 0

    collection = db['categories']
    saved_count = 0

    for category in categories:
        try:
            # Use slug as unique identifier (matches the _id field)
            result = collection.update_one(
                {'_id': category['_id']},
                {'$set': category},
                upsert=True
            )
            if result.upserted_id or result.modified_count > 0:
                saved_count += 1
        except Exception as e:
            print(f"Error saving category {category.get('name', 'Unknown')}: {e}")

    return saved_count

def main():
    # Configure Edge WebDriver
    options = Options()
    # No headless - visible browser
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # Reduce logging noise
    options.add_argument("--log-level=3")
    options.add_argument("--disable-logging")
    options.add_argument("--silent")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    driver = webdriver.Edge(options=options)
    driver.maximize_window()

    # Connect to MongoDB
    db = connect_mongodb()

    try:
        # Navigate to Carrefour homepage
        print("Navigating to Carrefour homepage...")
        driver.get("https://www.carrefour.com.ar")

        # Wait for page to load
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "title")))

        print("Page loaded. Waiting...")
        time.sleep(1)

        # Remove modal that blocks clicks
        driver.execute_script("""
            var modal = document.querySelector('.dy-modal-wrapper');
            if (modal) {
                modal.remove();
                console.log('Modal removed');
            }
            // Also try to remove any overlay
            var overlays = document.querySelectorAll('[class*="overlay"], [class*="modal"]');
            overlays.forEach(function(overlay) {
                if (overlay !== modal) overlay.remove();
            });
        """)

        # Find the categories menu button
        categories_button = driver.find_element(By.CSS_SELECTOR, 'button[data-id="mega-menu-trigger-button"]')

        # Use JavaScript click instead of Selenium click
        driver.execute_script("arguments[0].click();", categories_button)

        print("Menu opened! Extracting categories...")

        # Wait for menu to fully load
        time.sleep(2)

        # Extract categories from the opened menu
        categories_data = driver.execute_script("""
            const menuContainer = document.querySelector('.carrefourar-mega-menu-0-x-menuContainer');
            if (!menuContainer) return [];

            const categoryLinks = menuContainer.querySelectorAll('li.carrefourar-mega-menu-0-x-menuItem a.carrefourar-mega-menu-0-x-styledLink');
            const categories = [];

            function generateSlug(name) {
                let slug = name.toLowerCase();
                // Replace Spanish characters
                slug = slug.replace(/á/g, 'a').replace(/é/g, 'e').replace(/í/g, 'i').replace(/ó/g, 'o').replace(/ú/g, 'u');
                slug = slug.replace(/ñ/g, 'n').replace(/ü/g, 'u');
                // Replace spaces and special characters with hyphens
                slug = slug.replace(/\\s+/g, '-').replace(/y/g, '-').replace(/&/g, '-').replace(/\\//g, '-');
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
                        _id: slug,  // Use slug as unique ID (matches model requirement)
                        name: name, // Category name (required, unique)
                        displayName: name, // Display name (same as name for now)
                        slug: slug, // URL-friendly slug (unique)
                        subcategories: [], // Empty array by default
                        active: true, // Default to active
                        featured: false, // Default to not featured
                        metadata: {
                            productCount: 0, // Default to 0
                            subcategoryCount: 0, // Default to 0
                            lastUpdated: null // Will be set when products are updated
                        }
                        // createdAt and updatedAt will be set automatically by Mongoose
                    });
                }
            });

            return categories;
        """)

        # Filter out categories to ignore
        categories_to_ignore = ["bazar y textil", "indumentaria", "ofertas", "destacados"]
        filtered_categories = [
            cat for cat in categories_data
            if cat['name'].lower() not in categories_to_ignore
        ]

        print(f"Extracted {len(filtered_categories)} categories (filtered from {len(categories_data)}):")
        for i, cat in enumerate(filtered_categories[:5], 1):  # Show first 5
            print(f"{i}. {cat['name']} -> {cat['slug']}")

        if len(filtered_categories) > 5:
            print(f"... and {len(filtered_categories) - 5} more categories")

        # Save to database
        if db is not None and filtered_categories:
            saved_count = save_categories_to_db(db, filtered_categories)
            print(f"Saved {saved_count} categories to database")
        else:
            print("No database connection or no categories to save")

        print("Test completed successfully!")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        driver.quit()
        if db is not None:
            print("Database connection closed")

if __name__ == "__main__":
    main()