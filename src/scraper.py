import time
from bs4 import BeautifulSoup as bs
import logging

class Scraper:
    def __init__(self, session, config):
        self.session = session
        self.config = config
    
    def crawl_hierarchy(self, url):
        response = self.session.get(url)
        if response.status_code != 200:
            logging.error(f"Failed to access page {url}. Status code: {response.status_code}")
            return
        
        soup = bs(response.text, 'html.parser')

        hierarchy_items = soup.find_all('a', class_=['hierarchy-item with-children', 'hierarchy-item without-children'])

        # !!! this is recursive, remember to prevent it from scraping everything during testing!!!
        for item in hierarchy_items:
            if 'with-children' in item['class']:
                child_url = self.config['urls']['base'] + item['href']
                logging.info(f"Crawling child hierarchy: {child_url}")
                self.crawl_hierarchy(child_url)
            else:
                leaf_url = self.config['urls']['base'] + item['href']
                logging.info(f"Scraping leaf page: {leaf_url}")
                self.scrape_leaf_page(leaf_url)
            
            time.sleep(self.config['scraping']['delay'])

    def scrape_leaf_page(self, url):
        response = self.session.get(url)
        if response.status_code != 200:
            logging.error(f"Failed to access leaf page. Status code: {response.status_code}")
            return None
        
        soup = bs(response.text, 'html.parser')

        # scraping logic goes here

        logging.info(f"Successfully scraped data from {url}")

        return None
    
    def start_scraping(self):
        start_url = self.config['urls']['secure']
        self.crawl_hierarchy(start_url)