#!/usr/bin/env python3
"""
Script de prueba para comparar productos totales en categorías vs productos registrados
Lee categorías de MongoDB, visita cada URL, extrae total de productos y compara con DB
Genera reporte en Sandbox/temps/
"""

import logging
import time
import random
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pymongo import MongoClient
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Anti-detection constants
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'
]

def random_delay():
    time.sleep(random.uniform(1.0, 2.0))

def setup_driver():
    firefox_options = Options()
    firefox_options.add_argument("--headless")
    firefox_options.add_argument("--no-sandbox")
    firefox_options.add_argument("--disable-dev-shm-usage")
    firefox_options.add_argument("--window-size=1920,1080")
    firefox_options.add_argument("--disable-gpu")
    firefox_options.add_argument("--disable-extensions")

    user_agent = random.choice(USER_AGENTS)
    firefox_options.set_preference("general.useragent.override", user_agent)

    geckodriver_path = r"d:\dev\caminando-onlinev10\geckodriver_temp\geckodriver.exe"
    service = Service(geckodriver_path)
    driver = webdriver.Firefox(service=service, options=firefox_options)

    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    return driver

def get_total_products(driver):
    """Get total number of products from the page"""
    try:
        # Specific selector provided by user
        specific_selector = "div.valtech-carrefourar-search-result-3-x-totalProducts--layout span"
        
        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, specific_selector))
            )
            text = element.text.strip()
            # Extract number
            import re
            match = re.search(r'(\d+)', text.replace('.', '').replace(',', ''))
            if match:
                return int(match.group(1))
        except:
            pass

        # Fallback selectors
        selectors = [
            "span.valtech-carrefourar-search-result-0-x-totalProducts",
            "span[data-testid*='total']",
            "span:contains('productos')",
            ".search-result-info span"
        ]

        for selector in selectors:
            try:
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                text = element.text.strip()
                # Extract number from text like "X productos"
                import re
                match = re.search(r'(\d+)', text.replace('.', '').replace(',', ''))
                if match:
                    return int(match.group(1))
            except:
                continue

        return 0
    except Exception as e:
        logging.error(f"Error getting total products: {e}")
        return 0

def get_categories_from_db():
    """Get all categories from MongoDB"""
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['carrefour']
        collection = db['categories']

        categories = list(collection.find({}, {'name': 1, 'url': 1, '_id': 0}))
        client.close()

        return categories
    except Exception as e:
        logging.error(f"Error retrieving categories: {e}")
        return []

def count_products_in_db(category_name):
    """Count products in DB for a specific category"""
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['carrefour']
        collection = db['products']

        count = collection.count_documents({'category': category_name})
        client.close()

        return count
    except Exception as e:
        logging.error(f"Error counting products in DB: {e}")
        return 0

def generate_report(results):
    """Generate report file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"d:\\dev\\caminando-onlinev10\\Sandbox\\temps\\categories_products_comparison_{timestamp}.txt"

    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write("REPORTE DE COMPARACIÓN: PRODUCTOS TOTALES VS REGISTRADOS\n")
        f.write("=" * 70 + "\n")
        f.write(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        total_categories = len(results)
        total_web_products = sum(r['web_total'] for r in results)
        total_db_products = sum(r['db_count'] for r in results)
        total_difference = total_web_products - total_db_products

        f.write(f"Categorías procesadas: {total_categories}\n")
        f.write(f"Total productos en web: {total_web_products}\n")
        f.write(f"Total productos en DB: {total_db_products}\n")
        f.write(f"Diferencia total: {total_difference}\n\n")

        f.write("DETALLE POR CATEGORÍA:\n")
        f.write("-" * 70 + "\n")

        for result in results:
            f.write(f"Categoría: {result['name']}\n")
            f.write(f"  URL: {result['url']}\n")
            f.write(f"  Productos en web: {result['web_total']}\n")
            f.write(f"  Productos en DB: {result['db_count']}\n")
            f.write(f"  Diferencia: {result['web_total'] - result['db_count']}\n")
            f.write(f"  Estado: {'✅ Completo' if result['web_total'] == result['db_count'] else '⚠️ Pendiente'}\n\n")

    logging.info(f"Report generated: {report_filename}")
    print(f"\n📄 Reporte generado: {report_filename}")

    return report_filename

def main():
    logging.info("Starting categories products comparison test")

    # Get categories from DB
    categories = get_categories_from_db()
    if not categories:
        logging.error("No categories found")
        return

    logging.info(f"Found {len(categories)} categories")

    results = []

    for category in categories:
        category_name = category.get('name')
        category_url = category.get('url')

        if not category_name or not category_url:
            logging.warning(f"Skipping invalid category: {category}")
            continue

        logging.info(f"Processing category: {category_name}")

        driver = None
        try:
            driver = setup_driver()
            random_delay()

            driver.get(category_url)
            time.sleep(3)  # Wait for page load

            # Get total products from web
            web_total = get_total_products(driver)

            # Get count from DB
            db_count = count_products_in_db(category_name)

            results.append({
                'name': category_name,
                'url': category_url,
                'web_total': web_total,
                'db_count': db_count
            })

            logging.info(f"{category_name}: Web={web_total}, DB={db_count}, Diff={web_total - db_count}")

        except Exception as e:
            logging.error(f"Error processing category {category_name}: {e}")
            results.append({
                'name': category_name,
                'url': category_url,
                'web_total': 0,
                'db_count': count_products_in_db(category_name)
            })

        finally:
            if driver:
                driver.quit()

        # Delay between categories
        time.sleep(2)

    # Generate report
    generate_report(results)

    logging.info("Comparison test completed")

if __name__ == "__main__":
    main()