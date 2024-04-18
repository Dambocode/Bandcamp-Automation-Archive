import requests
import urllib.parse

from src.utils import logResponse
# startCheckout will start the checkout process.


def startPayment(session, start_payment_response):
    url = start_payment_response.headers['Location']

    response = session.get(url, proxies=session.proxies)

    return response, session
