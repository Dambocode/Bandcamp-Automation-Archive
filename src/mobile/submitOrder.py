import time
import hmac
import hashlib
import requests
import numpy as np
import json
import urllib.parse

from src.utils import cliLogger



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


def submitOrder(session, task, bootstrap_response, access_token, shipping_data, paymentToken, product_details, order_data):

    print(order_data)

    try:
        dm = bootstrap_response.headers["x-bandcamp-dm"]

        product_data = product_details["merch"][0]

        # BODY = '{"items":[{"quantity":1,"item_type":"p","shipping_address":{"street":"1 main st","city":"Stugattsville","country":"United States","signature":"ilSZSY4iMKThIbAE03fKwRjzT6g=","address_id":15815533,"country_code":"US","zip":"11111","street_2":"","name":"Stew Gatts","state":"NY"},"display":{"item_title":"Limited Edition Clear Vinyl","tax":{"amount":0,"currency":"GBP"},"shipping":{"amount":0,"currency":"GBP"},"total":{"amount":2500,"currency":"GBP"},"item_id":3999519273,"sub_total":{"amount":2500,"currency":"GBP"},"converted_totals":{},"preorder":false,"currency":"GBP","artist_name":"YUNGMORPHEUS & THERAVADA"},"package_info":{"id":3999519273,"type_id":2,"image_id":29992288,"type_display":"Vinyl LP"},"download_id":725746560,"download_type":"a","unit_price":{"amount":2500,"currency":"GBP"},"item_id":3999519273}],"payment":{"country_code":"US","save_card":false,"token":"GPGk0OwQkcXjDQraVKEIHwsKc5Z"},"total":{"amount":3300,"currency":"GBP"},"buyer":{"email":"","currency":"","lastname":"","firstname":"John+Smith"},"referrer_code":"iasearch","notification_prefs":{"label":false,"band":false}}'

        BODY = {
            "items": [
                {
                    "quantity": 1,
                    "item_type": "p",
                    "shipping_address": {
                        "street": task["address_1"],
                        "city": task["city"],
                        "country": "United States",
                        "signature": shipping_data["address_id_sig"],
                        "address_id": shipping_data["address_id"],
                        "country_code": "US",
                        "zip": task["zip_code"],
                        "street_2": task["address_2"],
                        "name": task["name"],
                        "state": task["state"]
                    },
                    "display": {
                        "item_title": product_data["title"],
                        "tax": {
                            "amount": order_data["orders"][0]["totals"]["tax"]["amount"],
                            "currency": order_data["orders"][0]["totals"]["tax"]["currency"]
                        },
                        "shipping": {
                            "amount": order_data["orders"][0]["totals"]["shipping"]["amount"],
                            "currency": order_data["orders"][0]["totals"]["shipping"]["currency"]
                        },
                        "total": {
                            "amount": order_data["orders"][0]["totals"]["total"]["amount"],
                            "currency": order_data["orders"][0]["totals"]["total"]["currency"]
                        },
                        "item_id": product_data["id"],
                        "sub_total": {
                            "amount": order_data["orders"][0]["totals"]["sub_total"]["amount"],
                            "currency": order_data["orders"][0]["totals"]["sub_total"]["currency"]
                        },
                        "converted_totals": {},
                        "preorder": order_data["orders"][0]["items"][0]["display"]["preorder"],
                        "currency": order_data["orders"][0]["items"][0]["display"]["currency"],
                        "artist_name": order_data["orders"][0]["items"][0]["display"]["artist_name"]
                    },
                    "package_info": {
                        "id": product_data["id"],
                        "type_id": product_data["type_id"],
                        "image_id": product_data["arts"][0]["image_id"],
                        "type_display": product_data["type_name"]
                    },
                    "download_id": product_data["download_id"],
                    "download_type": product_data["download_type"],
                    "unit_price": {
                        "amount": order_data["orders"][0]["totals"]["sub_total"]["amount"],
                        "currency": order_data["orders"][0]["totals"]["sub_total"]["currency"]
                    },
                    "item_id": product_data["id"]
                }
            ],
            "payment": {
                "country_code": "US",
                "save_card": False,
                "token": paymentToken
            },
            "total": {
                "amount": order_data["orders"][0]["totals"]["total"]["amount"],
                "currency": order_data["orders"][0]["totals"]["total"]["currency"]
            },
            "buyer": {
                "email": "",
                "currency": "",
                "lastname": "",
                "firstname": task["name"].replace(" ", "+")
            },
            "referrer_code": "iasearch",
            "notification_prefs": {
                "label": False,
                "band": False
            }
        }
        
        json_string = json.dumps(BODY)


        dm = dm[:19] + dm[22:]
        bandcamDM = hash(f"{dm}{json_string}", "dtmfa")

        url = "https://bandcamp.com/api/checkout/1/submit_credit_card_order"

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

        response_json = json.loads(response.text)
        task["end_time"] = time.time()


        try:
            if response_json["sale_item_ids"]:
                cliLogger.cliLogger("Successfully Checked Out: " + product_data["title"], task, "success")
                return response_json
        except:
                cliLogger.cliLogger("Checkout Error: " + response_json["error_type"], task, "error")
            
        
    except Exception as e:
        cliLogger.cliLogger(e, task, "error")
        time.sleep(task["retry_delay"])