import requests
import json
import time

from src.utils import cliLogger

def getPaymentToken(task):
    
    headers = {
        "content-Type": "application/json",
        "spreedly-environment-key": "A99s7SaswUW4CdYdV7oO52cA6CU",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
    }

    data = {
        "environment_key": "A99s7SaswUW4CdYdV7oO52cA6CU",
        "payment_method": {
            "credit_card": {
                "country": "US",
                "full_name": task["name"],
                "month": task["card_exp_month"],
                "number": task["card_num"],
                "verification_value": task["card_cvv"],
                "year": task["card_exp_year"],
                "zip": task["zip_code"]
            }
        }
    }
   

    payment_token = None
    while payment_token is None:
        try:
            response = requests.post("https://core.spreedly.com/v1/payment_methods/restricted.json?from=iframe&v=1.87", json=data, headers=headers)
            payment_token = json.loads(response.text)["transaction"]["payment_method"]["token"]
            cliLogger.cliLogger("Got Payment Token", task)
            return payment_token
        except Exception as e:
            cliLogger.cliLogger("Error Generating Payment Token: " + str(e), task, "error")
            time.sleep(float(task["retry_delay"]) / 1000)
            pass


    
