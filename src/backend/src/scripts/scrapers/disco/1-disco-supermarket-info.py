#!/usr/bin/env python3
"""
Supermarket Info Scraper for Disco
Extracts comprehensive metadata from Disco's homepage including:
- Basic info (name, logo, website)
- Geographic info (country, language, currency)
- Technical platform details (VTEX version, theme)
- Analytics and tracking systems
- Legal information (terms, privacy policy)
- PWA configuration
- Cookie consent settings
"""

import os
import json
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import re
import time
import requests
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv

try:
    from colorama import init, Fore, Back, Style
    COLORAMA_AVAILABLE = True
    init(autoreset=True)
except ImportError:
    COLORAMA_AVAILABLE = False

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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DiscoSupermarketInfoScraper:
    def __init__(self):
        # Load environment variables
        load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '.env'))

        self.base_url = "https://www.disco.com.ar"
        self.mongo_uri = os.getenv('MONGO_DISCO_URI')
        self.driver = None
        self.wait_timeout = 60  # Increased timeout for Disco website
        self.mongo_client = None
        self.db = None

    def connect_mongodb(self):
        """Connect to MongoDB Atlas"""
        try:
            if not self.mongo_uri:
                logger.warning("MONGO_DISCO_URI not found in environment variables")
                return False

            self.mongo_client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=5000)
            # Test the connection
            self.mongo_client.admin.command('ping')
            self.db = self.mongo_client.disco  # Database name from URI
            print_success("Connected to MongoDB Atlas successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False

    def disconnect_mongodb(self):
        """Disconnect from MongoDB"""
        if self.mongo_client:
            self.mongo_client.close()
            print_info("Disconnected from MongoDB")

    def setup_driver(self):
        """Configure Edge WebDriver with appropriate options"""
        try:
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-plugins")
            options.add_argument("--disable-images")  # Speed up loading
            options.add_argument("--disable-javascript")  # We need JS for dynamic content
            options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            # Suppress Chromium error messages
            options.add_argument("--log-level=3")
            options.add_argument("--disable-logging")
            options.add_argument("--silent")
            options.add_argument("--disable-dev-tools")

            self.driver = webdriver.Edge(options=options)
            self.driver.maximize_window()

            # Set page load timeout
            self.driver.set_page_load_timeout(self.wait_timeout)
            self.wait = WebDriverWait(self.driver, self.wait_timeout)

            print_success("WebDriver configured successfully")
        except Exception as e:
            logger.error(f"Failed to setup WebDriver: {e}")
            raise

    def extract_basic_info(self):
        """Extract basic supermarket information"""
        try:
            # Get title
            title = self.driver.title or "Supermercado Disco Online | Todo lo Que Necesitás"

            # Extract meta tags
            meta_tags = {}
            meta_elements = self.driver.find_elements(By.TAG_NAME, "meta")
            for meta in meta_elements:
                name = meta.get_attribute("name") or meta.get_attribute("property")
                content = meta.get_attribute("content")
                if name and content:
                    meta_tags[name] = content

            # Extract logo URL - use the correct logo URL from HTML analysis
            logo_url = None
            try:
                # Use the logo URL found in the HTML
                logo_url = "https://discoargentina.vtexassets.com/assets/vtex.file-manager-graphql/images/bd790034-1117-4263-90e5-04f3f5a27503___ab950355900559ccc0bc0cb131364561.png"

                # Verify the URL exists
                try:
                    response = requests.head(logo_url, timeout=5)
                    if response.status_code != 200:
                        logger.warning(f"Logo URL returned status {response.status_code}")
                except:
                    logger.warning("Could not verify logo URL accessibility")

            except Exception as e:
                logger.warning(f"Could not extract logo: {e}")
                # Fallback to known logo URL
                logo_url = "https://discoargentina.vtexassets.com/assets/vtex.file-manager-graphql/images/bd790034-1117-4263-90e5-04f3f5a27503___ab950355900559ccc0bc0cb131364561.png"

            # Extract isoLogo URL - use the same logo URL
            iso_logo_url = None
            try:
                # Use the same logo URL for isoLogo
                iso_logo_url = "https://discoargentina.vtexassets.com/assets/vtex.file-manager-graphql/images/bd790034-1117-4263-90e5-04f3f5a27503___ab950355900559ccc0bc0cb131364561.png"

                # Verify the URL exists
                try:
                    response = requests.head(iso_logo_url, timeout=5)
                    if response.status_code != 200:
                        logger.warning(f"IsoLogo URL returned status {response.status_code}")
                except:
                    logger.warning("Could not verify isoLogo URL accessibility")

            except Exception as e:
                logger.warning(f"Could not extract isoLogo: {e}")
                # Fallback to known isoLogo URL
                iso_logo_url = "https://discoargentina.vtexassets.com/assets/vtex.file-manager-graphql/images/bd790034-1117-4263-90e5-04f3f5a27503___ab950355900559ccc0bc0cb131364561.png"

            return {
                "name": "Disco",
                "website": self.base_url,
                "logo": logo_url,
                "isoLogo": iso_logo_url,
                "title": title,
                "meta_tags": meta_tags
            }
        except Exception as e:
            logger.error(f"Error extracting basic info: {e}")
            return {}

    def extract_geographic_info(self, meta_tags):
        """Extract geographic and regional information"""
        return {
            "country": "ARG",  # Argentina
            "language": "es-AR",  # Spanish - Argentina
            "currency": "ARS"  # Argentine Peso
        }

    def extract_platform_info(self):
        """Extract VTEX platform and technical information"""
        platform_info = {
            "platform": "VTEX",
            "platformVersion": None,
            "theme": None,
            "themeVersion": None,
            "workspace": "master"  # Default VTEX workspace
        }

        try:
            # Look for VTEX render server version
            scripts = self.driver.find_elements(By.TAG_NAME, "script")
            for script in scripts:
                src = script.get_attribute("src") or ""
                if "vtexassets.com" in src and "render-runtime" in src:
                    # Extract version from URL
                    version_match = re.search(r'@(\d+\.\d+\.\d+)', src)
                    if version_match:
                        platform_info["platformVersion"] = version_match.group(1)

                # Look for theme information
                if "discoargentina.store" in src:
                    theme_match = re.search(r'discoargentina\.store@([\d.]+)', src)
                    if theme_match:
                        platform_info["theme"] = "discoargentina.store"
                        platform_info["themeVersion"] = theme_match.group(1)

        except Exception as e:
            logger.warning(f"Could not extract platform info: {e}")

        return platform_info

    def extract_analytics_info(self):
        """Extract analytics and tracking systems information"""
        analytics = {
            "googleAnalytics": None,
            "googleTagManager": [],
            "facebookPixel": None,
            "tiktokPixel": [],
            "hotjar": None,
            "activityFlow": False,
            "survicate": False,
            "icommTracker": False
        }

        try:
            scripts = self.driver.find_elements(By.TAG_NAME, "script")

            for script in scripts:
                script_content = script.get_attribute("innerHTML") or ""

                # Google Analytics 4
                ga4_match = re.search(r'G-([A-Z0-9]{10,})', script_content)
                if ga4_match and not analytics["googleAnalytics"]:
                    analytics["googleAnalytics"] = f"G-{ga4_match.group(1)}"

                # Google Tag Manager
                gtm_match = re.search(r'GTM-([A-Z0-9]+)', script_content)
                if gtm_match:
                    analytics["googleTagManager"].append(f"GTM-{gtm_match.group(1)}")

                # Facebook Pixel
                fb_pixel_match = re.search(r'pixelId["\s]*:[\s]*["\'](\d+)["\']', script_content)
                if fb_pixel_match:
                    analytics["facebookPixel"] = fb_pixel_match.group(1)

                # TikTok Pixel
                tiktok_match = re.search(r'sdkid["\s]*:[\s]*["\']([A-Z0-9]+)["\']', script_content)
                if tiktok_match and "ttq" in script_content:
                    analytics["tiktokPixel"].append(tiktok_match.group(1))

                # Hotjar
                if "hotjar" in script.get_attribute("src") or "":
                    hj_match = re.search(r'hjid["\s]*:[\s]*(\d+)', script_content)
                    if hj_match:
                        analytics["hotjar"] = hj_match.group(1)

                # Activity Flow
                if "activity-flow.vtex.com" in script_content:
                    analytics["activityFlow"] = True

                # Survicate
                if "survicate.com" in script.get_attribute("src") or "":
                    analytics["survicate"] = True

                # Icomm Tracker
                if "icomm-sites" in script.get_attribute("src") or "":
                    analytics["icommTracker"] = True

        except Exception as e:
            logger.warning(f"Could not extract analytics info: {e}")

        return analytics

    def extract_legal_info(self):
        """Extract legal information and policy URLs"""
        legal_info = {
            "termsAndConditions": None,
            "privacyPolicy": None,
            "consumerDefense": "https://www.argentina.gob.ar/produccion/defensadelconsumidor/formulario",
            "cookiePolicy": None
        }

        try:
            # Look for legal links in footer or content
            links = self.driver.find_elements(By.TAG_NAME, "a")
            for link in links:
                href = link.get_attribute("href") or ""
                text = link.text.lower().strip()

                if "términos" in text or "terminos" in text or "legales" in href:
                    if "legales" in href or "terminos" in href:
                        legal_info["termsAndConditions"] = href

                if "privacidad" in text or "privacidad" in href:
                    legal_info["privacyPolicy"] = href

                if "cookies" in text or "cookies" in href:
                    legal_info["cookiePolicy"] = href

                # Also check for specific URLs we know from HTML analysis
                if "disco.com.ar/legales" in href:
                    legal_info["termsAndConditions"] = href
                    legal_info["privacyPolicy"] = href
                    legal_info["cookiePolicy"] = href

        except Exception as e:
            logger.warning(f"Could not extract legal info: {e}")

        return legal_info

    def extract_pwa_info(self):
        """Extract Progressive Web App information"""
        pwa_info = {
            "enabled": False,
            "manifest": None,
            "themeColor": None,
            "icons": []
        }

        try:
            # Check for manifest link
            manifest_link = self.driver.find_elements(By.CSS_SELECTOR, "link[rel='manifest']")
            if manifest_link:
                pwa_info["enabled"] = True
                pwa_info["manifest"] = manifest_link[0].get_attribute("href")

            # Extract theme color
            theme_meta = self.driver.find_elements(By.CSS_SELECTOR, "meta[name='theme-color']")
            if theme_meta:
                pwa_info["themeColor"] = theme_meta[0].get_attribute("content")

            # Extract PWA icons
            icon_links = self.driver.find_elements(By.CSS_SELECTOR, "link[rel*='apple-touch-icon'], link[rel*='icon']")
            for icon in icon_links:
                icon_info = {
                    "src": icon.get_attribute("href"),
                    "sizes": icon.get_attribute("sizes"),
                    "type": icon.get_attribute("type")
                }
                pwa_info["icons"].append(icon_info)

        except Exception as e:
            logger.warning(f"Could not extract PWA info: {e}")

        return pwa_info

    def extract_cookie_consent_info(self):
        """Extract cookie consent system information"""
        cookie_info = {
            "provider": None,
            "privacyUrl": None,
            "consentRequired": True
        }

        try:
            # Look for OneTrust or similar cookie consent systems
            scripts = self.driver.find_elements(By.TAG_NAME, "script")
            for script in scripts:
                src = script.get_attribute("src") or ""
                content = script.get_attribute("innerHTML") or ""

                if "cookielaw.org" in src or "onetrust" in content.lower():
                    cookie_info["provider"] = "OneTrust"

                # Look for privacy policy URL in cookie banner
                privacy_match = re.search(r'privacy.*?(https?://[^\s"\'<>]+)', content, re.IGNORECASE)
                if privacy_match:
                    cookie_info["privacyUrl"] = privacy_match.group(1)

        except Exception as e:
            logger.warning(f"Could not extract cookie consent info: {e}")

        return cookie_info

    def scrape_supermarket_info(self):
        """Main scraping function"""
        try:
            print_info("Starting Disco supermarket info scraping")

            # Connect to MongoDB
            mongo_connected = self.connect_mongodb()

            # Setup WebDriver
            self.setup_driver()

            # Navigate to homepage
            print_info(f"Navigating to {self.base_url}")
            self.driver.get(self.base_url)

            # Wait for page to load
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "title")))

            # Give extra time for dynamic content (Disco website is slower)
            time.sleep(5)

            # Extract all information
            basic_info = self.extract_basic_info()
            geographic_info = self.extract_geographic_info(basic_info.get("meta_tags", {}))
            platform_info = self.extract_platform_info()
            analytics_info = self.extract_analytics_info()
            legal_info = self.extract_legal_info()
            pwa_info = self.extract_pwa_info()
            cookie_info = self.extract_cookie_consent_info()

            # Compile final data
            supermarket_data = {
                "_id": ObjectId(),
                "code": "disco",
                "name": basic_info.get("name", "Disco"),
                "logo": basic_info.get("logo"),
                "isoLogo": basic_info.get("isoLogo"),
                "website": basic_info.get("website", self.base_url),
                "country": geographic_info.get("country"),
                "language": geographic_info.get("language"),
                "currency": geographic_info.get("currency"),
                "platform": platform_info.get("platform"),
                "platformVersion": platform_info.get("platformVersion"),
                "theme": platform_info.get("theme"),
                "themeVersion": platform_info.get("themeVersion"),
                "workspace": platform_info.get("workspace"),
                "domain": "www.disco.com.ar",
                "charset": "utf-8",
                "analytics": analytics_info,
                "homepageMetadata": {
                    "title": basic_info.get("title"),
                    "description": basic_info.get("meta_tags", {}).get("description"),
                    "robots": basic_info.get("meta_tags", {}).get("robots"),
                    "storefront": basic_info.get("meta_tags", {}).get("storefront"),
                    "copyright": basic_info.get("meta_tags", {}).get("copyright"),
                    "author": basic_info.get("meta_tags", {}).get("author")
                },
                "legalInfo": legal_info,
                "pwa": pwa_info,
                "cookieConsent": cookie_info,
                "active": True,
                "lastHomepageScraped": datetime.now(),
                "createdAt": datetime.now(),
                "updatedAt": datetime.now()
            }

            # Save to MongoDB if connected
            if mongo_connected:
                mongo_saved = self.save_to_mongodb(supermarket_data)
                if mongo_saved:
                    print_success("Data saved to MongoDB Atlas successfully")
                else:
                    print_warning("Failed to save data to MongoDB Atlas")
            else:
                print_warning("MongoDB not connected - data only saved to JSON")

            print_success("Supermarket info scraping completed successfully")
            return supermarket_data

        except Exception as e:
            logger.error(f"Error during supermarket info scraping: {e}")
            raise
        finally:
            if self.driver:
                self.driver.quit()
            self.disconnect_mongodb()

    def save_to_mongodb(self, data):
        """Save scraped data to MongoDB Atlas"""
        if self.db is None:
            logger.warning("MongoDB connection not available")
            return False

        try:
            collection = self.db['supermarket-info']

            # Check if document already exists
            existing_doc = collection.find_one({'code': data['code']})

            if existing_doc:
                # Update existing document (exclude _id from update)
                update_data = {k: v for k, v in data.items() if k != '_id'}
                result = collection.update_one(
                    {'code': data['code']},
                    {'$set': update_data}
                )
                print_success(f"Updated existing document with code: {data['code']}")
            else:
                # Insert new document (include _id)
                result = collection.insert_one(data)
                print_success(f"Inserted new document with ID: {result.inserted_id}")

            return True
        except Exception as e:
            logger.error(f"Failed to save to MongoDB: {e}")
            return False

    def save_to_json(self, data, filename=None):
        """Save scraped data to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"disco_supermarket_info_{timestamp}.json"

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            print_success(f"Data saved to {filename}")
        except Exception as e:
            logger.error(f"Failed to save data to JSON: {e}")

def main():
    """Main execution function"""
    scraper = DiscoSupermarketInfoScraper()

    try:
        # Scrape supermarket info
        data = scraper.scrape_supermarket_info()

        # Print summary
        print("\n=== Disco Supermarket Info Scraped ===")
        print(f"Name: {data.get('name')}")
        print(f"Website: {data.get('website')}")
        print(f"Logo: {data.get('logo')}")
        print(f"isoLogo: {data.get('isoLogo')}")
        print(f"Platform: {data.get('platform')} {data.get('platformVersion')}")
        print(f"Theme: {data.get('theme')} {data.get('themeVersion')}")
        print(f"Country: {data.get('country')}, Language: {data.get('language')}, Currency: {data.get('currency')}")
        print(f"PWA Enabled: {data.get('pwa', {}).get('enabled', False)}")
        print(f"Analytics: GA4={data.get('analytics', {}).get('googleAnalytics')}, GTM={len(data.get('analytics', {}).get('googleTagManager', []))}")
        print(f"Legal Info: Terms={bool(data.get('legalInfo', {}).get('termsAndConditions'))}")

    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    main()