import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

def analyze_product_types_for_subcategories():
    # Configurar opciones de Firefox
    options = Options()
    options.headless = False  # Cambiar a True para headless si es necesario

    # Inicializar el driver
    driver = webdriver.Firefox(options=options)

    try:
        # URL de la categoría Carnes y Pescados en Carrefour
        url = "https://www.carrefour.com.ar/Carnes-y-Pescados"
        driver.get(url)

        # Esperar a que la página cargue completamente
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "valtech-carrefourar-search-result-3-x-filter__container--tipo-de-producto"))
        )

        # Verificar si el contenedor existe
        containers = driver.find_elements(By.CLASS_NAME, "valtech-carrefourar-search-result-3-x-filter__container--tipo-de-producto")
        if not containers:
            print("No se encontró el contenedor de tipos de producto.")
            return

        container = containers[0]
        print("Contenedor encontrado.")

        # Intentar cerrar cualquier modal o popup que pueda obstruir
        try:
            modal_close = driver.find_element(By.CLASS_NAME, "dy-modal-close")
            modal_close.click()
            time.sleep(1)
            print("Modal cerrado.")
        except:
            pass

        # Hacer clic en el título del filtro para expandirlo
        try:
            # Buscar el título del filtro dentro del contenedor
            filter_title = container.find_element(By.XPATH, ".//span[contains(text(), 'Tipo de producto')]")
            # Usar JavaScript para hacer clic si el clic normal falla
            driver.execute_script("arguments[0].click();", filter_title)
            print("Filtro expandido.")
            # Esperar un momento para que se carguen los elementos
            time.sleep(3)
        except Exception as e:
            print(f"No se pudo expandir el filtro: {e}")
            # Intentar hacer clic en el contenedor completo si el título no funciona
            try:
                driver.execute_script("arguments[0].click();", container)
                time.sleep(3)
                print("Filtro expandido haciendo clic en el contenedor.")
            except Exception as e2:
                print(f"No se pudo expandir el filtro con JS: {e2}")

        # Buscar y hacer clic en el botón "Ver más" para expandir completamente el filtro
        try:
            see_more_button = container.find_element(By.CLASS_NAME, "valtech-carrefourar-search-result-3-x-seeMoreButton")
            driver.execute_script("arguments[0].click();", see_more_button)
            print("Botón 'Ver más' activado.")
            # Esperar a que se carguen todos los elementos
            time.sleep(3)
        except Exception as e:
            print(f"No se encontró el botón 'Ver más' o no se pudo activar: {e}")

        # Encontrar todos los labels dentro del contenedor
        labels = container.find_elements(By.CLASS_NAME, "vtex-checkbox__label")

        # Extraer los tipos de producto
        product_types = []
        for label in labels:
            text = label.text
            # Remover el número entre paréntesis usando regex
            clean_text = re.sub(r'\s*\(\d+\)$', '', text).strip()
            if clean_text:
                product_types.append(clean_text)

        # Función para clasificar tipos de producto en sub-categorías
        def classify_product_type(product_type):
            product_type_lower = product_type.lower()

            # Aves - más específico primero
            if any(word in product_type_lower for word in ['pollo', 'gallina', 'pavo', 'ave', 'gallineta', 'suprema de pollo', 'milanesa de pollo']):
                return 'Aves'

            # Cerdos - expandir con más productos específicos
            if any(word in product_type_lower for word in ['cerdo', 'lechón', 'chancho', 'cochinillo', 'lomo de cerdo', 'matambre de cerdo', 'paleta de cerdo', 'pechito de cerdo', 'pernil de cerdo', 'churrasquito de cerdo', 'chorizo de cerdo', 'bondiola', 'grasa porcina', 'panceta']):
                return 'Cerdos'

            # Pescados - expandir con más especies y productos
            if any(word in product_type_lower for word in ['pescado', 'salmón', 'atún', 'merluza', 'bacalao', 'trucha', 'lenguado', 'pacú', 'abadejo', 'brotola', 'surubí', 'truchón', 'boga', 'filet', 'filete', 'bastones de', 'crocantes de', 'medallón de', 'milanesa de merluza', 'formitas de', 'kanikama']):
                return 'Pescados'

            # Vacunos - cortes comunes de vaca y achuras
            if any(word in product_type_lower for word in ['vaca', 'ternera', 'novillo', 'bife', 'asado', 'entraña', 'matambre', 'churrasco', 'churrasquito', 'lomo', 'bola de lomo', 'colita de cuadril', 'cuadril', 'cuarto trasero', 'espinazo', 'nalga', 'osobuco', 'paleta', 'palomita', 'peceto', 'pechito de manta', 'picanha', 'ribbs', 'riñón', 'solomillo', 'tapa de nalga', 'vacío', 'milanesa de carne', 'plancha de asado', 'ojo de bife', 'roast beef', 'carnaza', 'carne picada', 'hígado', 'marucha', 'mondongo', 'suprema', 'suprema de fillete']):
                return 'Vacunos'

            # Ovinos
            if any(word in product_type_lower for word in ['cordero', 'oveja', 'borrego']):
                return 'Ovinos'

            # Conejos y Liebres
            if any(word in product_type_lower for word in ['conejo', 'liebre']):
                return 'Conejos y Liebres'

            # Embutidos - expandir con más tipos
            if any(word in product_type_lower for word in ['embutido', 'salchicha', 'chorizo', 'mortadela', 'salchicha parrillera', 'chorizo tipo candelario', 'morcilla', 'leberwurst']):
                return 'Embutidos'

            # Mariscos
            if any(word in product_type_lower for word in ['marisco', 'camarón', 'langostino', 'calamar', 'pulpo', 'anillas de calamar', 'mariscos congelados']):
                return 'Mariscos'

            # Productos procesados o no cárnicos que aparecen en esta categoría
            if any(word in product_type_lower for word in ['alcohol etílico', 'astilla ahumadora', 'briquetas de carbón', 'carbón', 'fósforos', 'leña', 'tortuga']):
                return 'Otros'

            # Todo lo demás va a Otros
            else:
                return 'Otros'

        # Agrupar tipos de producto por sub-categoría
        subcategories = {}
        for pt in product_types:
            subcategory = classify_product_type(pt)
            if subcategory not in subcategories:
                subcategories[subcategory] = []
            subcategories[subcategory].append(pt)

        # Imprimir el análisis
        print("Análisis de Tipos de Producto para Sub-Categorías en 'Carnes y Pescados'")
        print("=" * 70)
        for subcategory, types in subcategories.items():
            print(f"\nSub-Categoría: {subcategory}")
            print(f"Tipos de Producto ({len(types)}):")
            for t in types:
                print(f"  - {t}")
        print("\n" + "=" * 70)
        print(f"Total de Tipos de Producto encontrados: {len(product_types)}")
        print(f"Sub-Categorías propuestas: {len(subcategories)}")

    except Exception as e:
        print(f"Error durante el análisis: {e}")

    finally:
        # Cerrar el driver
        driver.quit()

if __name__ == "__main__":
    analyze_product_types_for_subcategories()