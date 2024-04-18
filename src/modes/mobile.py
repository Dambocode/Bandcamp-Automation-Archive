

from src.utils import cliLogger, findProductMobile

from src.mobile import login, getBandDetails, saveShippingDetails, groupOrder, getProductDetails, generateBandcampSession, submitOrder, getPaymentToken

from src.utils import discord, checkoutAlert
import requests
import time


def bandCampMobile(task):
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

    tokens, bootstrap_response, session = login.login(session, task)

    paymentToken = getPaymentToken.getPaymentToken(task)

    session.headers.update(
        {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
            "Authorization": f"Bearer {tokens['access_token']}"
        }
    )

    # Saving Shipping Info
    shipping_data = None
    while shipping_data is None:
        try:
            shipping_data, session = saveShippingDetails.saveShippingDetails(
                session, task)
        except Exception as e:
            cliLogger.cliLogger(e, task, "error")
            time.sleep(float(task["retry_delay"]) / 1000)
            pass

    # Find product
    product_details = None
    while product_details is None:
        try:
            products_response, session = getBandDetails.getBandDetails(session, task)

            if products_response.status_code == 200:
                product_data = findProductMobile.findProductMobile(
                    task, products_response.text)
                if product_data is None:
                    cliLogger.cliLogger("Waiting For Product", task)
                    time.sleep(float(task["retry_delay"]) / 1000)
                if product_data:
                    product_details, session = getProductDetails.getProductDetails(session, task, product_data)


            else:
                cliLogger.cliLogger(
                    f"Site Error: {products_response.status_code}", task)
                time.sleep(float(task["retry_delay"]) / 1000)

        except Exception as e:
            cliLogger.cliLogger(e, task, "error")
            time.sleep(float(task["retry_delay"]) / 1000)
            pass

    # Stat checkout clock
    task["start_time"] = time.time()

    # Group Order Data
    order_data = None
    while order_data is None:
        
        try:
            order_data = groupOrder.groupOrder(session, task, bootstrap_response, tokens['access_token'], product_details)
        
        except Exception as e:
            cliLogger.cliLogger(e, task, "error")
            time.sleep(float(task["retry_delay"]) / 1000)
            pass

    
    # Submit Order
    success_data = None
    while success_data is None:
        try:
            success_data = submitOrder.submitOrder(session, task, bootstrap_response, tokens['access_token'], shipping_data, paymentToken, product_details, order_data)
            discord.mobileSuccessWebhook(task, product_details)

        
        except Exception as e:
            cliLogger.cliLogger(e, task, "error")
            time.sleep(float(task["retry_delay"]) / 1000)
            pass
