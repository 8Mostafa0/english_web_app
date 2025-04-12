import requests
from bs4 import BeautifulSoup
import time
import csv
import random
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import json
import os
from datetime import datetime
import logging
import sys
from selenium.common.exceptions import TimeoutException, WebDriverException
import pickle

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('quizlet_scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class QuizletScraper:
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.cookies_file = "quizlet_cookies.pkl"
        self.setup_headers()
        self.setup_selenium()
        
    def setup_headers(self):
        """Setup rotating headers and user agents"""
        try:
            self.headers = {
                "User-Agent": self.ua.random,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Cache-Control": "max-age=0",
                "TE": "Trailers"
            }
            self.session.headers.update(self.headers)
            logging.info("Headers setup completed successfully")
        except Exception as e:
            logging.error(f"Error setting up headers: {str(e)}")
            raise
        
    def setup_selenium(self):
        """Setup undetected Chrome driver with cookie persistence"""
        try:
            options = uc.ChromeOptions()
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-extensions')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-infobars')
            options.add_argument('--disable-notifications')
            options.add_argument('--disable-popup-blocking')
            options.add_argument('--disable-web-security')
            
            # Add random window size
            width = random.randint(1024, 1920)
            height = random.randint(768, 1080)
            options.add_argument(f'--window-size={width},{height}')
            
            # Set user data directory for persistent cookies
            user_data_dir = os.path.join(os.getcwd(), 'chrome_profile')
            options.add_argument(f'--user-data-dir={user_data_dir}')
            
            logging.info("Initializing Chrome driver...")
            self.driver = uc.Chrome(options=options)
            logging.info("Chrome driver initialized successfully")
            
            # Load cookies if they exist
            self.load_cookies()
            
        except Exception as e:
            logging.error(f"Error setting up Selenium: {str(e)}")
            raise

    def load_cookies(self):
        """Load cookies from file if they exist"""
        try:
            if os.path.exists(self.cookies_file):
                with open(self.cookies_file, 'rb') as f:
                    cookies = pickle.load(f)
                    for cookie in cookies:
                        self.driver.add_cookie(cookie)
                logging.info("Successfully loaded cookies")
        except Exception as e:
            logging.warning(f"Error loading cookies: {str(e)}")

    def save_cookies(self):
        """Save current cookies to file"""
        try:
            cookies = self.driver.get_cookies()
            with open(self.cookies_file, 'wb') as f:
                pickle.dump(cookies, f)
            logging.info("Successfully saved cookies")
        except Exception as e:
            logging.warning(f"Error saving cookies: {str(e)}")

    def human_like_delay(self):
        """Simulate human-like delays"""
        delay = random.uniform(2, 5)
        logging.debug(f"Waiting for {delay:.2f} seconds")
        time.sleep(delay)

    def check_login_status(self):
        """Check if user is logged in"""
        try:
            # Look for login button or user profile element
            login_button = self.driver.find_elements(By.CSS_SELECTOR, "button[data-testid='header-login-button']")
            return len(login_button) == 0  # If no login button found, user is logged in
        except Exception as e:
            logging.warning(f"Error checking login status: {str(e)}")
            return False

    def extract_data_examples(self, url):
        """Example method showing different ways to extract data based on website structure"""
        try:
            self.driver.get(url)
            print(self.driver)
            self.human_like_delay()
            
            # Example 1: Using ID selector
            # <div id="id-cars-place">
            #     <div id="cards">...</div>
            # </div>
            try:
                title = ""
                parent_div = self.driver.find_element(By.CLASS_NAME, "l1i8mi1u")
                carsd_data = parent_div.find_elements(By.CLASS_NAME,"SetPreviewCard-title")
                for i in carsd_data:
                    link = i.find_element(By.TAG_NAME,"a").get_attribute("href")
                    print(link)
                    title = i.find_element(By.TAG_NAME,"a").text
                    print(title)
                logging.info("Found elements using ID selectors")
            except Exception as e:
                logging.warning(f"ID selector example failed: {str(e)}")

        except Exception as e:
            logging.error(f"Error in extract_data_examples: {str(e)}")


    def save_to_csv(self, data, filename="quizlet_flashcards.csv"):
        """Save scraped flashcards to CSV"""
        try:
            with open(filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["term", "definition", "scraped_at"])
                writer.writeheader()
                writer.writerows(data)
            logging.info(f"Successfully saved {len(data)} flashcards to {filename}")
        except Exception as e:
            logging.error(f"Error saving to CSV: {str(e)}")
            raise

    def save_to_json(self, data, filename="quizlet_flashcards.json"):
        """Save scraped flashcards to JSON"""
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logging.info(f"Successfully saved {len(data)} flashcards to {filename}")
        except Exception as e:
            logging.error(f"Error saving to JSON: {str(e)}")
            raise
            
    def close(self):
        """Clean up resources"""
        try:
            if hasattr(self, 'driver'):
                self.save_cookies()  # Save cookies before closing
                self.driver.quit()
                logging.info("Chrome driver closed successfully")
            if hasattr(self, 'session'):
                self.session.close()
                logging.info("Session closed successfully")
        except Exception as e:
            logging.error(f"Error during cleanup: {str(e)}")

def main():
    # Quizlet flashcards URL
    url = "https://quizlet.com/exams/toefl/toefl-vocabulary-e473ccd-s01"
    
    scraper = None
    try:
        logging.info("Starting Quizlet flashcards scraping...")
        scraper = QuizletScraper()
        
        # Demonstrate different extraction methods
        scraper.extract_data_examples(url)
        
    except Exception as e:
        logging.error(f"An error occurred in main: {str(e)}")
    finally:
        if scraper:
            scraper.close()

if __name__ == "__main__":
    main()