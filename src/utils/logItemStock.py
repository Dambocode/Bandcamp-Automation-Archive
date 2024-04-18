import os
import json


def logItemStock(name, stock):
    with open("monitor_stock/"+ str(name) + ".json", "w+") as f:
        json.dump(stock, f, indent=4)

