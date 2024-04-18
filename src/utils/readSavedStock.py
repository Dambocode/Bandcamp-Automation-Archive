import json


def readSavedStock(item_id):
    try:
        with open(f"monitor_stock/{item_id}.json", 'r') as f:
            data = json.load(f)
            return data

    except:
        return None