import json

from src.utils import cliLogger

def findProductMobile(task, products):
    products = json.loads(products)
    keywords = task["keywords"].split("|")[0].lower().split(",")
    album_keywords = task["keywords"].split("|")[1].lower().split(",")

    print("Keywords: " + str(keywords))
    print("Album Keyword: " + str(album_keywords) )
    
    for product in products["merch"]:
        keywords_check = []
        for keyword in keywords:
            if keyword in product["title"].lower():
                keywords_check.append(True)
            else:
                keywords_check.append(False)
        for keyword in album_keywords:
            if product["download_title"]:
                if keyword in product["download_title"].lower():
                    keywords_check.append(True)
                else:
                    keywords_check.append(False)
            else:
                keywords_check.append(False)

        if all(keywords_check):
            cliLogger.cliLogger(f"Product Found: {product['title']}", task, "alert")
            return product