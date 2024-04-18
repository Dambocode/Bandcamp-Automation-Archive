

import requests
import urllib.parse

# startCheckout will start the checkout process.


def getPaypal(session, request_params):
    

    response = session.get(f'https://bandcamp.com/cart/checkout_continue' + request_params, allow_redirects=False, proxies=session.proxies)
    return response, session
