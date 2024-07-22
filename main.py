import requests
import creds
from bs4 import BeautifulSoup as bs

base_url = 'https://www.guildsomm.com/'
login_url = f"{base_url}login"

result = requests.get(base_url)
doc = bs(result.text, "html.parser")

print(doc)