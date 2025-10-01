import os
import time
import logging
import re
import subprocess
import signal
import sys
import datetime
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from dotenv import load_dotenv
import colorama
from colorama import Fore, Style
import requests

# Initialize colorama for colored console output
colorama.init(autoreset=True)

# Load environment variables from backend directory
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.abspath(os.path.join(script_dir, '..', '..', '..', '..'))
env_path = os.path.join(backend_dir, '.env')
load_dotenv(env_path)

# Configure logging with better format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('dia_supermarket_info.log'),
        logging.StreamHandler()
    ]
)

class DiaSupermarketInfoScraper:
    def __init__(self):
        self.base_url = "https://diaonline.supermercadosdia.com.ar"
        self.api_url = "http://localhost:5000/api/supermarketinfo"  # API endpoint

        # Firefox options - headless mode for production
        self.options = Options()
        self.options.add_argument("--headless")  # Run in headless mode
        self.options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

        self.driver = None
        self.server_process = None

    def start_driver(self):
        """Initialize the Firefox WebDriver"""
        try:
            self.driver = webdriver.Firefox(options=self.options)
            logging.info("Firefox WebDriver started successfully")
        except Exception as e:
            logging.error(f"Failed to start WebDriver: {e}")
            raise

    def close_driver(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            logging.info("WebDriver closed")

    def start_server(self):
        """Start the Node.js backend server"""
        try:
            print(f"{Fore.CYAN}Starting backend server...{Style.RESET_ALL}")
            logging.info("Starting backend server")

            # Get the backend directory path - go up from script location to project root, then to backend
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.abspath(os.path.join(script_dir, '..', '..', '..', '..', '..', '..'))
            backend_dir = os.path.join(project_root, 'src', 'backend')

            print(f"{Fore.CYAN}Backend directory: {backend_dir}{Style.RESET_ALL}")

            self.server_process = subprocess.Popen(
                ['npm', 'start'],
                cwd=backend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True
            )

            # Wait for server to start
            print(f"{Fore.CYAN}Waiting for server to be ready...{Style.RESET_ALL}")
            time.sleep(10)  # Give server time to start

            # Test server connection
            max_attempts = 15  # Increased attempts
            for attempt in range(max_attempts):
                try:
                    response = requests.get('http://localhost:5000/api/supermarketinfo', timeout=5)
                    if response.status_code in [200, 404]:  # 404 is OK, means server is running
                        print(f"{Fore.GREEN}Server is ready!{Style.RESET_ALL}")
                        logging.info("Server started successfully")
                        return True
                except requests.exceptions.RequestException as e:
                    logging.warning(f"Server check attempt {attempt + 1} failed: {e}")
                    pass

                print(f"{Fore.YELLOW}Waiting for server... (attempt {attempt + 1}/{max_attempts}){Style.RESET_ALL}")
                time.sleep(3)

            print(f"{Fore.RED}Server failed to start properly{Style.RESET_ALL}")
            logging.error("Server failed to start")
            return False

        except Exception as e:
            print(f"{Fore.RED}Error starting server: {e}{Style.RESET_ALL}")
            logging.error(f"Error starting server: {e}")
            return False

    def stop_server(self):
        """Stop the Node.js backend server"""
        try:
            if self.server_process:
                print(f"{Fore.CYAN}Stopping backend server...{Style.RESET_ALL}")
                logging.info("Stopping backend server")

                # Try graceful shutdown first
                try:
                    self.server_process.terminate()
                    self.server_process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    # Force kill if graceful shutdown fails
                    self.server_process.kill()
                    self.server_process.wait()

                print(f"{Fore.GREEN}Server stopped{Style.RESET_ALL}")
                logging.info("Server stopped successfully")
        except Exception as e:
            print(f"{Fore.RED}Error stopping server: {e}{Style.RESET_ALL}")
            logging.error(f"Error stopping server: {e}")

    def extract_basic_info(self):
        """Extract basic supermarket information"""
        try:
            self.driver.get(self.base_url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Extract title
            title = self.driver.title

            # Extract meta description
            try:
                meta_desc = self.driver.find_element(By.CSS_SELECTOR, 'meta[name="description"]').get_attribute('content')
            except NoSuchElementException:
                meta_desc = None

            # Extract logo URL
            try:
                logo_element = self.driver.find_element(By.CSS_SELECTOR, 'img[alt*="Dia"], img[src*="logo"], img[class*="logo"]')
                logo_url = logo_element.get_attribute('src')
            except NoSuchElementException:
                logo_url = None

            # Extract favicon
            try:
                favicon = self.driver.find_element(By.CSS_SELECTOR, 'link[rel="icon"], link[rel="shortcut icon"]').get_attribute('href')
            except NoSuchElementException:
                favicon = None

            # Extract OG image
            try:
                og_image = self.driver.find_element(By.CSS_SELECTOR, 'meta[property="og:image"]').get_attribute('content')
            except NoSuchElementException:
                og_image = None

            basic_info = {
                "name": "Dia",
                "website": self.base_url,
                "country": "Argentina",
                "language": "es-AR",
                "currency": "ARS",
                "domain": "diaonline.supermercadosdia.com.ar",
                "charset": "utf-8",  # Default for modern sites
                "homepageMetadata": {
                    "title": title,
                    "description": meta_desc,
                    "ogImage": og_image,
                    "favicon": favicon
                }
            }

            logging.info(f"Extracted basic info: {basic_info}")
            return basic_info

        except Exception as e:
            logging.error(f"Error extracting basic info: {e}")
            return {}

    def extract_platform_info(self):
        """Extract platform and technical information"""
        try:
            platform_info = {}

            # Check for VTEX platform indicators
            page_source = self.driver.page_source.lower()
            if 'vtex' in page_source:
                platform_info["platform"] = "VTEX"

                # Try to extract VTEX version from scripts
                scripts = self.driver.find_elements(By.TAG_NAME, 'script')
                for script in scripts:
                    src = script.get_attribute('src') or ''
                    if 'vtex' in src.lower():
                        # Look for version patterns in URL
                        version_match = re.search(r'v(\d+\.\d+\.\d+)', src)
                        if version_match:
                            platform_info["platformVersion"] = version_match.group(1)
                            break

                # Extract workspace from URL or meta
                try:
                    workspace_meta = self.driver.find_element(By.CSS_SELECTOR, 'meta[name="vtex-workspace"]')
                    platform_info["workspace"] = workspace_meta.get_attribute('content')
                except NoSuchElementException:
                    platform_info["workspace"] = "master"  # Default

            # Check for PWA
            try:
                manifest_link = self.driver.find_element(By.CSS_SELECTOR, 'link[rel="manifest"]')
                platform_info["pwa"] = {
                    "enabled": True,
                    "manifest": manifest_link.get_attribute('href')
                }
            except NoSuchElementException:
                platform_info["pwa"] = {"enabled": False}

            # Extract theme color
            try:
                theme_color = self.driver.find_element(By.CSS_SELECTOR, 'meta[name="theme-color"]').get_attribute('content')
                if platform_info.get("pwa"):
                    platform_info["pwa"]["themeColor"] = theme_color
            except NoSuchElementException:
                pass

            logging.info(f"Extracted platform info: {platform_info}")
            return platform_info

        except Exception as e:
            logging.error(f"Error extracting platform info: {e}")
            return {}

    def extract_analytics_info(self):
        """Extract analytics and tracking information"""
        try:
            analytics_info = {}

            # Get all scripts
            scripts = self.driver.find_elements(By.TAG_NAME, 'script')
            script_contents = []
            script_srcs = []

            for script in scripts:
                src = script.get_attribute('src')
                if src:
                    script_srcs.append(src)
                content = script.get_attribute('innerHTML')
                if content:
                    script_contents.append(content)

            # Extract Google Analytics (GA4)
            ga_pattern = r'G-[A-Z0-9]+'
            for content in script_contents:
                ga_match = re.search(ga_pattern, content)
                if ga_match:
                    analytics_info["googleAnalytics"] = ga_match.group(0)
                    break

            # Extract Google Tag Manager
            gtm_pattern = r'GTM-[A-Z0-9]+'
            analytics_info["googleTagManager"] = []
            for content in script_contents:
                gtm_matches = re.findall(gtm_pattern, content)
                analytics_info["googleTagManager"].extend(gtm_matches)

            # Extract Facebook Pixel
            fb_pattern = r'fbq\([\'"]init[\'"],\s*[\'"]([^\'"]+)[\'"]'
            for content in script_contents:
                fb_match = re.search(fb_pattern, content)
                if fb_match:
                    analytics_info["facebookPixel"] = fb_match.group(1)
                    break

            # Check for Dynamic Yield
            if any('dynamicyield' in src.lower() for src in script_srcs):
                analytics_info["dynamicYield"] = "present"

            logging.info(f"Extracted analytics info: {analytics_info}")
            return {"analytics": analytics_info}

        except Exception as e:
            logging.error(f"Error extracting analytics info: {e}")
            return {}

    def extract_legal_info(self):
        """Extract legal and policy information"""
        try:
            legal_info = {}

            # Look for footer links
            footer_links = self.driver.find_elements(By.CSS_SELECTOR, 'footer a, .footer a, [class*="footer"] a')
            for link in footer_links:
                href = link.get_attribute('href')
                text = link.text.lower().strip()
                if href and href.startswith('http'):
                    if any(word in text for word in ['privacidad', 'privacy', 'política de privacidad']):
                        legal_info["privacyPolicy"] = href
                    elif any(word in text for word in ['términos', 'terminos', 'terms', 'condiciones']):
                        legal_info["termsAndConditions"] = href
                    elif 'cookies' in text:
                        legal_info["cookiePolicy"] = href
                    elif any(word in text for word in ['consumidor', 'defensa']):
                        legal_info["consumerDefense"] = href

            logging.info(f"Extracted legal info: {legal_info}")
            return {"legalInfo": legal_info}

        except Exception as e:
            logging.error(f"Error extracting legal info: {e}")
            return {}

    def extract_logo_info(self):
        """Extract logo and isoLogo information"""
        try:
            logo_info = {}

            # Try to find main logo
            try:
                logo_element = self.driver.find_element(By.CSS_SELECTOR, 'img[alt*="Dia"], img[src*="logo"], header img, .logo img')
                logo_info["logo"] = logo_element.get_attribute('src')
            except NoSuchElementException:
                pass

            # Try to find iso logo (smaller version)
            try:
                iso_logo = self.driver.find_element(By.CSS_SELECTOR, 'img[alt*="iso"], img[class*="iso"], .isotipo img')
                logo_info["isoLogo"] = iso_logo.get_attribute('src')
            except NoSuchElementException:
                pass

            logging.info(f"Extracted logo info: {logo_info}")
            return logo_info

        except Exception as e:
            logging.error(f"Error extracting logo info: {e}")
            return {}

    def save_to_api(self, data):
        """Save extracted data via REST API with upsert logic"""
        try:
            # Set custom code identifier
            data["code"] = "dia"

            # Note: updatedAt will be handled automatically by Mongoose timestamps

            logging.info("🔍 Checking if Dia data already exists...")
            print(f"{Fore.CYAN}🔍 Checking if Dia data already exists...{Style.RESET_ALL}")

            # First, verify server is still running before making requests
            try:
                health_check = requests.get('http://localhost:5000/api/supermarketinfo', timeout=5)
                if health_check.status_code not in [200, 404]:
                    raise Exception(f"Server health check failed with status {health_check.status_code}")
            except Exception as e:
                logging.error(f"Server health check failed: {e}")
                print(f"{Fore.RED}❌ Server health check failed: {e}{Style.RESET_ALL}")
                raise Exception("Server is not responding")

            # Check if a document with code "dia" already exists
            search_url = f"{self.api_url}?code=dia"
            logging.info(f"Searching for existing document at: {search_url}")
            print(f"{Fore.CYAN}🔍 Searching for existing document at: {search_url}{Style.RESET_ALL}")
            search_response = requests.get(search_url, timeout=10)

            logging.info(f"Search response status: {search_response.status_code}")
            print(f"{Fore.CYAN}📊 Search response status: {search_response.status_code}{Style.RESET_ALL}")

            # Log response content (truncated for readability)
            response_preview = search_response.text[:200] + "..." if len(search_response.text) > 200 else search_response.text
            logging.info(f"Search response content: {response_preview}")
            print(f"{Fore.CYAN}📄 Search response: {response_preview}{Style.RESET_ALL}")

            existing_document = None
            if search_response.status_code == 200:
                search_result = search_response.json()
                logging.info(f"Parsed search result: {len(search_result.get('supermarketInfos', []))} documents found")
                if search_result.get('supermarketInfos') and len(search_result['supermarketInfos']) > 0:
                    existing_document = search_result['supermarketInfos'][0]
                    logging.info(f"Found existing Dia document with ID: {existing_document['_id']}")
                    print(f"{Fore.YELLOW}📋 Found existing Dia document with ID: {existing_document['_id']}{Style.RESET_ALL}")
                else:
                    logging.info("No existing documents found with code filter, trying name filter...")
                    print(f"{Fore.YELLOW}⚠️  No existing documents found with code filter, trying name filter...{Style.RESET_ALL}")
                    # Try searching by name instead
                    search_url_name = f"{self.api_url}?search=Dia"
                    logging.info(f"Searching by name at: {search_url_name}")
                    print(f"{Fore.CYAN}🔍 Searching by name at: {search_url_name}{Style.RESET_ALL}")
                    search_response_name = requests.get(search_url_name, timeout=10)
                    if search_response_name.status_code == 200:
                        search_result_name = search_response_name.json()
                        logging.info(f"Name search result: {len(search_result_name.get('supermarketInfos', []))} documents found")
                        print(f"{Fore.CYAN}📊 Name search result: {len(search_result_name.get('supermarketInfos', []))} documents found{Style.RESET_ALL}")
                        if search_result_name.get('supermarketInfos') and len(search_result_name['supermarketInfos']) > 0:
                            existing_document = search_result_name['supermarketInfos'][0]
                            logging.info(f"Found existing Dia document by name with ID: {existing_document['_id']}")
                            print(f"{Fore.YELLOW}📋 Found existing Dia document by name with ID: {existing_document['_id']}{Style.RESET_ALL}")
            else:
                logging.error(f"Search request failed with status: {search_response.status_code}")
                print(f"{Fore.RED}❌ Search request failed with status: {search_response.status_code}{Style.RESET_ALL}")

            if existing_document:
                # Update existing document
                update_url = f"{self.api_url}/{existing_document['_id']}"
                logging.info(f"Updating existing document at {update_url}")
                print(f"{Fore.CYAN}📤 Updating existing document at: {update_url}{Style.RESET_ALL}")

                response = requests.put(update_url, json=data, headers={'Content-Type': 'application/json'}, timeout=10)

                if response.status_code == 200:
                    result = response.json()
                    logging.info("✅ Data updated successfully")
                    print(f"{Fore.GREEN}✅ Data updated successfully{Style.RESET_ALL}")
                    # Log key updated fields
                    if 'supermarketInfo' in result:
                        updated_at = result['supermarketInfo'].get('updatedAt', 'N/A')
                        logging.info(f"Document updated at: {updated_at}")
                        print(f"{Fore.GREEN}🕒 Document updated at: {updated_at}{Style.RESET_ALL}")
                    return result
                else:
                    logging.error(f"Update failed with status {response.status_code}: {response.text}")
                    print(f"{Fore.RED}❌ Update failed with status {response.status_code}{Style.RESET_ALL}")
                    raise Exception(f"Update failed: {response.status_code}")
            else:
                # Create new document
                logging.info(f"Creating new document at {self.api_url}")
                print(f"{Fore.CYAN}🆕 Creating new document at: {self.api_url}{Style.RESET_ALL}")

                response = requests.post(self.api_url, json=data, headers={'Content-Type': 'application/json'}, timeout=10)

                if response.status_code == 201:
                    result = response.json()
                    logging.info("✅ New document created successfully")
                    print(f"{Fore.GREEN}✅ New document created successfully{Style.RESET_ALL}")
                    # Log creation timestamp
                    if 'supermarketInfo' in result:
                        created_at = result['supermarketInfo'].get('createdAt', 'N/A')
                        logging.info(f"Document created at: {created_at}")
                        print(f"{Fore.GREEN}🕒 Document created at: {created_at}{Style.RESET_ALL}")
                    return result
                else:
                    logging.error(f"Creation failed with status {response.status_code}: {response.text}")
                    print(f"{Fore.RED}❌ Creation failed with status {response.status_code}{Style.RESET_ALL}")
                    raise Exception(f"Creation failed: {response.status_code}")

        except Exception as e:
            logging.error(f"Error in save_to_api: {str(e)}")
            print(f"{Fore.RED}❌ Error saving to API: {str(e)}{Style.RESET_ALL}")
            raise

    def run(self):
        """Main execution method"""
        server_started = False
        try:
            print(f"{Fore.YELLOW}🚀 Starting Dia Supermarket Info Scraper...{Style.RESET_ALL}")
            logging.info("🚀 Starting Dia Supermarket Info Scraper")

            # Start the backend server
            server_started = self.start_server()
            if not server_started:
                raise Exception("Failed to start backend server")

            # Start WebDriver
            self.start_driver()

            # Extract all information
            basic_info = self.extract_basic_info()
            platform_info = self.extract_platform_info()
            analytics_info = self.extract_analytics_info()
            legal_info = self.extract_legal_info()
            logo_info = self.extract_logo_info()

            # Combine all data
            supermarket_data = {
                **basic_info,
                **platform_info,
                **analytics_info,
                **legal_info,
                **logo_info,
                "lastHomepageScraped": datetime.datetime.now().isoformat()
            }

            print(f"{Fore.GREEN}✅ Data extraction completed successfully{Style.RESET_ALL}")
            logging.info("✅ Data extraction completed successfully")

            # Verify server is still running before saving
            print(f"{Fore.CYAN}🔍 Verifying server status before saving...{Style.RESET_ALL}")
            try:
                health_response = requests.get('http://localhost:5000/api/supermarketinfo', timeout=5)
                if health_response.status_code not in [200, 404]:
                    print(f"{Fore.YELLOW}⚠️  Server not responding, attempting restart...{Style.RESET_ALL}")
                    # Try to restart server
                    if hasattr(self, 'server_process') and self.server_process:
                        self.stop_server()
                    server_restarted = self.start_server()
                    if not server_restarted:
                        raise Exception("Failed to restart server")
            except Exception as e:
                print(f"{Fore.YELLOW}⚠️  Server health check failed, attempting restart: {e}{Style.RESET_ALL}")
                # Try to restart server
                if hasattr(self, 'server_process') and self.server_process:
                    self.stop_server()
                server_restarted = self.start_server()
                if not server_restarted:
                    raise Exception("Failed to restart server")

            # Save to API
            self.save_to_api(supermarket_data)

            print(f"{Fore.GREEN}🎉 Scraping completed successfully!{Style.RESET_ALL}")
            logging.info("🎉 Scraping completed successfully")

        except Exception as e:
            print(f"{Fore.RED}💥 Error during scraping: {e}{Style.RESET_ALL}")
            logging.error(f"💥 Error during scraping: {e}")
        finally:
            # Always close WebDriver
            self.close_driver()

            # Always stop server if it was started
            if server_started:
                self.stop_server()


if __name__ == "__main__":
    scraper = DiaSupermarketInfoScraper()
    scraper.run()