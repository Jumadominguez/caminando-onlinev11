import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def extract_outerhtml(url, output_dir, page_name):
    """
    Extrae el outerHTML completo de una página web usando Selenium con Chrome.

    Args:
        url (str): URL de la página a scrapear.
        output_dir (str): Directorio donde guardar el archivo HTML.
        page_name (str): Nombre de la página para el archivo (e.g., 'home').
    """
    # Configurar opciones de Chrome
    options = Options()
    options.add_argument("--headless")  # Ejecutar en modo headless
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    # Inicializar el driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # Navegar a la URL
        driver.get(url)
        time.sleep(5)  # Esperar a que la página cargue completamente

        # Extraer outerHTML
        outer_html = driver.execute_script("return document.documentElement.outerHTML;")

        # Generar timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{page_name}_{timestamp}.html"
        filepath = os.path.join(output_dir, filename)

        # Guardar en archivo
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(outer_html)

        print(f"OuterHTML extraído y guardado en: {filepath}")

    except Exception as e:
        print(f"Error al extraer outerHTML de {url}: {e}")

    finally:
        driver.quit()

if __name__ == "__main__":
    # URLs clave de Jumbo
    urls = {
        "home": "https://www.jumbo.com.ar/",
        # Agregar más URLs según sea necesario, e.g., categorías
    }

    # Directorio de salida
    output_dir = os.path.dirname(os.path.abspath(__file__))  # Misma carpeta que el script

    # Extraer outerHTML para cada URL
    for page_name, url in urls.items():
        extract_outerhtml(url, output_dir, page_name)