import os
import time
import shutil
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By

def clean_vault(vault_dir, page_name):
    """
    Mantiene solo las 2 versiones más recientes de archivos para un page_name en vault.

    Args:
        vault_dir (str): Directorio vault.
        page_name (str): Nombre de la página (e.g., 'home').
    """
    prefix = f"{page_name}_"
    files = [f for f in os.listdir(vault_dir) if f.startswith(prefix) and f.endswith('.html')]
    
    if len(files) > 2:
        # Ordenar por timestamp (YYYYMMDD_HHMMSS en el nombre)
        files.sort(key=lambda x: x[len(prefix):-5], reverse=True)  # -5 para quitar .html
        # Mantener los 2 primeros (más recientes), eliminar el resto
        for old_file in files[2:]:
            os.remove(os.path.join(vault_dir, old_file))
            print(f"Eliminado archivo antiguo del vault: {old_file}")

def extract_outerhtml(driver, url, output_dir, vault_dir, page_name):
    """
    Extrae el outerHTML completo de una página web usando Selenium.

    Args:
        driver: Instancia de WebDriver.
        url (str): URL de la página a scrapear.
        output_dir (str): Directorio donde guardar el archivo HTML.
        vault_dir (str): Directorio del vault para archivos antiguos.
        page_name (str): Nombre de la página para el archivo.
    """
    try:
        driver.get(url)
        time.sleep(5)  # Esperar a que la página cargue

        outer_html = driver.execute_script("return document.documentElement.outerHTML;")

        # Mover archivos existentes al vault
        if os.path.exists(output_dir):
            for file in os.listdir(output_dir):
                if file.startswith(f"{page_name}_") and file.endswith(".html"):
                    src = os.path.join(output_dir, file)
                    dst = os.path.join(vault_dir, file)
                    shutil.move(src, dst)
                    print(f"Movido al vault: {file}")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{page_name}_{timestamp}.html"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(outer_html)

        print(f"OuterHTML extraído: {filepath}")

        # Limpiar vault manteniendo solo 2 versiones
        clean_vault(vault_dir, page_name)

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
    vault_dir = os.path.join(output_dir, "vault")

    # Asegurar que el vault existe
    os.makedirs(vault_dir, exist_ok=True)

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
            "producto_ejemplo": f"{base_url}/aceite-de-girasol-carrefour-classic-alto-omega-pet-900-cc-699030-699030/p"
        }

        # Extraer outerHTML de URLs específicas
        for name, url in specific_urls.items():
            extract_outerhtml(driver, url, output_dir, vault_dir, name)

    finally:
        driver.quit()

if __name__ == "__main__":
    output_dir = os.path.dirname(os.path.abspath(__file__))  # Carpeta HTML donde está el script
    crawl_carrefour(output_dir)