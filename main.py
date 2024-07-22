import requests
import creds
from bs4 import BeautifulSoup as bs

base_url = 'https://www.guildsomm.com/'
login_url = f"{base_url}login"

# get the login page to retrieve viewstate info which is unique to each session
session = requests.Session()
response = session.get(login_url)
soup = bs(response.text, "html.parser")
viewstate = soup.find("input", {'name': '__VIEWSTATE'})['value']
viewstategenerator = soup.find("input", {'name': '__VIEWSTATEGENERATOR'})['value']

payload = {
    '__VIEWSTATE': viewstate,
    '__VIEWSTATEGENERATOR': viewstategenerator,
    'fragment-7717_action': 'login',
    'fragment-7717_provider': '',
    'fragment-7717_username': creds.username,
    'fragment-7717_password': creds.password,
    'fragment-7717_rememberMe': 'on'
}

response = session.post(login_url, data=payload)
print(response.status_code)
print(response.url)