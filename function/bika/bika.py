import requests
import hashlib
import hmac
import json
import random
import string
import time
import os
import sys;
sys.path.append("My-Actions/function/bika/")
from sendNotify import *
from http import client

sendNotify = sendNotify()

SEND_KEY = os.environ['SEND_KEY']

msg = ''

# noinspection SpellCheckingInspection
pica_api_host = "picaapi.picacomic.com"
pica_api_base_url = "https://%s/" % pica_api_host
sign_in_path = "auth/sign-in"
punch_in_path = "users/punch-in"
POST = "POST"

# noinspection SpellCheckingInspection
api_key = "C69BAF41DA5ABD1FFEDC6D2FEA56B"
api_secret = "~d}$Q7$eIni=V)9\\RK/P.RM4;9[7|@/CA}b~OW!3?EV`:<>M7pddUBL5n|0/*Cn"
# noinspection SpellCheckingInspection
static_headers = {
    "api-key": api_key,
    "accept": "application/vnd.picacomic.com.v1+json",
    "app-channel": "2",
    "app-version": "2.2.1.2.3.3",
    "app-uuid": "defaultUuid",
    "app-platform": "android",
    "app-build-version": "44",
    "User-Agent": "okhttp/3.8.1",
    "image-quality": "original",
}


def send_request(path: string, method: string, body: string = None, token: string = None) -> dict:
    current_time = str(int(time.time()))
    nonce = "".join(random.choices(string.ascii_lowercase + string.digits, k=32))
    raw = path + current_time + nonce + method + api_key
    raw = raw.lower()
    h = hmac.new(api_secret.encode(), digestmod=hashlib.sha256)
    h.update(raw.encode())
    signature = h.hexdigest()
    headers = static_headers.copy()
    headers["time"] = current_time
    headers["nonce"] = nonce
    headers["signature"] = signature
    if body is not None:
        headers["Content-Type"] = "application/json; charset=UTF-8"
    if token is not None:
        headers["authorization"] = token
    connection = client.HTTPSConnection(pica_api_host)
    connection.request(method, '/' + path, body, headers)
    response = connection.getresponse().read().decode("utf-8")
    json_object = json.loads(response)
    if json_object["code"] != 200:
        if SEND_KEY != '':
            sendNotify.send(title = u"哔咔漫画自动打哔咔", msg = "登录失败 账号或密码错误")
            print(json_object["message"])
        exit(0)
        raise RuntimeError(json_object["message"])
    return json_object

def sign_in(email: string, password: string) -> string:
    body = {
        "email": email,
        "password": password
    }
    return send_request(sign_in_path, POST, json.dumps(body))["data"]["token"]

def punch_in(token: string):
    return send_request(punch_in_path, POST, token=token)

if __name__ == '__main__':
    if os.environ['BIKA_USER'] == "" or os.environ['BIKA_PASS'] == "":
        print("未填写哔咔账号密码 取消运行")
        exit(0)
    current_token = sign_in(os.environ['BIKA_USER'], os.environ['BIKA_PASS'])
    punch_in_response = punch_in(current_token)
    result = punch_in_response["data"]["res"]
    if result["status"] == "ok":
        msg = "打卡成功, 最后一次打卡: %s" % result["punchInLastDay"]
        print(msg)
    else:
        msg = '重复签到 - Already punch-in'
        print(msg)

if SEND_KEY == '':
    sendNotify.send(title = u"哔咔漫画自动打哔咔", msg = msg)

