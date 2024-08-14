import time
import random
from bs4 import BeautifulSoup as bs
import logging
from playwright.sync_api import sync_playwright
import urllib.parse

class Scraper:
    def __init__(self, config, playwright):
        self.config = config
        self.playwright = playwright
        self.browser = self.playwright.chromium.launch(headless=True)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
    
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
    
    def crawl_hierarchy(self, url, parent_url=None, depth = 0):
        print(f"{'  ' * depth}crawling {url} (Parent = {parent_url})")
        self.page.goto(url)
        self.page.wait_for_load_state('networkidle')

        current_item = self.page.query_selector('div.hierarchy-item.selected')
        if not current_item:
            print(f"{'  ' * depth}Cannot find item in hierarchy")
            return
        
        children_container = current_item.query_selector('+ div.hierarchy-children')
        if not children_container:
            print(f"{'  ' * depth}No children found for this page")
            return

        hierarchy_items = self.page.query_selector_all('div.hierarchy-item:not(.selected)')

        if not hierarchy_items:
            print("No hierarchy items found. Printing page content:")
            print(self.page.content())
            return

        print(f"{'  ' * depth}Found {len(hierarchy_items)} items on {url}")
        for index, item in enumerate(hierarchy_items):
            item_html = item.evaluate('(element) => element.outerHTML')
            print(f"{'  ' * depth}Item {index}: {item_html}")


        # !!! this is recursive, remember to prevent it from scraping everything during testing!!!
        self.random_delay()

        for item in hierarchy_items:
            # item_html= item.evaluate('(element) => element.outerHTML')
            # print(f"item: {item_html}")

            link = item.query_selector('a')
            if link:
                link_html = link.evaluate('(element) => element.outerHTML')
                print(f"link: {link_html}")

                href = link.get_attribute('href')
                if href is None:
                    print(f"Empty href for {item}")
                    continue

                normalized_href = self.normalize_url(href)
                if normalized_href == parent_url:
                    print(f"{'  ' * depth}Skipping parent URL {normalized_href}")
                    continue

                title = link.inner_text()
                item_class = item.get_attribute('class')

                print(f"{'  ' * depth}Title: {title}")
                print(f"{'  ' * depth}Original URL: {href}")
                print(f"{'  ' * depth}Normalised URL: {normalized_href}")

                if 'with-children' in item_class:
                    expand_collapse = link.query_selector('span.expand-collapse')
                    if expand_collapse and 'collapsed' in expand_collapse.get_attribute('class'):
                        print(f"{'  ' * depth}Expanding: {title}")
                        expand_collapse.click()
                        self.page.wait_for_load_state('networkidle')

                    print(f"{'  ' * depth}Crawling child hierarchy: {normalized_href}")
                    self.crawl_hierarchy(normalized_href)
                else:
                    print(f"{'  ' * depth}Scraping leaf page: {normalized_href}")
                    self.scrape_leaf_page(normalized_href)
            else:
                print(f"{'  ' * depth}No link for item {item}")

        if parent_url:
            print(f"{'  ' * depth}Returning to parent URL {parent_url}")
            self.page.goto(parent_url)
            self.page.wait_for_load_state('networkidle')

    def scrape_leaf_page(self, url):
        self.random_delay()
        self.page.goto(url)
        self.page.wait_for_load_state('networkidle')
        html_content = self.page.content()
        soup = bs(html_content, 'html.parser')

        # scraping logic goes here
        print(soup)

        logging.info(f"Successfully scraped data from {url}")

        return None
    
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
            raise
    
    def random_delay(self):
        delay = random.uniform(self.config['scraping']['min_delay'],
                               self.config['scraping']['max_delay'])
        time.sleep(delay)
    
    def close(self):
        print("closing")
        self.context.close()
        self.browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop()