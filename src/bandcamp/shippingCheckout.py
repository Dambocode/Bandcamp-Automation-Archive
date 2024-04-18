

import requests
import urllib.parse

# startCheckout will start the checkout process.


def shippingCheckout(session, task, url, cart_id, album, collected_address=False):
    # Variables
    query = {}
    # url = "https://bandcamp.com/cart/checkout_shipping_address?cart_id=90554943&orig=&previous_step=1&sig=df5c69a562ac354cbd16a08b08ff6371&timezone_sym_id=1"
    params = url.split("?")[1]
    params = params.split("&")
    for param in params:
        param = param.split("=")
        query[param[0]] = param[1]

    query["return_url"] = urllib.parse.quote(f'https://{task["subdomain"]}.bandcamp.com{album}')

    if collected_address:
        query["collected_address"] = True


    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
    }

    response = session.get(f'https://bandcamp.com/cart/checkout_shipping_address',
                           params=query, headers=headers, allow_redirects=False, proxies=session.proxies)
    return response, session
