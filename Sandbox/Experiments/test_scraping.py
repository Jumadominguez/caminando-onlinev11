from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
import time

# Setup driver
firefox_options = Options()
firefox_options.add_argument('--headless')
geckodriver_path = r'd:\dev\caminando-onlinev10\geckodriver_temp\geckodriver.exe'
service = Service(geckodriver_path)
driver = webdriver.Firefox(service=service, options=firefox_options)

try:
    # Navigate to Carrefour
    driver.get('https://www.carrefour.com.ar/bebidas')
    time.sleep(5)
    print('Successfully navigated to Carrefour bebidas page')
    
    # Try to find filters panel
    from selenium.webdriver.common.by import By
    try:
        filter_button = driver.find_element(By.XPATH, \"//button[contains(text(), 'Filtrar')]\")
        filter_button.click()
        print('Successfully opened filters panel')
    except Exception as e:
        print(f'Could not find filter button: {e}')
    
    time.sleep(3)
    
except Exception as e:
    print(f'Error: {e}')
finally:
    driver.quit()
    print('Test completed')
