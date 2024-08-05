import time
import random
from bs4 import BeautifulSoup as bs
import logging
from playwright.sync_api import sync_playwright

class Scraper:
    def __init__(self, config):
        self.config = config
        self.playwright= sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
    
    def login(self):
        self.page.goto(self.config['urls']['login'])
        self.page.fill('input[name="username"]', self.config['credentials']['username'])
        self.page.fill('input[name="password]', self.config['credentials']['password'])
        self.page.click('button[type="submit"]')
        self.page.wait_for_load_state('networkidle')
    
    def crawl_hierarchy(self, url):
        self.page.goto(url)
        self.page.wait_for_load_state('networkidle')

        hierarchy_items = self.page.query_selector_all('a.hierarchy-item')

        # !!! this is recursive, remember to prevent it from scraping everything during testing!!!
        counter = 0
        for item in hierarchy_items:
            if 'with-children' in item.get_attribute('class'):
                child_url = item.get_attribute('href')
                logging.info(f"Crawling child hierarchy: {child_url}")
                self.crawl_hierarchy(child_url)
            else:
                leaf_url = item.get_attribute('href')
                logging.info(f"Scraping leaf page: {leaf_url}")
                self.scrape_leaf_page(leaf_url)
            
            self.random_delay()

            # temporary for testing
            counter = counter + 1
            if counter > 10:
                break

    def scrape_leaf_page(self, url):
        self.page.goto(url)
        self.page.wait_for_load_state('networkidle')
        html_content = self.page.content()
        soup = bs(html_content, 'html.parser')

        # scraping logic goes here
        print(soup)

        logging.info(f"Successfully scraped data from {url}")

        return None
    
    def start_scraping(self):
        start_url = self.config['urls']['secure']
        self.crawl_hierarchy(start_url)
    
    def random_delay(self):
        delay = random.uniform(self.config['scraping']['min_delay'],
                               self.config['scraping']['max_delay'])
        time.sleep(delay)