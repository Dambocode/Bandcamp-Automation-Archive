

def getPaymentPage(session, url):
    response = session.get(url, proxies=session.proxies)

    return response, session
