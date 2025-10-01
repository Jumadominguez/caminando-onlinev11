import os
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# Function to check URL load time in headless browser
def check_url_load(url):
    # Configure Firefox options for headless mode
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # Specify GeckoDriver path
    service = Service(executable_path=r"D:\dev\caminando-onlinev11\drivers\geckodriver.exe")
    
    # Start driver
    driver = webdriver.Firefox(service=service, options=options)
    driver.set_window_size(1920, 1080)  # Set larger window size for headless
    
    try:
        start_time = time.time()
        driver.get(url)
        
        # Wait for DOM to be ready
        WebDriverWait(driver, 30).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        
        # Wait for the filter container to be present
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "valtech-carrefourar-search-result-3-x-filterContent"))
        )
        
        # Find the container for "Tipo De Producto" by checking for inputs with 'tipo-de-producto' in id
        container = driver.find_element(By.XPATH, "//div[contains(@class, 'valtech-carrefourar-search-result-3-x-filterContent') and .//input[contains(@id, 'tipo-de-producto')]]")
        
        # Try to find and click the "Ver más" button
        try:
            see_more_button = container.find_element(By.CLASS_NAME, "valtech-carrefourar-search-result-3-x-seeMoreButton")
            # Scroll to the button to make it visible
            driver.execute_script("arguments[0].scrollIntoView();", see_more_button)
            time.sleep(1)  # Wait for scroll
            # Use JavaScript click
            driver.execute_script("arguments[0].click();", see_more_button)
            # Wait for additional items to load
            time.sleep(2)
            print("Botón 'Ver más' clickeado.")
        except Exception as e:
            print(f"Botón 'Ver más' no encontrado o no clickeable: {str(e)}")
        
        # Count the filter items inside
        filter_items = container.find_elements(By.CLASS_NAME, "valtech-carrefourar-search-result-3-x-filterItem")
        count = len(filter_items)
        print(f"Encontrados {count} elementos en el contenedor de filtros.")
        
        # Print the list of elements
        print("Lista de elementos:")
        for i, item in enumerate(filter_items, 1):
            try:
                text = item.get_attribute("textContent").strip()
                print(f"{i}. {text}")
            except Exception as e:
                print(f"{i}. Error obteniendo texto: {str(e)}")
        
        end_time = time.time()
        elapsed = end_time - start_time
        print(f"URL {url} cargada correctamente en {elapsed:.2f} segundos")

    except Exception as e:
        print(f"Error cargando URL {url}: {str(e)}")
    
    finally:
        driver.quit()

# Hardcoded URL for testing
url = "https://www.carrefour.com.ar/Electro-y-tecnologia?initialMap=c&initialQuery=Electro-y-tecnologia&map=category-1,category-3&query=/Electro-y-tecnologia/accesorios-de-celulares&searchState"

# Process the URL
print("Verificando carga de URL en navegador headless:")
check_url_load(url)