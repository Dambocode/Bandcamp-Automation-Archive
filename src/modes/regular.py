from src.bandcamp import getHome, addToCart, removeFromCart, getAlbumPage, startCheckout, shippingCheckout, submitShipping, getPaymentPage, getPaymentToken, submitOrder, getPaypal

from src.scraper import getAlbums, getPageData, getCheckoutData, getPlaceOrderData
from src.utils import findProduct, findAlbum, discord, loadTasks, cliLogger, checkoutAlert
from src.captcha import getCaptcha

import requests


import json
from multiprocessing import Process
import time
import os


def bandCampRegular(task):
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
    session.headers.update(
        {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'})

    product = None
    album = None

# Find album
    while album is None:
        try:
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
    while product is None:
        cliLogger.cliLogger(f"Searching for Product: {task['keywords']}", task)
        try:
            # Get album page.
            album_response, session = getAlbumPage.getAlbumPage(
                session, task["subdomain"], album)

            # Get the product ids from the albums.
            page_data = getPageData.getPageData(album_response)

            # Select Product
            product = findProduct.findProduct(
                task['keywords'], page_data['products'])
            if product is None:
                time.sleep(float(task["retry_delay"]) / 1000)

        except Exception as e:
            cliLogger.cliLogger(e, task, "error")
            pass
    cliLogger.cliLogger("Product Found: " + product["item_name"], task)

    # Stat checkout clock
    task["start_time"] = time.time()

# Add item to cart - /cart/cb
    while True:
        try:
            # Add the item to the cart.
            atc_response, session = addToCart.addToCart(
                session, product, page_data['band_id'], task)
            if atc_response.status_code == 200:
                if json.loads(atc_response.text)["id"]:
                    cliLogger.cliLogger("Item Added to Cart", task, "alert")
                    break
        except Exception as e:
            cliLogger.cliLogger(e, task, "error")

# Start checkout session (c or p) - /cart/checkout_start
    while True:
        try:
            # Start the checkout & Get redirect.
            start_checkout_response, session = startCheckout.startCheckout(
                session, task, album)
            if start_checkout_response.headers["location"]:
                cliLogger.cliLogger("Checkout URL Generated", task)
                break
        except Exception as e:
            cliLogger.cliLogger(e, task, "error")

# Get Shipping Page - /cart/checkout_shipping_address
    while True:
        try:
            # Get the shipping page
            shipping_response, session = shippingCheckout.shippingCheckout(
                session, task, start_checkout_response.headers["location"], json.loads(atc_response.text)["id"], album)
            # Get Checkout Data from shipping page.
            checkout_data = getCheckoutData.getCheckoutData(shipping_response)
            
            try:
                if checkout_data["sale_ids"]:
                    cliLogger.cliLogger("Checkout Data Generated", task)
                    break
            except KeyError:
                cliLogger.cliLogger(
                    f"[{product['item_name']}] Waiting for restock...", task)
                time.sleep(float(task["retry_delay"]) / 1000)
                pass
        except Exception as e:
            cliLogger.cliLogger(e, task, "error")
            pass

# Submit Shipping - /api/addresses/1/add_to_items
    while True:
        try:
            # Submit Shipping
            submit_shipping_response, session = submitShipping.submitShipping(
                session, task, checkout_data, start_checkout_response.headers["location"])
            if submit_shipping_response.status_code == 200:
                if json.loads(submit_shipping_response.text) == {}:
                    cliLogger.cliLogger(f"Submitting Shipping", task)
                    break
        except Exception as e:
            cliLogger.cliLogger(e, task, "error")
    cliLogger.cliLogger(f"Shipping Submitted", task, "alert")

# Payment Handler (Paypal or Credit Card)
    while True:
        try:
            # Get the payment page redirect.
            start_payment_response, session = shippingCheckout.shippingCheckout(
                session, task, start_checkout_response.headers["location"], json.loads(atc_response.text)["id"], album, True)

            if start_payment_response.headers["location"]:
                cliLogger.cliLogger(f"Got Payment Page", task)
                break
        except Exception as e:
            cliLogger.cliLogger(e, task, "error")

    # Paypal Checkout
    if task["payment_pref"] == "p":
        while True:
            try:
                # Get the payment page
                payment_page, session = getPaymentPage.getPaymentPage(
                    session, start_payment_response.headers["location"])

                # Get the payment page data.
                payment_data = getPlaceOrderData.getPlaceOrderData(
                    payment_page)
                
                if payment_data["force_paypal_params"]:
                    cliLogger.cliLogger(
                        f"Generating Paypal URL", task, "paypal")
                    break
            except Exception as e:
                cliLogger.cliLogger(e, task, "error")

    # Get Paypal.com Link from Bandcamp Checkout Page
        while True:
            try:
                # Start Paypal
                paypal_url_response, session = getPaypal.getPaypal(
                    session, payment_data["force_paypal_params"])
                if paypal_url_response.headers["location"]:
                    cliLogger.cliLogger(
                        f'[{product["item_name"]}] Paypal URL Generated: {paypal_url_response.headers["location"]}', task, "success")
                break
            except Exception as e:
                cliLogger.cliLogger(e, task, "error")
        while True:
            task["end_time"] = time.time()
            task["paypal_link"] = paypal_url_response.headers['Location']

            # Send Webhook
            discord.sendTaskWebhook(task, product)
            # Alert Sound
            checkoutAlert.checkoutAlert(task)
            break

    # Credit Card Checkout
    if task["payment_pref"] == "c":

        # Get the payment page
        while True:
            try:
                ref_url = start_payment_response.headers["location"] + \
                    "&collected_address=true"

                payment_page, session = getPaymentPage.getPaymentPage(
                    session, ref_url)
                break
            except Exception as e:
                cliLogger.cliLogger("Error: " + e, task, "error")

        # Get the payment page data - /cart/checkout
        while True:
            try:
                payment_data = getPlaceOrderData.getPlaceOrderData(
                    payment_page)
                
                json.dump(checkout_data, open("checkout_data.json", "w"))

                ref_url = "https://bandcamp.com/cart/checkout" + \
                    payment_data["signed_params"] + "&collected_address=true"
                ref_url = ref_url.replace("amp;", "")
                break
            except Exception as e:
                cliLogger.cliLogger("Error: " + e, task, "error")

        # Generate Payment Token
        while True:
            try:
                cliLogger.cliLogger("Generating Payment Token", task)
                payment_token_response = getPaymentToken.getPaymentToken(
                    session, payment_data, task)
                payment_token = json.loads(payment_token_response.text)[
                    "transaction"]["payment_method"]["token"]
                break
            except Exception as e:
                cliLogger.cliLogger("Error: " + e, task, "error")


        # Submit Order
        while True:
            try:
                cliLogger.cliLogger("Submitting Order", task, "alert")
                submit_order_response, session = submitOrder.submitOrder(
                    session, task, payment_data, ref_url, payment_token, getCaptcha.getCaptcha(task))
                print(submit_order_response.text)
                if json.loads(submit_order_response.text)["payment_ids"]:
                    cliLogger.cliLogger(
                        "Successfully Checked Out: " + product["item_name"], task, "success")
                    while True:
                            try:
                                task["end_time"] = time.time()

                                task["order_url"] = ref_url

                                # Send Webhook
                                discord.sendTaskWebhook(task, product)
                                # Alert Sound
                                checkoutAlert.checkoutAlert(task)
                                break
                            except:
                                pass
                        # break
            except Exception as e:
                cliLogger.cliLogger(str(e), task, "error")
                time.sleep(task["retry_delay"])

def bandCampPreload(task):

    print(task)
    input()

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
    session.headers.update(
        {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'})

    product = None
    album = None

# Find dummy album
    while album is None:
        try:
            # Get the home page of the subdomain.
            home_response, session = getHome.getHome(session, task["preload_subdomain"])

            # Get the albums from the home page.
            albums = getAlbums.getAlbums(home_response, task)

            # Select Album
            album = findAlbum.findAlbum(task['preload_album'], albums)
        except Exception as e:
            cliLogger.cliLogger(e, task, "error")
            pass
    cliLogger.cliLogger("Preload Album Found: " + album, task)


# Find dummy product
    while product is None:
        cliLogger.cliLogger(f"Searching for Preload Product: {task['preload_keywords']}", task)
        try:
            # Get album page.
            album_response, session = getAlbumPage.getAlbumPage(
                session, task["preload_subdomain"], album)

            # Get the product ids from the albums.
            page_data = getPageData.getPageData(album_response)

            # Select Product
            product = findProduct.findProduct(
                task['preload_keywords'], page_data['products'])
            if product is None:
                time.sleep(float(task["retry_delay"]) / 1000)

        except Exception as e:
            cliLogger.cliLogger(e, task, "error")
            input()
            pass
    cliLogger.cliLogger("Preload Product Found: " + product["item_name"], task)


# Add dummy item to cart - /cart/cb
    while True:
        try:
            # Add the item to the cart.
            atc_response, session = addToCart.addToCart(
                session, product, page_data['band_id'], task)
            if atc_response.status_code == 200:
                if json.loads(atc_response.text)["id"]:
                    cliLogger.cliLogger("Preload Item Added to Cart", task, "alert")
                    break
        except Exception as e:
            cliLogger.cliLogger(e, task, "error")

# Start checkout session (c or p) - /cart/checkout_start
    while True:
        try:
            # Start the checkout & Get redirect.
            start_checkout_response, session = startCheckout.startCheckout(
                session, task, album)
            if start_checkout_response.headers["location"]:
                cliLogger.cliLogger("Checkout URL Generated", task)
                break
        except Exception as e:
            cliLogger.cliLogger(e, task, "error")

# Get Shipping Page - /cart/checkout_shipping_address
    while True:
        try:
            # Get the shipping page
            shipping_response, session = shippingCheckout.shippingCheckout(
                session, task, start_checkout_response.headers["location"], json.loads(atc_response.text)["id"], album)
            # Get Checkout Data from shipping page.
            checkout_data = getCheckoutData.getCheckoutData(shipping_response)
            try:
                if checkout_data["sale_ids"]:
                    cliLogger.cliLogger("Checkout Data Generated", task)
                    break
            except KeyError:
                cliLogger.cliLogger(
                    f"[{product['item_name']}] Waiting for restock...", task)
                time.sleep(float(task["retry_delay"]) / 1000)
                pass
        except Exception as e:
            cliLogger.cliLogger(e, task, "error")
            pass

# Submit Shipping - /api/addresses/1/add_to_items
    while True:
        try:
            # Submit Shipping
            submit_shipping_response, session = submitShipping.submitShipping(
                session, task, checkout_data, start_checkout_response.headers["location"])
            if submit_shipping_response.status_code == 200:
                if json.loads(submit_shipping_response.text) == {}:
                    cliLogger.cliLogger(f"Submitting Shipping", task)
                    break
        except Exception as e:
            cliLogger.cliLogger(e, task, "error")
    cliLogger.cliLogger(f"Shipping Submitted", task, "alert")

# Remove Dummy Item From Cart
    while True:
        try:
            remove_response, session = removeFromCart.removeFromCart(session,product,task)
            print(remove_response.text)
            print(session.cookies.get_dict())
            
        except Exception as e:
            cliLogger.cliLogger(e, task, "error")
        cliLogger.cliLogger(f"Preload Complete!", task, "alert")
        break


# Find album
    while album is None:
        try:
            # Get the home page of the subdomain.
            home_response, session = getHome.getHome(session, task["subdomain"])

            # Get the albums from the home page.
            albums = getAlbums.getAlbums(home_response, task)

            print(task['album'])

            # Select Album
            album = findAlbum.findAlbum(task['album'], albums)
        except Exception as e:
            cliLogger.cliLogger(e, task, "error")
            pass
    cliLogger.cliLogger("Album Found: " + album, task)
# Find product
    while product is None:
        cliLogger.cliLogger(f"Searching for Product: {task['keywords']}", task)
        try:
            # Get album page.
            album_response, session = getAlbumPage.getAlbumPage(
                session, task["subdomain"], album)

            # Get the product ids from the albums.
            page_data = getPageData.getPageData(album_response)

            # Select Product
            product = findProduct.findProduct(
                task['keywords'], page_data['products'])
            if product is None:
                time.sleep(float(task["retry_delay"]) / 1000)

        except Exception as e:
            cliLogger.cliLogger(e, task, "error")
            pass
    cliLogger.cliLogger("Product Found: " + product["item_name"], task)

    # Stat checkout clock
    task["start_time"] = time.time()

# Add item to cart - /cart/cb
    while True:
        try:
            # Add the item to the cart.
            atc_response, session = addToCart.addToCart(
                session, product, page_data['band_id'], task)
            if atc_response.status_code == 200:
                print(atc_response.text)
                input()
                if json.loads(atc_response.text)["id"]:
                    cliLogger.cliLogger("Item Added to Cart", task, "alert")
                    break
        except Exception as e:
            cliLogger.cliLogger(e, task, "error")

# Payment Handler (Paypal or Credit Card)
    while True:
        try:
            # Get the payment page redirect.
            start_payment_response, session = shippingCheckout.shippingCheckout(
                session, task, start_checkout_response.headers["location"], json.loads(atc_response.text)["id"], album, True)

            if start_payment_response.headers["location"]:
                cliLogger.cliLogger(f"Got Payment Page", task)
                break
        except Exception as e:
            cliLogger.cliLogger(e, task, "error")



    # Paypal Checkout
    if task["payment_pref"] == "p":
        while True:
            try:
                # Get the payment page
                payment_page, session = getPaymentPage.getPaymentPage(
                    session, start_payment_response.headers["location"])

                # Get the payment page data.
                payment_data = getPlaceOrderData.getPlaceOrderData(
                    payment_page)
                if payment_data["force_paypal_params"]:
                    cliLogger.cliLogger(
                        f"Generating Paypal URL", task, "paypal")
                    break
            except Exception as e:
                cliLogger.cliLogger(e, task, "error")

    # Get Paypal.com Link from Bandcamp Checkout Page
        while True:
            try:
                # Start Paypal
                paypal_url_response, session = getPaypal.getPaypal(
                    session, payment_data["force_paypal_params"])
                if paypal_url_response.headers["location"]:
                    cliLogger.cliLogger(
                        f'[{product["item_name"]}] Paypal URL Generated: {paypal_url_response.headers["location"]}', task, "success")
                break
            except Exception as e:
                cliLogger.cliLogger(e, task, "error")
        while True:
            task["end_time"] = time.time()
            task["paypal_link"] = paypal_url_response.headers['Location']

            # Send Webhook
            discord.sendTaskWebhook(task, product)
            # Alert Sound
            checkoutAlert.checkoutAlert(task)
            break

#     # Credit Card Checkout
#     if task["payment_pref"] == "c":

#         # Get the payment page
#         while True:
#             try:
#                 ref_url = start_payment_response.headers["location"] + \
#                     "&collected_address=true"

#                 payment_page, session = getPaymentPage.getPaymentPage(
#                     session, ref_url)
#                 break
#             except Exception as e:
#                 cliLogger.cliLogger("Error: " + e, task, "error")

#         # Get the payment page data - /cart/checkout
#         while True:
#             try:
#                 payment_data = getPlaceOrderData.getPlaceOrderData(
#                     payment_page)

#                 ref_url = "https://bandcamp.com/cart/checkout" + \
#                     payment_data["signed_params"] + "&collected_address=true"
#                 ref_url = ref_url.replace("amp;", "")
#                 break
#             except Exception as e:
#                 cliLogger.cliLogger("Error: " + e, task, "error")

#         # Generate Payment Token
#         while True:
#             try:
#                 cliLogger.cliLogger("Generating Payment Token", task)
#                 payment_token_response = getPaymentToken.getPaymentToken(
#                     session, payment_data, task)
#                 payment_token = json.loads(payment_token_response.text)[
#                     "transaction"]["payment_method"]["token"]
#                 break
#             except Exception as e:
#                 cliLogger.cliLogger("Error: " + e, task, "error")

#         print(payment_token)
#         print(ref_url)


#         # Submit Order
#         # while True:
#         try:
#             cliLogger.cliLogger("Submitting Order", task, "alert")
#             submit_order_response, session = submitOrder.submitOrder(
#                 session, task, payment_data, ref_url, payment_token, input("ENTER CAPTCHA:\n"))
#             print(submit_order_response.text)
#             if json.loads(submit_order_response.text)["payment_ids"]:
#                 cliLogger.cliLogger(
#                     "Successfully Checked Out: " + product["item_name"], task, "success")
#                 while True:
#                         try:
#                             task["end_time"] = time.time()

#                             task["order_url"] = ref_url

#                             # Send Webhook
#                             discord.sendTaskWebhook(task, product)
#                             # Alert Sound
#                             checkoutAlert.checkoutAlert(task)
#                             break
#                         except:
#                             pass
#                     # break
#         except Exception as e:
#             cliLogger.cliLogger(
#                 "Checkout Failed: " + json.loads(submit_order_response.text)["error_key"] + f" - Retrying in {task['retry_delay']}ms", task, "error")
#             time.sleep(task["retry_delay"])



