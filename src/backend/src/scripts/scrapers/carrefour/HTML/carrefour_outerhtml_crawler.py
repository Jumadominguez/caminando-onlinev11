import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By

def extract_outerhtml(driver, url, output_dir, page_name):
    """
    Extrae el outerHTML completo de una página web usando Selenium.

    Args:
        driver: Instancia de WebDriver.
        url (str): URL de la página a scrapear.
        output_dir (str): Directorio donde guardar el archivo HTML.
        page_name (str): Nombre de la página para el archivo.
    """
    try:
        driver.get(url)
        time.sleep(5)  # Esperar a que la página cargue

        outer_html = driver.execute_script("return document.documentElement.outerHTML;")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{page_name}_{timestamp}.html"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(outer_html)

        print(f"OuterHTML extraído: {filepath}")
        return filepath

    except Exception as e:
        print(f"Error extrayendo {url}: {e}")
        return None

def find_links(driver, base_url, patterns):
    """
    Encuentra enlaces relevantes en la página actual.

    Args:
        driver: Instancia de WebDriver.
        base_url (str): URL base para filtrar enlaces internos.
        patterns (list): Lista de patrones para href (e.g., '/categoria/').

    Returns:
        list: Lista de URLs únicas que coinciden con patrones.
    """
    links = set()
    try:
        elements = driver.find_elements(By.TAG_NAME, 'a')
        for elem in elements:
            href = elem.get_attribute('href')
            if href and href.startswith(base_url):
                for pattern in patterns:
                    if pattern in href:
                        links.add(href)
                        break
    except Exception as e:
        print(f"Error encontrando enlaces: {e}")
    return list(links)[:5]  # Limitar a 5 enlaces por tipo

def crawl_carrefour(output_dir):
    """
    Crawling básico de Carrefour para extraer outerHTML de páginas clave.
    """
    base_url = "https://www.carrefour.com.ar"

    # Configurar Edge
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    driver = webdriver.Edge(options=options)

    try:
        # URLs específicas a extraer
        specific_urls = {
            "home": f"{base_url}/",
            "categoria_almacen": f"{base_url}/Almacen",
            "producto_ejemplo": f"{base_url}/aceite-de-girasol-carrefour-classic-alto-omega-pet-900-cc-699030-699030/p",
            "ofertas": f"{base_url}/promociones"
        }

        # Extraer outerHTML de URLs específicas
        for name, url in specific_urls.items():
            extract_outerhtml(driver, url, output_dir, name)

    finally:
        driver.quit()

if __name__ == "__main__":
    output_dir = os.path.dirname(os.path.abspath(__file__))  # Carpeta HTML donde está el script
    crawl_carrefour(output_dir)