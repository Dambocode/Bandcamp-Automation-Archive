import requests

def getAlbumPage(session, subdomain, link):
    # Get the album page.
    response = session.get("https://"+ subdomain + ".bandcamp.com" + link, proxies=session.proxies)
    return response, session

