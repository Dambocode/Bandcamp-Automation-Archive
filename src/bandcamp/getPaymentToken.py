import requests
import json

def getPaymentToken(session, payment_data, task):
    spreedly_env_token = payment_data["spreedly_env_token"]
    
    headers = {
        "content-Type": "application/json",
        "spreedly-environment-key": spreedly_env_token,
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
    }

    data = {
        "environment_key": spreedly_env_token,
        "payment_method": {
            "credit_card": {
                "country": "US",
                "full_name": task["shipping_name"],
                "month": task["card_exp_month"],
                "number": task["card_number"],
                "verification_value": task["card_cvv"],
                "year": task["card_exp_year"],
                "zip": task["shipping_zip"]
            }
        }
    }

    response = session.post(
        "https://core.spreedly.com/v1/payment_methods/restricted.json?from=iframe&v=1.87", data=json.dumps(data), headers=headers)

    # print(response.text)
    # print(response.status_code)

    return response
