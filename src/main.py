import logging
from scraper import Scraper
from auth import Authenticator
from utils import load_config
import os
import sys

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

    auth = Authenticator(config['urls']['login'], config['credentials'])
    session = auth.login()
    
    scraper = Scraper(session, config)

    ready = True
    if not ready:
        print("Disable fully recursive scraping first!")
        return
    scraper.start_scraping()

    print(data)

    # get the login page to retrieve viewstate info which is unique to each session
    # session = requests.Session()
    # response = session.get(login_url)
    # soup = bs(response.text, "html.parser")
    # viewstate = soup.find("input", {'name': '__VIEWSTATE'})['value']
    # viewstategenerator = soup.find("input", {'name': '__VIEWSTATEGENERATOR'})['value']

    # payload = {
    #     '__VIEWSTATE': viewstate,
    #     '__VIEWSTATEGENERATOR': viewstategenerator,
    #     'fragment-7717_action': 'login',
    #     'fragment-7717_provider': '',
    #     'fragment-7717_username': creds.username,
    #     'fragment-7717_password': creds.password,
    #     'fragment-7717_rememberMe': 'on'
    # }

    # response = session.post(login_url, data=payload)
    # print(response.status_code)
    # print(response.url)

if __name__ == "__main__":
    main()