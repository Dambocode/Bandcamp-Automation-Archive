from bs4 import BeautifulSoup
import json


def getCheckoutData(response):
    # Get the albums from the home page.
    soup = BeautifulSoup(response.text, 'html.parser')

    page_data = str(soup.findAll(id='pagedata')[0])
    page_data = page_data.replace("<div data-blob='", "")
    page_data = page_data.replace("' id=", "")
    page_data = page_data.replace('"pagedata"></div>', "")
    # page_data = page_data.replace("\n", "")
    # page_data = page_data.replace("\t", "")
    page_data = json.loads(page_data)


    return page_data

