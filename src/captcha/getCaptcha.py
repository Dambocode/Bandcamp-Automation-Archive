import requests


def getCaptcha(task):
    while True:
        try:
            response = requests.get(
                f"http://localhost:{task['captcha_port']}/captcha")

            if response.text:
                return response.text
        except Exception as e:
            print("Waiting For Captcha")
            pass

# getCaptcha({"captcha_port": 3000})
