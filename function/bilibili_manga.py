import requests
import sys;
sys.path.append("My-Actions/function/")
from bilibili import *
from sendNotify import *
import time
import os

msg = ""
day = ""

sendNotify = sendNotify()
SEND_KEY = os.environ['SEND_KEY']
# 尝试登陆
b = Bilibili()
login = b.login(username=os.environ['BILI_USER'], password=os.environ['BILI_PASS'])
print(login)
if login == False:
    if SEND_KEY != '':
        sendNotify.send(title = u"哔哩哔哩漫画签到", msg = "登录失败 账号或密码错误")
        exit(0)
# 获取 Cookie
cookie_str = ""
cookies = b.get_cookies()

for cookie in cookies:
    cookie_str += cookie + "=" + cookies[cookie] + "; "

headers_with_cookie={
    'User-Agent': "Mozilla/5.0 BiliDroid/6.4.0 (bbcallen@gmail.com) os/android model/M1903F11I mobi_app/android build/6040500 channel/bili innerVer/6040500 osVer/9.0.0 network/2",
    'Cookie': cookie_str
}

print("哔哩哔哩漫画开始签到 start>>>")
msg = msg + "哔哩哔哩漫画开始签到: \n"

r = requests.post("https://manga.bilibili.com/twirp/activity.v1.Activity/ClockIn", verify=False, headers=headers_with_cookie, data={
    "platform": "android"
})

# print("响应: " + r.text)
if r.json()['code'] == 0:
    print("签到成功.")
    msg = msg + "签到成功🐶\n"
if r.json()['msg'] == "clockin clockin is duplicate":
    print("今日已签到.")
    msg = msg + "今日已签到⚠\n"

time.sleep(2)

print("哔哩哔哩漫画获取签到信息 start>>>")
msg = msg + "哔哩哔哩漫画获取签到信息: \n"
r = requests.post("https://manga.bilibili.com/twirp/activity.v1.Activity/GetClockInInfo", verify=False, headers=headers_with_cookie)
day = str(r.json()['data']['day_count'])
if day == "0":
    print("登录失败,未登录🐶")
    msg = "登录失败,未登录🐶"
print("累计签到" + day + "天🐶")
msg = msg + "累计签到" + day + "天🐶\n"

time.sleep(3)

# 如果不使用银瓜子兑换硬币 请注释掉下面两行即可。
print("哔哩哔哩银瓜子兑换硬币 start>>>")
print(b.silver_to_coin())

# print(msg)
if SEND_KEY == '':
    sendNotify.send(title = u"哔哩哔哩漫画签到",msg = msg)