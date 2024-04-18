from src.utils import cliLogger
import time
import json

def getProductDetails(session, task, product):
    product_details = None
    while product_details is None:
        try:
            band_id = task["band_id"]
            
            
            url = "https://bandcamp.com/api/mobile/25/merch_details"
            
            query = {
                "band_id": band_id,
                "package_ids": str(product["id"])
            }
            
            response = session.get(url, params=query)
            
            if response.status_code == 200:
                return json.loads(response.text), session
            else:
                cliLogger.cliLogger(response.status_code, task, "error")
                time.sleep(float(task["retry_delay"]) / 1000)
        except Exception as e:
            cliLogger.cliLogger(e, task, "error")
            time.sleep(float(task["retry_delay"]) / 1000)
    