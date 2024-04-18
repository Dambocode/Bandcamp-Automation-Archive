from src.utils import logItemStock, readSavedStock, discord, cliLogger


def checkStockChanges(page_data, new_stock, album, task):
    for product in page_data["products"]:
        # print(product["item_id"])

        saved_stock = readSavedStock.readSavedStock(product["item_id"])
        # print(json.loads(new_stock)["merch_inventory"][str(product["item_id"])])
        # print(saved_stock)
        # If there is no stock saved, item is new and must be saved in ./monitor_stock/{item_id}.json
        if saved_stock is None:
            logItemStock.logItemStock(product["item_id"], new_stock["merch_inventory"][str(product["item_id"])])
            discord.sendMonitorWebhook(task, product, new_stock["merch_inventory"][str(product["item_id"])], album)
            cliLogger.cliLogger(f"New Item Found: {product['item_name']}", task, "alert")

            # WEBHOOK -> NEW ITEM FOUND


        elif new_stock["merch_inventory"][str(product["item_id"])] == saved_stock:
            cliLogger.cliLogger(f"No Stock Changes - {product['item_name']}", task, "alert")
        else:
            while True:
                try:
                    discord.sendMonitorWebhook(task, product, new_stock["merch_inventory"][str(product["item_id"])], album)
                    logItemStock.logItemStock(product["item_id"], new_stock["merch_inventory"][str(product["item_id"])])
                    cliLogger.cliLogger(f"Stock Update Found for {product['item_name']}", task, "alert")
                    break
                except:
                    pass