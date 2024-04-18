from bs4 import BeautifulSoup


def getAlbums(response, task):
    # Get all albums from a subdomain.
    


    # Get the albums from the home page.
    soup = BeautifulSoup(response.text, 'html.parser')

    links = []
    for link in soup.find_all('a'):
        links.append(link.get("href"))
    
    unique_links = []
    for link in links:
        if link != None:
            if link.startswith('/album'):
                unique_links.append(link)
    unique_links = [*set(unique_links)]
    
    return unique_links
    
