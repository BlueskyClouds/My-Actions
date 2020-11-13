# -*- coding: utf8 -*-
import requests, os
from bs4 import BeautifulSoup
 
cookie = os.environ.get('cookie_52pj')

def pjCheckin(*args):
    try:
        SCKEY = os.environ.get('SCKEY')
        s = requests.Session()
        headers={
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36',
            'Cookie': cookie,
            'ContentType':'text/html;charset=gbk'
        }
        s.get('https://www.52pojie.cn/home.php?mod=task&do=apply&id=2', headers=headers)
        a = s.get('https://www.52pojie.cn/home.php?mod=task&do=draw&id=2', headers=headers)
        b = BeautifulSoup(a.text,'html.parser')
        c = b.find('div',id='messagetext').find('p').text

        if "您需要先登录才能继续本操作"  in c:
            if SCKEY:
                scurl = f"https://sc.ftqq.com/{SCKEY}.send"
                data = {
                        "text" : "52pojie  Cookie过期",
                        "desp" : c
                        }
                requests.post(scurl, data=data)
            print("cookie_52pj失效，需重新获取")
        elif "恭喜"  in c:
            print("52pj签到成功")
        else:
            print(c)
    except:
        print(b)
        print("52pj出错")
        

if __name__ == "__main__":
    if cookie:
        pjCheckin()
