import re


def findProduct(keywords, products):
    keywords = keywords.lower().split(",")
    for product in products:
        keywords_check = []
        for keyword in keywords:
            if keyword in product["item_name"].lower():
                # print("Keyword Found: " + keyword)
                keywords_check.append(True)
            else:
                keywords_check.append(False)
        if all(keywords_check):
            return product

        # print(product["item_name"].lower())
        # print(regex_res)
        # for keyword in keywords:

    
