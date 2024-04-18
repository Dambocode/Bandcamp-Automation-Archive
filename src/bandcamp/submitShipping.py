import requests
import json
import urllib.parse


def submitShipping(session, task, checkout_data, ref_url):

    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://bandcamp.com",
        "Referer": ref_url
    }

    data = {
        "sale_ids": checkout_data["sale_ids"],
        "cart_id": f'{checkout_data["cart_id"]}',
        "sig": urllib.parse.unquote(checkout_data["cart_sig"].split("sig=")[1]),
        "shipping_name": task["shipping_name"],
        "shipping_street": task["shipping_address"],
        "shipping_city": task["shipping_city"],
        "shipping_state": task["shipping_state"],
        "shipping_zip": task["shipping_zip"],
        "shipping_country_code": task["shipping_country"],
        "from": "checkout_start"
    }

    response = session.post(f'https://bandcamp.com/api/addresses/1/add_to_items',
                            data=json.dumps(data), headers=headers, proxies=session.proxies)
    return response, session
