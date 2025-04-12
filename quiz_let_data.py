import sys
import requests
from bs4 import BeautifulSoup
import csv
import time
import random
impo
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage, QWebEngineSettings

class CustomBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Custom Browser for Quizlet Scraping")
        self.setGeometry(100, 100, 1200, 800)

        # Set up session for requests
        self.session = requests.Session()
        self.headers = {
            # Mimic Firefox 115 on Windows 10
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'DNT': '1',  # Do Not Track
            'Referer': 'https://quizlet.com/',
        }
        self.session.headers.update(self.headers)

        # Set up the browser profile to mimic Firefox
        self.profile = QWebEngineProfile()
        self.profile.setHttpUserAgent(self.headers['User-Agent'])
        self.profile.setHttpAcceptLanguage(self.headers['Accept-Language'])
        self.profile.setPersistentCookiesPolicy(QWebEngineProfile.AllowPersistentCookies)

        # Create the browser page and view
        self.page = QWebEnginePage(self.profile)
        self.browser = QWebEngineView()
        self.browser.setPage(self.page)

        # Enhance browser settings to mimic Firefox
        settings = self.page.settings()
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebGLEnabled, True)
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, False)  # Firefox often disables plugins by default
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, True)
        # Mimic Firefox's canvas and WebGL fingerprint (approximation)
        settings.setAttribute(QWebEngineSettings.ShowScrollBars, True)

        # Load the Quizlet login page for manual login
        self.login_url = "https://quizlet.com/"
        self.target_url = "https://quizlet.com/783834328/toefl-beginner-activities-and-hobbies-vocabulary-set-2-flash-cards/"
        self.browser.setUrl(QUrl(self.login_url))

        # Simulate human-like behavior
        self.simulate_human_behavior()

        # Set up buttons
        self.scrape_button = QPushButton("Scrape Data")
        self.scrape_button.clicked.connect(self.scrape_data)

        self.refresh_button = QPushButton("Refresh Page")
        self.refresh_button.clicked.connect(self.refresh_page)

        # Set up layout
        layout = QVBoxLayout()
        layout.addWidget(self.browser)
        layout.addWidget(self.scrape_button)
        layout.addWidget(self.refresh_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Variable to store cookies after login
        self.cookies = None

        # Connect to cookie signal to capture cookies after login
        self.profile.cookieStore().cookieAdded.connect(self.on_cookie_added)

    def on_cookie_added(self, cookie):
        # Capture cookies after login
        if not self.cookies:
            self.cookies = {}
        cookie_name = cookie.name().data().decode('utf-8')
        cookie_value = cookie.value().data().decode('utf-8')
        self.cookies[cookie_name] = cookie_value
        print(f"Captured cookie: {cookie_name}={cookie_value}")

    def simulate_human_behavior(self):
        # Simulate scrolling to mimic human behavior
        self.page.runJavaScript("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(1, 3))
        self.page.runJavaScript("window.scrollTo(0, 0);")
        # Simulate random mouse movement (basic approximation)
        self.page.runJavaScript("document.dispatchEvent(new Event('mousemove'));")
        print("Simulated human behavior (scrolling and mouse movement).")

    def refresh_page(self):
        # Reload the current page
        self.browser.reload()
        time.sleep(random.uniform(1, 2))  # Add a small random delay to mimic human behavior
        self.simulate_human_behavior()  # Simulate behavior after refresh
        print("Page refreshed.")

    def scrape_data(self):
        if not self.cookies:
            print("Please log in first to scrape data.")
            return

        # Update session cookies
        self.session.cookies.update(self.cookies)

        # Scrape the target page
        try:
            # Add random delay to mimic human behavior
            time.sleep(random.uniform(1, 3))

            response = self.session.get(self.target_url)
            if response.status_code != 200:
                print(f"Failed to access page: {response.status_code}")
                return

            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract flashcards
            flashcards = soup.find_all('div', class_='SetPageTerm-content')
            lesson_data = []

            for card in flashcards:
                try:
                    terms = card.find_all('span', class_='TermText')
                    if len(terms) >= 2:
                        word = terms[0].text.strip()
                        definition = terms[1].text.strip()
                        lesson_data.append({
                            'word': word,
                            'definition': definition
                        })
                except (AttributeError, IndexError):
                    continue

            print(f"Extracted {len(lesson_data)} terms from {self.target_url}")

            # Save to CSV
            with open('toefl_vocabulary.csv', 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=['word', 'definition'])
                writer.writeheader()
                for item in lesson_data:
                    writer.writerow({
                        'word': item['word'],
                        'definition': item['definition']
                    })

            print("Data saved to toefl_vocabulary.csv")

        except Exception as e:
            print(f"Error during scraping: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CustomBrowser()
    window.show()
    sys.exit(app.exec_())