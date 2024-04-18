import requests
import urllib.parse

# startCheckout will start the checkout process.


def startCheckout(session, task, album):
    # Variables
    subdomain = task['subdomain']

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
    }

    query = {
        "client_id": session.cookies.get_dict()['client_id'],
        "from": "dialog",
        "return_url": urllib.parse.quote(f"https://{subdomain}.bandcamp.com{album}"),
        "local_timezone": "America/New_York",
        "payment_pref": task["payment_pref"]
    }
    response = session.get(f'https://bandcamp.com/cart/checkout_start', params=query, headers=headers, allow_redirects=False, proxies=session.proxies)

    return response, session
