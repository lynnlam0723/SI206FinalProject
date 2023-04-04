import requests
from bs4 import BeautifulSoup

# get the response from the URL
url = "https://www.fda.gov/food/food-labeling-nutrition/nutrition-information-raw-vegetables"
resp = requests.get(url)

# create the soup object
soup = BeautifulSoup(resp.content, 'html.parser')