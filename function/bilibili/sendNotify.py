import requests
import time
import hmac
import hashlib
import base64
import json
import os
import urllib.parse


class sendNotify:
    # =======================================微信server酱通知设置区域===========================================
    # 此处填你申请的SCKEY.
    # 注：此处设置github action用户填写到Settings-Secrets里面(Name输入PUSH_KEY)
    SCKEY = ''

    # =======================================Bark App通知设置区域===========================================
    # 此处填你BarkAPP的信息(IP/设备码，例如：https://api.day.app/XXXXXXXX)
    # 注：此处设置github action用户填写到Settings-Secrets里面（Name输入BARK_PUSH）
    BARK_PUSH = ''
    # BARK app推送铃声,铃声列表去APP查看复制填写
    # 注：此处设置github action用户填写到Settings-Secrets里面（Name输入BARK_SOUND , Value输入app提供的铃声名称，例如:birdsong）
    BARK_SOUND = ''

    # =======================================telegram机器人通知设置区域===========================================
    # 此处填你telegram bot 的Token，例如：1077xxx4424:AAFjv0FlexboxEMGfi22B4yh15R5uw
    # 注：此处设置github action用户填写到Settings-Secrets里面(Name输入TG_BOT_TOKEN)
    TG_BOT_TOKEN = ''
    # 此处填你接收通知消息的telegram用户的id，例如：129xxx206
    # 注：此处设置github action用户填写到Settings-Secrets里面(Name输入TG_USER_ID)
    TG_USER_ID = ''

    # =======================================钉钉机器人通知设置区域===========================================
    # 此处填你钉钉 bot 的webhook，例如：5a544165465465645d0f31dca676e7bd07415assayed
    # 注：此处设置github action用户填写到Settings-Secrets里面(Name输入DD_BOT_TOKEN)
    DD_BOT_TOKEN = ''
    # 密钥，机器人安全设置页面，加签一栏下面显示的SEC开头的字符串
    DD_BOT_SECRET = ''

    # =======================================企业微信机器人通知设置区域=========================================== 此处填你企业微信机器人的
    # webhook(详见文档 https://work.weixin.qq.com/api/doc/90000/90136/91770)，例如：693a91f6-7xxx-4bc4-97a0-0ec2sifa5aaa
    # 注：此处设置github action用户填写到Settings-Secrets里面(Name输入QYWX_KEY)
    # QYWX_KEY = ''

    # =======================================企业微信应用消息通知设置区域=========================================== 此处填你企业微信应用消息的
    # 第一个值是企业id，第二个值是secret，第三个值@all(或者成员id)，第四个值是AgentID 中间以逗号隔开
    # 详情查看https://note.youdao.com/ynoteshare1/index.html?id=351e08a72378206f9dd64d2281e9b83b&type=note#/
    # B-791548lnzXBE6_BWfxdf3kSTMJr9vFEPKAbh6WERQ,mingcheng,1000001,2COXgjH2UIfERF2zxrtUOKgQ9XklUqMdGSWLBoW_lSDAdafat
    QYWX_AM = ''

    # =======================================QQ酷推通知设置区域===========================================
    # 此处填你申请的SKEY(具体详见文档 https://cp.xuthus.cc/)
    # 注：此处设置github action用户填写到Settings-Secrets里面(Name输入QQ_SKEY)
    # QQ_SKEY = ''
    # #此处填写私聊或群组推送，默认私聊(send或group或者wx)
    # QQ_MODE = 'send'

    # =======================================push+设置区域=======================================
    # 官方文档：https://www.pushplus.plus/
    # PUSH_PLUS_TOKEN：微信扫码登录后一对一推送或一对多推送下面的token(您的Token)，不提供PUSH_PLUS_USER则默认为一对一推送
    PUSH_PLUS_TOKEN = ''
    # PUSH_PLUS_USER： 一对多推送的“群组编码”（一对多推送下面->您的群组(如无则新建)->群组编码，如果您是创建群组人。也需点击“查看二维码”扫描绑定，否则不能接受群组消息推送）
    PUSH_PLUS_USER = ''

    # Server酱
    if os.environ['PUSH_KEY'] != "":
        SCKEY = os.environ['PUSH_KEY']

    # Bark App
    if os.environ['BARK_PUSH'] != "":
        if os.environ['BARK_PUSH'].find("https") != -1 or os.environ['BARK_PUSH'].find("http") != -1:
            BARK_PUSH = os.environ['PUSH_KEY']
        else:
            BARK_PUSH = "https://api.day.app/" + os.environ['BARK_PUSH']
    elif os.environ['BARK_SOUND'] != "":
        BARK_SOUND = os.environ['BARK_SOUND']
    elif BARK_PUSH != "" or BARK_PUSH.find("https") != -1 or BARK_PUSH.find("http") != -1:
        BARK_PUSH = "https://api.day.app/" + BARK_PUSH

    # telegram
    if os.environ['TG_BOT_TOKEN'] != "":
        TG_BOT_TOKEN = os.environ['TG_BOT_TOKEN']
    if os.environ['TG_USER_ID'] != "":
        TG_USER_ID = os.environ['TG_USER_ID']

    # 钉钉机器人
    if os.environ['DD_BOT_TOKEN'] != "":
        DD_BOT_TOKEN = os.environ['DD_BOT_TOKEN']
    if os.environ['DD_BOT_SECRET'] != "":
        DD_BOT_SECRET = os.environ['DD_BOT_SECRET']

    # QQ酷推
    # if os.environ['QQ_SKEY'] != "":
    #     QQ_SKEY = os.environ['QQ_SKEY']
    # if os.environ['QQ_MODE'] != "":
    #     QQ_MODE = os.environ['QQ_MODE']

    # 企业微信
    # if os.environ['QYWX_KEY'] != "":
    #     QQ_SKEY = os.environ['QYWX_KEY']
    if os.environ['QYWX_AM'] != "":
        QYWX_AM = os.environ['QYWX_AM']

    # push+
    if os.environ['PUSH_PLUS_TOKEN'] != "":
        PUSH_PLUS_TOKEN = os.environ['PUSH_PLUS_TOKEN']
    if os.environ['PUSH_PLUS_USER'] != "":
        PUSH_PLUS_USER = os.environ['PUSH_PLUS_USER']

    def serverNotify(self, text, desp):
        if sendNotify.SCKEY != '':
            url = 'https://sctapi.ftqq.com/' + sendNotify.SCKEY + '.send'
            if "\n" in desp:
                desp = desp.replace("\n", "\n\n")
            data = {
                'text': text,
                'desp': desp
            }
            response = json.dumps(requests.post(url, data).json(), ensure_ascii=False)
            datas = json.loads(response)
            # print(datas)
            if datas['code'] == 0:
                print('\nserver酱发送通知消息成功\n')
            elif datas['code'] == 40001:
                print('\nPUSH_KEY 错误\n')
            else:
                print('\n发送通知调用API失败！！\n')
        else:
            print('\n您未提供server酱的SCKEY，取消微信推送消息通知\n')
            pass

    def BarkNotify(self, text, desp):
        if sendNotify.BARK_PUSH != '':
            url = sendNotify.BARK_PUSH + '/' + urllib.parse.quote(text) + '/' + urllib.parse.quote(
                desp) + '?sound=' + sendNotify.BARK_SOUND
            headers = {'Content-type': "application/x-www-form-urlencoded"}
            response = json.dumps(requests.get(url, headers=headers).json(), ensure_ascii=False)
            data = json.loads(response)
            # print(data)
            if data['code'] == 400:
                print('\n找不到 Key 对应的 DeviceToken\n')
            elif data['code'] == 200:
                print('\nBark APP发送通知消息成功\n')
            else:
                print('\nBark APP发送通知调用API失败！！\n')
                print(data)
        else:
            print('\n您未提供Bark的APP推送BARK_PUSH，取消Bark推送消息通知\n')
            pass

    def tgBotNotify(self, text, desp):
        if sendNotify.TG_BOT_TOKEN != '' or sendNotify.TG_USER_ID != '':

            url = 'https://api.telegram.org/bot' + sendNotify.TG_BOT_TOKEN + '/sendMessage'
            headers = {'Content-type': "application/x-www-form-urlencoded"}
            body = 'chat_id=' + sendNotify.TG_USER_ID + '&text=' + urllib.parse.quote(
                text) + '\n\n' + urllib.parse.quote(desp) + '&disable_web_page_preview=true'
            response = json.dumps(requests.post(url, data=body, headers=headers).json(), ensure_ascii=False)

            data = json.loads(response)
            if data['ok']:
                print('\nTelegram发送通知消息完成\n')
            elif data['error_code'] == 400:
                print('\n请主动给bot发送一条消息并检查接收用户ID是否正确。\n')
            elif data['error_code'] == 401:
                print('\nTelegram bot token 填写错误。\n')
            else:
                print('\nTelegram bot发送通知调用API失败！！\n')
                print(data)
        else:
            print('\n您未提供Bark的APP推送BARK_PUSH，取消Bark推送消息通知\n')
            pass

    def dingNotify(self, text, desp):
        if sendNotify.DD_BOT_TOKEN != '':
            url = 'https://oapi.dingtalk.com/robot/send?access_token=' + sendNotify.DD_BOT_TOKEN
            data = {
                "msgtype": "text",
                "text": {
                    'content': text + desp
                }
            }
            headers = {
                'Content-Type': 'application/json;charset=utf-8'
            }
            if sendNotify.DD_BOT_SECRET != '':
                timestamp = str(round(time.time() * 1000))
                secret = sendNotify.DD_BOT_SECRET
                secret_enc = secret.encode('utf-8')
                string_to_sign = '{}\n{}'.format(timestamp, secret)
                string_to_sign_enc = string_to_sign.encode('utf-8')
                hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
                sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
                url = 'https://oapi.dingtalk.com/robot/send?access_token=' + sendNotify.DD_BOT_TOKEN + '&timestamp=' + timestamp + '&sign=' + sign

            response = requests.post(url=url, data=json.dumps(data), headers=headers).text
            if json.loads(response)['errcode'] == 0:
                print('\n钉钉发送通知消息成功\n')
            else:
                print('\n钉钉发送通知失败！！\n')
        else:
            print('\n您未提供钉钉的有关数据，取消钉钉推送消息通知\n')
            pass

    # def coolpush(self, text, desp):
    #     if sendNotify.QQ_SKEY != '':
    #         url = "https://push.xuthus.cc/" + sendNotify.QQ_MODE + "/" + sendNotify.QQ_SKEY
    #         params = {"c": desp, "t": text}
    #         headers = {'content-type': 'charset=utf8'}
    #         response = json.dumps(requests.post(url=url, params=params, headers=headers).json(),ensure_ascii=False)
    #         datas = json.loads(response)
    #
    #         if datas['code'] == 200:
    #             print('\nQQ推送发送通知消息成功\n')
    #         elif datas['code'] == 500:
    #             print('\nQQ推送QQ_SKEY错误\n')
    #         else:
    #             print('\n发送通知调用API失败！！\n')
    #
    #     else:
    #         print('\n您未提供酷推的SKEY，取消QQ推送消息通知\n')
    #         pass
    def pushNotify(self, text, desp):
        if sendNotify.PUSH_PLUS_TOKEN != '':
            url = 'http://www.pushplus.plus/send'
            data = {
                "token": sendNotify.PUSH_PLUS_TOKEN,
                "title": text,
                "content": desp
            }
            if sendNotify.PUSH_PLUS_USER != '':
                data = {
                    "token": sendNotify.PUSH_PLUS_TOKEN,
                    "title": text,
                    "content": desp,
                    "topic": sendNotify.PUSH_PLUS_USER,
                    "template": "html"
                }
            body = json.dumps(data).encode(encoding='utf-8')
            headers = {'Content-Type': 'application/json'}
            response = json.dumps(requests.post(url, data=body, headers=headers).json(), ensure_ascii=False)
            datas = json.loads(response)
            if datas['code'] == 200:
                print('\npush+发送通知消息成功\n')
            if datas['code'] == 600:
                print('\nPUSH_PLUS_TOKEN 错误\n')
            else:
                print('\npush+发送通知调用API失败！！\n')
        else:
            print('\n您未提供push+的PUSH_PLUS_TOKEN，取消push+推送消息通知\n')
            pass

    # 企业微信推送
    def sendWechat(self, desp):
        if sendNotify.QYWX_AM != '':
            # 获得access_token
            url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken'
            token_param = '?corpid=' + sendNotify.QYWX_AM.split(',')[0] + '&corpsecret=' + sendNotify.QYWX_AM.split(',')[1]
            token_data = requests.get(url + token_param)
            token_data.encoding = 'utf-8'
            token_data = token_data.json()
            access_token = token_data['access_token']
            #发送内容
            content = desp
            #创建要发送的消息
            data = {
                "touser": sendNotify.QYWX_AM.split(',')[2],
                "msgtype": "text",
                "agentid": sendNotify.QYWX_AM.split(',')[3],
                "text": {"content": content}
            }
            send_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + access_token
            message = requests.post(send_url, json=data)
            message.encoding = 'utf-8'
            res = message.json()
            print('企业微信推送 : ' + res['errmsg'])
        else:
            print('\n您未提供企业微信的QYWX_AM，取消企业微信推送消息通知\n')
            pass

    def send(self, **kwargs):
        send = sendNotify()
        title = kwargs.get("title", "")
        msg = kwargs.get("msg", "")
        send.serverNotify(title, msg)
        send.BarkNotify(title, msg)
        send.tgBotNotify(title, msg)
        send.dingNotify(title, msg)
        send.pushNotify(title, msg)
        send.sendWechat(msg)
        # send.coolpush(title,msg)

# if __name__ == "__main__":
#     send(title = '这是标题',msg = '这是内容')
