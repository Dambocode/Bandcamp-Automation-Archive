import requests

from src.utils import logResponse

# addToCart will add the item to the cart.


def addToCart(session, product, band_id, task):

    if task["fan_id"]:
        fan_id = task["fan_id"]
    else:
        fan_id = ""

    # Variables
    subdomain = task['subdomain']

    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    query = {
        "req": "add",
        "item_type": product["item_type"],
        "item_id": product["item_id"],
        "unit_price": product["price"],
        "quantity": task['qty'],
        "band_id": band_id,
        "ip_country_code": "US",
        "fan_id": fan_id,
        "client_id": session.cookies.get_dict()['client_id'],
        "sync_num": "1"
    }
    response = session.post(f'https://{subdomain}.bandcamp.com/cart/cb', params=query, headers=headers)
    
    # logResponse.logResponse("addToCart", response)
    
    return response, session
