import requests
import json
def checkStock(task, product_data):

    url = f"https://{task['subdomain']}.bandcamp.com/api/merch/2/inventory?merch_id="

    for product in product_data["products"]:
        if product["availability"] != "OnlineOnly":
            url = url + str(product["item_id"]) + ","



    response = requests.get(url)
    if response.status_code == 200:
        return json.loads(response.text)