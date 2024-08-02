import time
from bs4 import BeautifulSoup as bs
import logging

class Scraper:
    def __init__(self, session, config):
        self.session = session
        self.config = config

    def scrape_secure_page(self):
        url = self.config['urls']['secure']
        response = self.session.get(url)

        if response.status_code != 200:
            logging.error(f"Failed to access secure page. Status code: {response.status_code}")
            return None
        
        # scraping logic here
        soup = bs(response.text, 'html.parser')

        data = soup.find_all(class_='hierarchy-item with-children')
        time.sleep(self.config['scraping']['delay'])

        return data