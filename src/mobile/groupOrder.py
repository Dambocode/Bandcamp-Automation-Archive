import time
import hmac
import hashlib
import requests
import numpy as np
import json
import urllib.parse

from src.utils import cliLogger

from src.mobile import getPaymentToken


def zero_fill_right_shift(val, n):
    return (val >> n) if val >= 0 else ((val + 0x100000000) >> n)


def calculatePow(body, payload):
    s1 = ""
    i1 = 0
    while s1 == "":
        num = np.base_repr(i1, 36).lower()
        digest = hashlib.sha1((body + payload + num).encode('utf-8')).digest()

        i2 = 0
        i3 = 0
        while True:
            if i3 < len(digest):
                i4 = 0
                if digest[i3] < 0:
                    i4 = 0
                elif digest[i3] < 1:
                    i4 = 8
                elif digest[i3] < 2:
                    i4 = 7
                elif digest[i3] < 4:
                    i4 = 6
                elif digest[i3] < 8:
                    i4 = 5
                elif digest[i3] < 16:
                    i4 = 4
                elif digest[i3] < 32:
                    i4 = 3
                elif digest[i3] < 64:
                    i4 = 2
                elif digest[i3] < 128:
                    i4 = 1

                i2 = i2 + i4
                if i4 == 8:
                    i3 += 1
                    continue

            if i2 >= 10:
                s1 = num
            i1 += 1
            break

    return s1


def byteSwap(digest_bytes):
    cArr = [None] * (len(digest_bytes) * 2)
    i = 0
    while i < len(digest_bytes):
        i2 = i * 2
        cArr2 = list("0123456789abcdef")
        cArr[i2] = cArr2[zero_fill_right_shift((digest_bytes[i] & 240), 4)]
        cArr[i2 + 1] = cArr2[digest_bytes[i] & 15]
        i += 1
    return ''.join(cArr)


def hash(dm, key):
    key = bytes(key, "UTF-8")
    message = bytes(dm, "UTF-8")
    digester = hmac.new(key, message, hashlib.sha1)
    signature = digester.digest()
    return byteSwap(signature)


def groupOrder(session, task, bootstrap_response, access_token, product_details):
    # product = json.loads(product)["merch"][0]
    # payment_token = getPaymentToken.getPaymentToken(session, task)

    dm = bootstrap_response.headers["x-bandcamp-dm"]

    product_data = product_details["merch"][0]

    BODY = {
        "items": [
            {
                "quantity": 1,
                "item_type": "p",
                "download_id": product_data["download_id"],
                "download_type": product_data["download_type"],
                "unit_price": {
                    "amount": product_data["price"] * 100,
                    "currency": product_data["currency"]
                },
                "item_id": product_data["id"]
            }
        ],
        "client_prefs": {
            "country_code": "US"
        },
        "currency": "USD"
    }

    json_string = json.dumps(BODY)
    dm = dm[:19] + dm[22:]
    
    
    while True:

        bandcamDM = hash(f"{dm}{json_string}", "dtmfa")

        url = "https://bandcamp.com/api/checkout/1/group_orders"

        headers = {
            "host": "bandcamp.com",
            "accept": "*/*",
            "x-bandcamp-dm": bandcamDM,
            "user-agent": "Bandcamp/218977 CFNetwork/1335.0.3 Darwin/21.6.0",
            "connection": "keep-alive",
            "accept-language": "en-US,en;q=0.9",
            "authorization": f"Bearer {access_token}",
            "content-type": "application/json"
        }

        response = session.request("POST", url, data=json_string, headers=headers)

        cliLogger.cliLogger("Submitting Order", task)

        if response.text == '{"__api_special__":"exception","error_type":"CheckoutClient::SoldOutError"}':
            cliLogger.cliLogger("Waiting For Restock", task, "error")
            time.sleep(task["retry_delay"])
        else:
            return json.loads(response.text)
    