import requests
import json
import urllib.parse


def submitOrder(session, task, payment_data, ref_url, payment_token, captcha_token):
    order_total_price = int(payment_data["order"]["totals"]["sub_total"]["amount"]) + int(
        payment_data["order"]["totals"]["tax"]["amount"])
    order_shipping_price = payment_data["order"]["shipping_totals"][0]
    order_currency = payment_data["order"]["totals"]["sub_total"]["currency"]

    # headers = {
    #     "content-Type": "application/x-www-form-urlencoded",
    #     "Referer": ref_url,
    #     "Origin": "https://www.bandcamp.com",
    #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
    # }
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        # Requests sorts cookies= alphabetically
        # 'Cookie': 'client_id=AA2C9F3DE7119FD3FBBD7D232953B9EE1A96D2C4201F9727908D4A37306B15E5; _ga=GA1.2.161706045.1659923743; _gid=GA1.2.921846778.1659923743; BACKENDID3=flexocentral-frnk-3; session=1%09t%3A1659923742%09bp%3A1%09c%3A1; BACKENDID=flexo1central-dfw6-5',
        'Origin': 'https://bandcamp.com',
        "Referer": ref_url,
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }
    print(ref_url)

    data = {
        "save_card": True,
        "signed_params": payment_data["signed_params"].replace("amp;",""),
        "previous_step": 2,
        "totals": [
            {"currency": order_currency, "amount": order_total_price},
            order_shipping_price,
        ],
        "is_zero_dollar_pledge": False,
        "timezone_sym_id": "1",
        "card_vault_token": payment_token,
        "first_name": task["shipping_name"].split(" ")[0],
        "last_name": task["shipping_name"].split(" ")[-1],
        "captcha_token": captcha_token,
        "email_address": task["email"],
        "card_country": "US",
        "card_zip": task["shipping_zip"],
        "checkout_context": {
            "logged_in_state": "not_fan",
            "payments_pref_state": "new",
            "platform": "desktop",
            "checkout_method": "new_card",
            "checkout_pricing": "nyp_nonzero_min",
            "locale": "en",
            "country": "US",
            "aggregation": "all_items",
            "item_type": "all_physical"
        }
    }

    # json.loads(str(data))
    # print(json.dumps(data, indent=4))
    json.dump(data, open("submit_order_bot.json", "w"))
    json.dump(headers, open("submit_order_headers_bot.json", "w"))
    response = session.post(f'https://bandcamp.com/api/payflow/1/checkout',
                            data=json.dumps(data), headers=headers)

    return response, session
