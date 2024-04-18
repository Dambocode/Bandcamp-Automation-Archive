from src.bandcamp import getHome, getAlbumPage, checkStock
from src.scraper import getAlbums, getPageData
from src.utils import findAlbum, cliLogger, checkStockChanges

import requests


def monitor(task):
    
    proxy = task["proxy"]
    if proxy == "":
        proxies = {}
    else:
        proxy_ip = proxy.split(":")[0]
        proxy_port = proxy.split(":")[1]
        proxy_user = proxy.split(":")[2]
        proxy_pass = proxy.split(":")[3]

        proxies = {
            "http": f'http://{proxy_user}:{proxy_pass}@{proxy_ip}:{proxy_port}',
            "https": f'http://{proxy_user}:{proxy_pass}@{proxy_ip}:{proxy_port}'
        }
    session = requests.Session()
    session.proxies.update(proxies)

    page_data = None
    album = None

    # Find album
    while album is None:
        try:
            cliLogger.cliLogger("Searching For Album: " + task["album"], task)
            # Get the home page of the subdomain.
            
            home_response, session = getHome.getHome(session, task["subdomain"])

            # Get the albums from the home page.
            albums = getAlbums.getAlbums(home_response, task)

            # Select Album
            album = findAlbum.findAlbum(task['album'], albums)
        except Exception as e:
            cliLogger.cliLogger(e, task, "error")
            pass
    cliLogger.cliLogger("Album Found: " + album, task)
    # Find product
    while page_data is None:
        cliLogger.cliLogger(f"Scraping Products...", task)
        try:
            # Get album page.
            album_response, session = getAlbumPage.getAlbumPage(
                session, task, album)

            # Get the product ids from the albums.
            page_data = getPageData.getPageData(album_response)

        except Exception as e:
            cliLogger.cliLogger(e, task, "error")
            pass
    # Check Stock
    while True:
        cliLogger.cliLogger(f"Checking Stock...", task)
        try:
            stock = checkStock.checkStock(task, page_data)
            checkStockChanges.checkStockChanges(page_data, stock, album, task)
            break

        except Exception as e:
            cliLogger.cliLogger(e, task, "error")
            pass


task = [
    {
        "id": 2,
        "subdomain": "daupe",
        "album": "kiss",
        "proxy": "",
        "webhook": "https://discord.com/api/webhooks/1039202393805561907/8w9csJPG2MgsH1aCr9tvZ8W5BaE-hJSHt4jFNcIeqqhrrVhfp52RZmW_qocFkDnc8wvf"
    }
]
monitor(task[0])
# for task in loadTasks.loadTasks():
    