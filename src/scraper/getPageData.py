from bs4 import BeautifulSoup
import json


def getPageData(response):
    # Get the albums from the home page.
    soup = BeautifulSoup(response.text, 'html.parser')

    page_data = str(soup.findAll(type='application/ld+json')[0])
    page_data = page_data.replace('<script type="application/ld+json">', "")
    page_data = page_data.replace("</script>", "")
    page_data = page_data.replace("\n", "")
    page_data = page_data.replace("\t", "")
    page_data = json.loads(page_data)

    products = []
    for product in page_data["albumRelease"]:
        try:
            products.append({
                "item_name": product["name"],
                "item_description": product["description"],
                "item_image": product["image"][0],
                "item_id": product["additionalProperty"][0]["value"],
                "item_type": product["additionalProperty"][1]["value"],
                "price": product["offers"]["price"],
                "availability": product["offers"]["availability"],
            })
        except KeyError as e:
            pass

    export_data = {
        "band_id": page_data["publisher"]["additionalProperty"][0]["value"],
        "products": products
    }

    return export_data
