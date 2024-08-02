import requests
from bs4 import BeautifulSoup as bs
import logging

class Authenticator:
    def __init__(self, login_url, credentials):
        self.login_url = login_url
        self.credentials = credentials
    
    # get the login page to retrieve viewstate info which is unique to each session
    def login(self):

        session = requests.Session()

        response = session.get(self.login_url)
        soup = bs(response.text, 'html.parser')

        viewstate = soup.find("input", {'name': '__VIEWSTATE'})['value']
        viewstategenerator = soup.find("input", {'name': '__VIEWSTATEGENERATOR'})['value']

        payload = {
            '__VIEWSTATE': viewstate,
            '__VIEWSTATEGENERATOR': viewstategenerator,
            'fragment-7717_action': 'login',
            'fragment-7717_provider': '',
            'fragment-7717_username': self.credentials['username'],
            'fragment-7717_password': self.credentials['password'],
            'fragment-7717_rememberMe': 'on'
        }

        response = session.post(self.login_url, data=payload)
        if response == self.login_url:
            logging.error("Login failed")
            return None
        logging.info("Login successful")
        return session

