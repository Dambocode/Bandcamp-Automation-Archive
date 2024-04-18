import requests

from src.utils import logResponse

# addToCart will add the item to the cart.


def removeFromCart(session, product, task):

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
        "req": "del",
        "id": product["item_id"],
        "client_id": session.cookies.get_dict()['client_id'],
        "sync_num": "2"
    }
    response = session.post(f'https://{subdomain}.bandcamp.com/cart/cb', params=query, headers=headers)
    
    # logResponse.logResponse("addToCart", response)
    
    return response, session
