import time
import json

from src.utils import cliLogger


def saveShippingDetails(session, task):
    
    shipping_data = {}

    # Get Address ID from api/shipping_address/1/establish
    url = "https://bandcamp.com/api/shipping_address/1/establish"

    data = {
        "shipping_name": str(task["name"]),
        "shipping_street": str(task["address_1"]),
        "shipping_street_2": str(task["address_2"]),
        "shipping_city": str(task["city"]),
        "shipping_state": str(task["state"]),
        "shipping_zip": str(task["zip_code"]),
        "shipping_country_code": str(task["country"]),
        "save_shipping_address": True,
        "from": "mobile_address_form"
    }

    while True:
        try:
            response = session.post(url, json=data)
            if response.status_code == 200:
                break
            else:
                cliLogger.cliLogger(response.status_code, task, "error")
                time.sleep(float(task["retry_delay"]) / 1000)
        except Exception as e:
            cliLogger.cliLogger(e, task, "error")
            time.sleep(float(task["retry_delay"]) / 1000)
        
    shipping_data["address_id"] = json.loads(response.text)["address_id"]
    shipping_data["address_id_sig"] = json.loads(response.text)["address_info_params_sig"]

    # Save Address ID to Account from api/mobile/25/save_default_shipping_address
    url = "https://bandcamp.com/api/mobile/25/save_default_shipping_address"

    data = {
        "address_id": json.loads(response.text)["address_id"],
        "address_id_sig": json.loads(response.text)["address_info_params_sig"]
    }

    while True:
        try:
            response = session.post(url, json=data)
            if response.status_code == 200:
                cliLogger.cliLogger("Saved Shipping Information", task, "alert")
                break
            else:
                cliLogger.cliLogger(response.status_code, task, "error")
                time.sleep(float(task["retry_delay"]) / 1000)
        except Exception as e:
            cliLogger.cliLogger(e, task, "error")
            time.sleep(float(task["retry_delay"]) / 1000)
        
    return shipping_data, session