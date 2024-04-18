import hmac
import hashlib
import requests
import numpy as np
import json

from src.utils import cliLogger


def zero_fill_right_shift(val, n):
    return (val >> n) if val >= 0 else ((val + 0x100000000) >> n)


def calculatePow(body, payload):
    s1 = ""
    i1 = 0
    while s1 == "":
        num = np.base_repr(i1, 36).lower()
        digest = hashlib.sha1((body + payload + num).encode('utf-8')).digest()

        i2 = 0
        i3 = 0
        while True:
            if i3 < len(digest):
                i4 = 0
                if digest[i3] < 0:
                    i4 = 0
                elif digest[i3] < 1:
                    i4 = 8
                elif digest[i3] < 2:
                    i4 = 7
                elif digest[i3] < 4:
                    i4 = 6
                elif digest[i3] < 8:
                    i4 = 5
                elif digest[i3] < 16:
                    i4 = 4
                elif digest[i3] < 32:
                    i4 = 3
                elif digest[i3] < 64:
                    i4 = 2
                elif digest[i3] < 128:
                    i4 = 1

                i2 = i2 + i4
                if i4 == 8:
                    i3 += 1
                    continue

            if i2 >= 10:
                s1 = num
            i1 += 1
            break

    return s1


def byteSwap(digest_bytes):
    cArr = [None] * (len(digest_bytes) * 2)
    i = 0
    while i < len(digest_bytes):
        i2 = i * 2
        cArr2 = list("0123456789abcdef")
        cArr[i2] = cArr2[zero_fill_right_shift((digest_bytes[i] & 240), 4)]
        cArr[i2 + 1] = cArr2[digest_bytes[i] & 15]
        i += 1
    return ''.join(cArr)


def hash(dm, key):
    key = bytes(key, "UTF-8")
    message = bytes(dm, "UTF-8")
    digester = hmac.new(key, message, hashlib.sha1)
    signature = digester.digest()
    return byteSwap(signature)


def login(session, task):
    email = task["email"]
    password = task["password"]

    # Get Bootstrap Data for PoW and DM
    bootstrap_response = session.get(
        url="https://bandcamp.com/api/mobile/25/bootstrap_data?platform=a&version=218977",
        headers={"X-Requested-With": "com.bandcamp.android",
                 "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 12; SM-G980F Build/SP1A.210812.016)", "Accept-Encoding": "gzip"},
    )

    # Check Login on Account
    BODY = '{"email":"'+ email + '","password":"' + password + '"}' 

    dm = bootstrap_response.headers["x-bandcamp-dm"]
    dm = dm[:19] + dm[22:]
    bandcamDM = hash(f"{dm}{BODY}", "dtmfa")

    work = bootstrap_response.headers["x-bandcamp-pow"].split(":")[2]
    bandcamPoW = f"1:10:{work}:{calculatePow(BODY, work)}"

    response = session.post(
        url="https://bandcamp.com/api/mobile/25/check_login",
        headers={"X-Requested-With": "com.bandcamp.android", "X-Bandcamp-DM": bandcamDM, "X-Bandcamp-PoW": bandcamPoW, "Content-Type": "application/json",
                 "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 12; SM-G980F Build/SP1A.210812.016)", "Accept-Encoding": "gzip"},
        data=BODY,
        proxies=None
    )
    # print(response.text)

    check_login_response = json.loads(response.text)

    BODY = f"grant_type=password&username={check_login_response['accounts'][0]['user_id']}&password={password}&username_is_user_id=1&client_id=134&client_secret=1myK12VeCL3dWl9o%2FncV2VyUUbOJuNPVJK6bZZJxHvk%3D"
    bandcamDM = hash(f"{dm}{BODY}", "dtmfa")
    response = session.post(
        url="https://bandcamp.com/oauth_login",
        headers={"X-Requested-With": "com.bandcamp.android", "X-Bandcamp-DM": bandcamDM, "Content-Type": "application/x-www-form-urlencoded",
                 "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 12; SM-G980F Build/SP1A.210812.016)", "Accept-Encoding": "gzip"},
        data=BODY,
        proxies=None
    )

    cliLogger.cliLogger("Successfully Logged In", task, "alert")

    return json.loads(response.text), bootstrap_response, session
