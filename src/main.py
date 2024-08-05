import logging
from scraper import Scraper
from auth import Authenticator
from utils import load_config
import os
import sys
from playwright.sync_api import sync_playwright

def main():

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(project_root)

    log_dir= os.path.join(project_root, 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_file = os.path.join(log_dir, 'scraper.log')
    logging.basicConfig(filename=log_file, level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    config_path = os.path.join(project_root, 'config', 'config.yaml')
    config = load_config(config_path)
    
    with sync_playwright() as playwright:
        scraper = Scraper(config, playwright)
        try:
            scraper.login()
            ready = True
            if not ready:
                print("Disable fully recursive scraping first!")
                return
            scraper.start_scraping()
        
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
        
        finally:
            scraper.close()

if __name__ == "__main__":
    main()