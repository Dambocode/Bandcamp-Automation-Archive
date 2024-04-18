

def calculateFees(session, task, product):
    band_id = task["band_id"]
    
    
    url = "https://bandcamp.com/api/mobile/25/hypo_shipping_and_tax"
    
    query = {
        "qty": 1,
        "unit_price": product["price"]
    }
    
    response = session.get(url, params=query)
    
    return response, session
    
    