from bs4 import BeautifulSoup
import json


def getPlaceOrderData(response):

    # Get the albums from the home page.
    soup = BeautifulSoup(response.text, 'html.parser')

    page_data = str(soup.findAll(id='checkout')[0])
    page_data = page_data.split('" id="checkout')[0]
    page_data = page_data.split('data-blob="')[1]
    page_data = page_data.replace('&quot;', '"')
    page_data = json.loads(page_data)

    
    return page_data

