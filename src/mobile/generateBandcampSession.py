from src.utils import cliLogger

import time


def generateBandcampSession(session, task):

    url = "https://bandcamp.com/api/mobile/25/bootstrap_data?platform=a&version=218977"

    headers = {
        "X-Requested-With": "com.bandcamp.android",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 12; SM-G980F Build/SP1A.210812.016)", "Accept-Encoding": "gzip"
    }

    while True:
        try:
            response = session.get(url, headers=headers)

            if response.status_code == 200:
                return response.headers

        except Exception as e:
            cliLogger.cliLogger(e, task, "error")
            time.sleep(float(task["retry_delay"]) / 1000)
