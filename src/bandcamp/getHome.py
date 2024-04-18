import requests


# getHome will initilize the home page of the bandcamp subdomain.

# This will be used in order to get our Client ID & Session ID.


def getHome(session, subdomain):
    response = session.get(
        f'https://{subdomain}.bandcamp.com/', proxies=session.proxies)
    return response, session
