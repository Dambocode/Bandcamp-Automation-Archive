

def getBandDetails(session, task):
    band_id = task["band_id"]
    
    
    url = "https://bandcamp.com/api/mobile/25/band_details"
    
    query = {
        "band_id": band_id
    }
    
    response = session.get(url, params=query)
    
    return response, session
    
    