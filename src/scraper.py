import time
import random
from bs4 import BeautifulSoup as bs
import logging
from playwright.sync_api import sync_playwright
import urllib.parse
from requests.exceptions import RequestException
from collections import deque

class Scraper:
    def __init__(self, config, playwright):
        self.config = config
        self.playwright = playwright
        self.browser = self.playwright.chromium.launch(headless=True)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        self.visited_urls = set()
        self.max_retries = self.config['settings']['max_retries']
    
    def login(self):
        print("starting login")
        login_url = self.config['urls']['login']
        self.page.goto(login_url)
        self.page.wait_for_load_state('networkidle')

        html_content = self.page.content()
        soup = bs(html_content, 'html.parser')

        viewstate = soup.find("input", {'name': '__VIEWSTATE'})['value']
        viewstategenerator = soup.find("input", {'name': '__VIEWSTATEGENERATOR'})['value']
        self.page.fill('input[name="fragment-7717_username"]', self.config['credentials']['username'])
        self.page.fill('input[name="fragment-7717_password"]', self.config['credentials']['password'])
        self.page.evaluate(f"""
            document.querySelector('input[name="__VIEWSTATE"]').value = '{viewstate}';
            document.querySelector('input[name="__VIEWSTATEGENERATOR"]').value = '{viewstategenerator}';
            document.querySelector('input[name="fragment-7717_action"]').value = 'login';
            document.querySelector('input[name="fragment-7717_provider"]').value = '';
            document.querySelector('input[name="fragment-7717_rememberMe"]').checked = true;
        """)

        submit_button = self.page.query_selector('a.internal-link.login.submit-button.button')
        if submit_button:
            submit_button.click()
        else:
            logging.error("Submit button not found")
            logging.info({self.page.content})
            raise Exception("Login failed, submit button not found")

        self.page.wait_for_load_state('networkidle')

        if self.is_login_successful():
            logging.info("Login Successful")
        else:
            logging.error("Login failed: Invalid Credentials")
            raise Exception("Login failed: Invalid Credentials")
    
    def crawl_hierarchy(self, start_url):
        queue = deque([(start_url, 0)]) # (url, depth)

        while queue:
            url, depth = queue.popleft()

            if url in self.visited_urls:
                print(f"{'  ' * depth}Already visited {url}, skipping")
                continue

            print(f"{'  ' * depth}Crawling {url}")

            for attempt in range(self.max_retries):
                try:
                    self.random_delay()
                    self.page.goto(url)
                    self.page.wait_for_load_state('networkidle')
                    self.visited_urls.add(url)
                    break
                except Exception as e:
                    if attempt < self.max_retries - 1:
                        wait_time = 2 ** attempt
                        print(f"Retrying crawl for {url}")
                        time.sleep(wait_time)
                        continue
                else:
                    print(f"Max retries for {url} reached, skipping")
                    logging.error(f"Error {str(e)}, failed to crawl {url} after max attempts")
                    continue

            current_item = self.page.query_selector('div.hierarchy-item.selected')
            if not current_item:
                print(f"{'  ' * depth}Cannot find item in hierarchy")
                continue
        
            children_container = current_item.query_selector('+ div.hierarchy-children')
            if not children_container:
                print(f"{'  ' * depth}No children found for this page")
                self.scrape_leaf_page(url)
                continue

            hierarchy_items = children_container.query_selector_all('> ul.hierarchy-list > li > div.hierarchy-item')
        
            if not hierarchy_items:
                print("No hierarchy items found.")
                # print(self.page.content())
                continue

            print(f"{'  ' * depth}Found {len(hierarchy_items)} items on {url}")

            for item in (hierarchy_items):
                link = item.query_selector('a')
                if not link:
                    print(f"{'  ' * depth}No link for {item}")
                    continue
                
                href = link.get_attribute('href')
                if href is None:
                    print(f"{'  ' * depth}Empty href for {item}")
                    continue

                normalized_href = self.normalize_url(href)
                title = link.inner_text()

                print(f"{'  ' * depth}Title: {title}")
                print(f"{'  ' * depth}Original URL: {href}")
                print(f"{'  ' * depth}Normalised URL: {normalized_href}")
                
                queue.append((normalized_href, depth + 1))

    
    # the server seems to be quite unreliable, created this for robustness
    def crawl_with_retry(self, url):
        for attempt in range(self.max_retries):
            try:
                return self.crawl_hierarchy(url)
            except Exception as e:
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"Retrying crawl for {url}")
                    time.sleep(wait_time)
                else:
                    print(f"Max retries for {url} reached, skipping")
                    logging.error(f"Error {str(e)}, failed to crawl {url} after max attempts")
        return None

    def scrape_leaf_page(self, url):
        self.random_delay()
        self.page.goto(url)
        self.page.wait_for_load_state('networkidle')
        html_content = self.page.content()
        soup = bs(html_content, 'html.parser')

        # scraping logic goes here
        print("scrape_leaf_page() called")

        logging.info(f"Successfully scraped data from {url}")

        return None
    
    def scrape_with_retry(self, url):
        try:
            for attempt in range(self.max_retries):
                return self.scrape_leaf_page(url)
        except Exception as e:
            if attempt < self.max_retries - 1:
                wait_time = 2 ** attempt
                print(f"Retrying scrape for {url}")
                time.sleep(wait_time)
            else:
                print(f"Failed to scrape {url} after max retries")
                logging.error(f"Error occurred while scraping {url}: {str(e)}")
        
        return False

    def is_login_successful(self):
        print("checking login success")
        TARGET_PAGE_ERROR = "Invalid Credentials"
        if TARGET_PAGE_ERROR in self.page.content():
            return False    
        else:
            return True
        
    def normalize_url(self, href_string):
        if href_string.startswith('http'):
            return href_string
        elif href_string.startswith('//'):
            return 'https:' + href_string
        elif href_string.startswith('/'):
            return urllib.parse.urljoin(self.config['urls']['base'], href_string)
        else:
            return urllib.parse.urljoin(self.config['urls']['base'] + '/', href_string)
    
    def start_scraping(self):
        try:
            self.login()
            start_url = self.config['urls']['secure']
            print("starting scraping")
            self.crawl_hierarchy(start_url)
        except Exception as e:
            logging.error(f"Scraping error {str(e)}")
        finally:
            print("Visited URLs:")
            for url in self.visited_urls:
                print(url)
    
    def random_delay(self):
        delay = random.uniform(self.config['settings']['min_delay'],
                               self.config['settings']['max_delay'])
        time.sleep(delay)
    
    def close(self):
        print("closing")
        self.context.close()
        self.browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop()