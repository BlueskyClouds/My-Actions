# !/usr/bin/env python
# coding=utf-8
import datetime
import random
import re
import sys
from io import StringIO

import cv2  # 图像处理模块
import numpy as np
import pytz

sys.path.append("My-Actions/function/wps")
from sendNotify import *

# Python版本 3.6, 该脚本仅供分享交流和学习, 不允许用于任何非法途径, 否则后果自负, 作者对此不承担任何责任
# 20210417更新: 添加WPS积分签到功能(个人使用强烈建议根据个人情况修改第28、42行);
# 请依次修改 28-36行中的需要修改的部分内容以实现推送功能，修改 39-58行中的需要修改的部分内容以实现签到功能
# 由于QPS限制，脚本完整运行时间为60-180秒，请谅解！
# 邀请用户签到可以额外获得会员, 每日可邀请最多10个用户, 已预置了12个小号用于接受邀请和会员群集结功能, 60-84行invite_sid信息可选删改
# 如邀请用户失效,请在相应60-84行处修改或相应位置前后增加invite_sid信息, 修改时注意逗号及保留双引号

# 参考以下代码解决https访问警告
# from requests.packages.urllib3.exceptions import InsecureRequestWarning,InsecurePlatformWarning
# requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
# requests.packages.urllib3.disable_warnings(InsecurePlatformWarning)

# 初始化信息
Wps_id = ''
sendNotify = sendNotify()
scf_environment = 0  # 本地环境运行选择0，scf云函数环境运行选择1

if os.environ['WPS_KEY'] != "":
    Wps_id = os.environ['WPS_KEY']
else:
    print("未填写WPS ID,取消运行")
    exit(0)

# 百度文字OCR获取地址[https://console.bce.baidu.com/ai/?fromai=1#/ai/ocr/app/list]
# 如需开启WPS微信积分签到，请获取并填写 client_id 和 client_secret
if os.environ['Orc_Id'] != "":
    client_id = os.environ['Orc_Id']
else:
    client_id = '*********复制百度文字OCR应用的API Key进来*************(保留引号)'

if os.environ['Orc_Secret'] != "":
    client_secret = os.environ['Orc_Secret']
else:
    client_secret = '*********复制百度文字OCR应用的Secret Key进来*************(保留引号)'

bdocr_loss = 0.95  # 微信积分签到验证时认为文字未倒置的置信度, 默认不修改
jifen_limit = 5  # WPS积分签到尝试次数，建议值为3-6，每次尝试最多会调用10次百度OCR接口，每人每天有500次高精度识别免费额度
data = {
    "wps_checkin": [
        {
            "name": "",
            "sid": Wps_id
        }
    ]
}
# 稻壳网页每月领取礼物开始日期, 无稻壳会员建议填25, 否则填0, 不得高于30
start_giftReceive_day = 0
# 是否显示WPS小程序邀请和会员群集结成功信息, 是填1, 否填0
success_info = 0
# 指定WPS小程序被有效邀请人数
invite_limit = 10
# 指定有效参与群集结人数, 减少因多余人数参与集结导致的invite_sid资源不足
mass_limit = 5
# 这12个账号被邀请,且参与WPS会员群集结,如群集结失败, 请修改以下sid, 修改时注意逗号及保留双引号
invite_sid = [
    {"name": "公共用户1",
     "sid": "V02S2UBSfNlvEprMOn70qP3jHPDqiZU00a7ef4a800341c7c3b"},
    {"name": "公共用户2",
     "sid": "V02SWIvKWYijG6Rggo4m0xvDKj1m7ew00a8e26d3002508b828"},
    {"name": "公共用户3",
     "sid": "V02Sr3nJ9IicoHWfeyQLiXgvrRpje6E00a240b890023270f97"},
    {"name": "公共用户4",
     "sid": "V02SBsNOf4sJZNFo4jOHdgHg7-2Tn1s00a338776000b669579"},
    {"name": "公共用户5",
     "sid": "V02S2oI49T-Jp0_zJKZ5U38dIUSIl8Q00aa679530026780e96"},
    {"name": "公共用户6",
     "sid": "V02ShotJqqiWyubCX0VWTlcbgcHqtSQ00a45564e002678124c"},
    {"name": "公共用户7",
     "sid": "V02SFiqdXRGnH5oAV2FmDDulZyGDL3M00a61660c0026781be1"},
    {"name": "公共用户8",
     "sid": "V02S7tldy5ltYcikCzJ8PJQDSy_ElEs00a327c3c0026782526"},
    {"name": "公共用户9",
     "sid": "V02SPoOluAnWda0dTBYTXpdetS97tyI00a16135e002684bb5c"},
    {"name": "公共用户10",
     "sid": "V02StVuaNcoKrZ3BuvJQ1FcFS_xnG2k00af250d4002664c02f"},
    {"name": "公共用户11",
     "sid": "V02Sb8gxW2inr6IDYrdHK_ywJnayd6s00ab7472b0026849b17"},
    {"name": "公共用户12",
     "sid": "V02SwV15KQ_8n6brU98_2kLnnFUDUOw00adf3fda0026934a7f"}
]

# 初始化日志
sio = StringIO('WPS签到日志\n\n')
sio.seek(0, 2)  # 将读写位置移动到结尾
dio = StringIO('')
# dio.seek(0, 2)
tmp_dir = os.path.abspath(os.path.dirname(__file__) + os.path.sep + "tmp")
s = requests.session()
s.cookies.clear()
tz = pytz.timezone('Asia/Shanghai')
nowtime = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
sio.write("---" + nowtime + "---\n\n")


# 获取百度ocr的token
def gettoken(id, secret):
    # 获取access_token
    # 文档https://cloud.baidu.com/doc/OCR/s/1k3h7y3db
    host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=' + id + '&client_secret=' + secret
    response = s.get(host)
    if response.status_code != 200:
        sio.write('百度文字识别Token获取失败, 不进行WPS微信积分签到! \n\n')
        # print('百度文字识别Token获取失败, 不进行WPS微信积分签到! \n\n')
        return
    tex = json.loads(response.text)
    token = tex['access_token']
    # sio.write("百度文字识别Token: {}\n\n".format(token))
    # print("百度文字识别Token: {}\n\n".format(token))
    return token


# wps积分签到
def wps_jifen_clockin(sid, headers: dict, bdocr_token):
    sio.write("          ---wps积分签到---↓\n\n")
    if len(sid) == 0:
        sio.write("签到失败: 用户sid为空, 请重新输入\n\n")
        return 0
    elif "*" in sid or sid[0] != "V":
        sio.write("签到失败: 用户sid错误, 请重新输入\n\n")
        return 0
    # 打卡签到
    clockin_url = 'https://vip.wps.cn/sign/v2'
    r = s.get('https://zt.wps.cn/spa/2019/vip_mobile_sign_v2/?from=wx_info_page', headers=headers)
    headers['content-type'] = 'application/x-www-form-urlencoded'
    r = s.post(clockin_url, headers=headers, data={'platform': 8})
    if len(r.history) != 0:
        if r.history[0].status_code == 302:
            sio.write("签到失败: 用户sid错误, 请重新输入\n\n")
            return 0
    resp = json.loads(r.text)
    headers.pop('content-type')
    # 判断是否已打卡
    if resp['msg'] == '已完成签到' or resp['msg'] == '10003':
        sio.write("签到信息: 今日已完成签到\n\n")
        return 1
    # 打卡签到需要参加活动
    elif resp['msg'] == 'need_captcha':
        # 提交答案
        answer_url = clockin_url
        for _ in range(jifen_limit):
            time.sleep(3)
            x_y = picocr(headers, bdocr_token)
            if not x_y:
                sio.write("获取坐标失败, 重新尝试\n\n")
                continue
            time.sleep(3)
            r = s.post(answer_url, headers=headers,
                       data={'platform': 8, 'captcha_pos': list2str(x_y), 'img_witdh': 280, 'img_height': 70.4})
            resp = json.loads(r.text)
            # 答案错误
            if resp['msg'] == 'captcha_not_match':
                sio.write("验证失败, 重新尝试\n\n")
                continue
            if resp['result'] == 'ok':
                sio.write("签到信息: 签到成功\n\n")
                sio.write("恭喜获得奖品: {}\n\n".format(resp['data']))
                return 1
        else:
            sio.write("{}次验证失败，WPS积分签到失败! \n\n".format(jifen_limit))
            return 2
    # 其他错误
    elif resp['result'] == 'ok':
        sio.write('签到信息: {}\n\n'.format(resp['data']))
        return 1
    else:
        sio.write('签到失败信息: {}\n\n'.format(r.text))
        return 2


# WPS积分签到验证码图片识别
def picocr(headers: dict, bdocr_token):
    url = 'https://vip.wps.cn/checkcode/signin/captcha.png?platform=8&encode=0&img_witdh=280&img_height=70.4'
    r = s.get(url, headers=headers)
    if r.status_code == 200:
        # 测试时去掉##dir = os.path.abspath(tmp_dir+os.path.sep+"original.png")#导出图片(原图)
        # 测试时去掉##fp = open(dir, 'wb')#导出图片(原图)
        # 测试时去掉##fp.write(r.content)#导出图片(原图)
        '''
        img = r.content
        img = Image.open(BytesIO(img))
        img.show()
        '''
        image = np.asarray(bytearray(r.content), dtype="uint8")
        img = cv2.imdecode(image, cv2.IMREAD_COLOR)  # 导入图片
        img = cv2.copyMakeBorder(img, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=[255, 255, 255])  # 图片扩充
        result = img.copy()
        return magic(img, result, bdocr_token)
    return []


# 获取验证图片中的文字块
def magic(img, result, bdocr_token):
    # 二值化
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 190, 255, cv2.THRESH_BINARY)  # 二值化(190-255变0-->这个范围的变成白色
    # 测试时去掉##cv2.iwrite(os.path.abspath(tmp_dir+os.path.sep+"gray.png"), thresh)#导出图片(二值化)

    # 形态学图像处理（膨胀腐蚀）###让轮廓更明显
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (6, 10))
    eroded = cv2.erode(thresh, kernel)
    # 测试时去掉##cv2.iwrite(os.path.abspath(tmp_dir+os.path.sep+"eroded.png"), eroded)#导出图片(加粗)

    # 轮廓检测
    contours, _ = cv2.findContours(eroded, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    '''
    contours:轮廓(很多个特征点)
    hierarchy:层次
    第二个参数表示轮廓的检索模式，有四种（本文介绍的都是新的cv2接口）：
        cv2.RETRY_EXTERNAL表示只检测外轮廓
        cv2.RETRY_LIST检测的轮廓不建立等级关系
        cv2.RETRY_COMP建立两个等级的轮廓，上面的一层为外边界，里面的一层为内孔的边界信息。如果内孔内还有一个连通物体，这个物体的边界也在顶层。
        cv2.RETRY_TREE建立一个等级树结构的轮廓。
    第三个参数method为轮廓的近似办法
        cv2.CHAIN_APPROX_NONE存储所有的轮廓点，相邻的两个点的像素位置差不超过1，即max（abs（x1-x2），abs（y2-y1））==1
        cv2.CHAIN_APPROX_SIMPLE压缩水平方向，垂直方向，对角线方向的元素，只保留该方向的终点坐标，例如一个矩形轮廓只需4个点来保存轮廓信息
    返回值{Contours()很多个轮廓的list}
        cv2.findContours()函数首先返回一个list值，[list]中每个元素都是图像中的一个[轮廓]也就我们要用到的[contours]
    '''

    color = (0, 255, 0)  # 画边界矩阵的颜色(0,255,0是纯绿色)第一位是红最后是蓝
    # 选取边界矩形
    temps = []  # 识别出的文字列表
    tmp = []  # 反转字体列表
    for c in contours[1:]:
        x, y, w, h = cv2.boundingRect(c)  # x，y是矩阵左上点的坐标，w，h是矩阵的宽和高。
        if w > 90 or h > 80:
            temps.append((x, y, w // 2, h))
            temps.append((x + w // 2, y, w // 2, h))
            continue
        if w > 20 and h > 20:
            temps.append((x, y, w, h))
    for x, y, w, h in temps:
        # sio.write("识别文字坐标: x={}, y={}, w={}, h={}\n\n".format(x,y,w,h))
        # 测试时去掉##sio.write("对应图片名字: {}-{}.png\n\n".format(x-10,y-10))
        # print("识别文字坐标: x={}, y={}, w={}, h={}\n\n".format(x,y,w,h))
        cv2.rectangle(img, (x, y), (x + w, y + h), color, 1)  # rectangle划线
        # temp = result[y:(y + h), x:(x + w)]#对result切割
        temp = thresh[y:(y + h), x:(x + w)]  # 对result切割#单字
        temp2 = temp.copy()
        # 测试时去掉##cv2.iwrite(os.path.abspath(tmp_dir+os.path.sep+str(x-10)+"-"+str(y-10)+".png"), temp)
        # 通过ROI将每张图片输出(导出)+ str(i)
        image_code = str(base64.b64encode(cv2.imencode('.png', temp)[1].tobytes()))[2:-1]  # 图片转base64？
        res = shibie(image_code, bdocr_token)
        if not res:
            sio.write("百度API调用失败, 结束当前积分签到！\n\n")
            return
        time.sleep(1)
        if not res['words_result'] or res['words_result'][0]['probability']['average'] < bdocr_loss:
            matRotate = cv2.getRotationMatrix2D((h * 0.5, w * 0.5), 180, 0.9)
            temp2 = cv2.warpAffine(temp, matRotate, (h, w), borderValue=(255, 255, 255))
            image_code2 = str(base64.b64encode(cv2.imencode('.png', temp2)[1].tobytes()))[2:-1]  # 图片转base64
            res2 = shibie(image_code2, bdocr_token)
            if not res2['words_result']:  # 两次都检查不到，那就装死得了，也不知道是不是图片有错|第一次能识别第二次（翻转）反而不能了，那就是本来正常字
                continue
            if not res['words_result'] or res2['words_result'][0]['probability']['average'] > \
                    res['words_result'][0]['probability']['average']:  # 反过来反而高了，本来是倒转
                circle(tmp, img, x, y, w, h)
    sio.write("倒置文字坐标:\n\n{}\n\n".format(tmp))
    # print("倒置文字坐标: {}\n\n".format(tmp))
    if scf_environment == 0:
        cv2.imwrite(os.path.abspath(tmp_dir + os.path.sep + "result.png"), img)  # 导出图片(画有边框的)
        sio.write('验证图片识别结果: {} \n\n'.format(upload(os.path.abspath(tmp_dir + os.path.sep + "result.png"))))
    return (tmp)


def circle(tmp, img, x, y, w, h):
    tmp.append((x - 10 + w // 2 + random.random(), y - 10 + h // 2 + random.random()))
    cv2.circle(img, (x - 10 + w // 2, y - 10 + h // 2), 3, (0, 0, 255), 0)


def shibie(img, token):
    request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic"  # 通用高精度(500次一天)
    params = {"image": img}
    access_token = token
    request_url = request_url + "?access_token=" + access_token + '&probability=true'
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response = requests.post(request_url, data=params, headers=headers)
    time.sleep(1)
    if response.status_code == 200:
        result_json = response.json()
        # if result_json['words_result']:
        #     sio.write("文字识别结果: {}\n\n".format(result_json['words_result'][0]['words']))
        # else:
        #     sio.write("文字识别结果: None\n\n")
        # print("文字识别结果:{}\n\n".format(result_json))
        return result_json


def list2str(x_y):
    res = ''
    if x_y:
        for i in x_y:
            res += str("{:.14f}".format(i[0]) + ',' + "{:.14f}".format(i[1]) + '|')
        res = res[:-1]
    return res


def file_set(file=None, type=None):
    if not os.path.exists(file):
        if not os.path.exists(os.path.dirname(file)):
            os.makedirs(os.path.dirname(file))
        if type == 'dir':
            os.makedirs(file)
        if type == 'file':
            with open(file, 'wb+') as handle:
                handle.close()
        if not os.path.exists(file):
            if os.path.isdir(file):
                os.makedirs(file)
            elif os.path.isfile(file):
                if not os.path.exists(os.path.dirname(file)):
                    os.makedirs(os.path.dirname(file))
                with open(file, 'wb+') as handle:
                    handle.close()
        return 0
    return 1


def upload(path):
    headers = {'Authorization': ''}
    files = {'smfile': open(path, 'rb')}
    url = 'https://sm.ms/api/v2/upload'
    res = requests.post(url, files=files, headers=headers).json()
    if res['code'] == 'success':
        return res['data']['url']
    elif res['code'] == 'image_repeated':
        return res['images']
    else:
        sio.write("上传https://sm.ms 图床失败: {}".format(res['message']))
        return res['message']


# wps网页签到
def wps_webpage_clockin(sid: str, headers: dict):
    sio.write("          ---wps网页签到---↓\n\n")
    if len(sid) == 0:
        sio.write("签到失败: 用户sid为空, 请重新输入\n\n")
        return 0
    elif "*" in sid or sid[0] != "V":
        sio.write("签到失败: 用户sid错误, 请重新输入\n\n")
        return 0
    # 打卡签到
    clockin_url = 'https://vip.wps.cn/sigin/do'
    r = s.post(clockin_url, headers=headers)
    if len(r.history) != 0:
        if r.history[0].status_code == 302:
            sio.write("签到失败: 用户sid错误, 请重新输入\n\n")
            return 0
    resp = json.loads(r.text)
    # 判断是否已打卡
    if resp['msg'] == '已完成签到':
        sio.write("签到信息: 今日{}\n\n".format(resp['msg']))
        return 1
    # 打卡签到需要参加活动
    elif resp['msg'] == 'need_captcha':
        getquestion_url = 'https://vip.wps.cn/checkcode/signin/question'
        r = s.get(getquestion_url, headers=headers)
        '''
        {
            "result": "ok",
            "data": {
                "multi_select": 1,
                "options": [
                    "30天文档分享链接有效期",
                    "远程下载助手",
                    "输出长图片去水印",
                    "PDF转图片"
                ],
                "title": "以下哪些特权是WPS会员和超级会员共同拥有的？"
            },
            "msg": ""
        }
        '''
        answer_set = {
            'WPS会员全文检索',
            '100G',
            'WPS会员数据恢复',
            'WPS会员PDF转doc',
            'WPS会员PDF转图片',
            'WPS图片转PDF插件',
            '金山PDF转WORD',
            'WPS会员拍照转文字',
            '使用WPS会员修复',
            'WPS全文检索功能',
            '有，且无限次',
            '文档修复'
        }
        resp = json.loads(r.text)
        # sio.write(resp['data']['multi_select'])
        # 只做单选题 multi_select==1表示多选题
        while resp['data']['multi_select'] == 1:
            r = s.get(getquestion_url, headers=headers)
            resp = json.loads(r.text)
            # sio.write('选择题类型: {}'.format(resp['data']['multi_select']))
        answer_id = 3
        for i in range(4):
            opt = resp['data']['options'][i]
            if opt in answer_set:
                answer_id = i + 1
                break
        sio.write("选项: {}\n\n".format(resp['data']['options']))
        sio.write("选择答案: {}\n\n".format(answer_id))
        # 提交答案
        answer_url = 'https://vip.wps.cn/sigin/do'
        r = s.post(answer_url, headers=headers, data={'platform': 2, 'answer': answer_id, 'auth_type': 'answer'})
        resp = json.loads(r.text)
        # 答案错误
        if resp['msg'] == 'wrong answer':
            sio.write("答案不对, 挨个尝试\n\n")
            for i in range(4):
                r = s.post(answer_url, headers=headers, data={'platform': 2, 'answer': i + 1, 'auth_type': 'answer'})
                resp = json.loads(r.text)
                sio.write(i + 1)
                if resp['result'] == 'ok':
                    break
        # 打卡签到
        sio.write("签到信息: 签到成功\n\n")
        if 'gift_name' in resp:
            sio.write("恭喜获得奖品: {}\n\n".format(resp['gift_name']))
            if 'url' in resp['data']:
                sio.write("领取地址: {}\n\n".format(resp['url']))
        return 1
    # 其他错误
    elif resp['result'] == 'ok':
        sio.write('签到信息: {}\n\n'.format(r.text))
        return 1
    else:
        sio.write('签到失败信息: {}\n\n'.format(r.text))
        return 1


# wps网页任务提示
def wps_webpage_taskreward(headers: dict):
    tasklist_url = 'https://vipapi.wps.cn/task_center/task/list'
    r = s.post(tasklist_url, headers=headers)
    if len(r.history) != 0:
        if r.history[0].status_code == 302:
            sio.write("任务检查失败: 用户sid错误, 请重新输入\n\n")
            return 0
    resp = json.loads(r.text)
    # 完善账户信息任务检查
    resplist = ([resp['data']['1']['task'], resp['data']['2']['task'],
                 resp['data']['3']['task']])
    for i in range(len(resplist)):
        checkinformation(resplist[i], headers)


# 检查wps网页任务提示信息
def checkinformation(information, headers: dict):
    for i in range(len(information)):
        if information[i]['status'] == 0:
            fetchMission_url = 'https://vipapi.wps.cn/task_center/task/receive_task'
            r = s.post(fetchMission_url, data={'id': information[i]['id']}, headers=headers)
            resp = json.loads(r.text)
            sio.write("任务{} “{}”领取情况: {}\n\n".format(information[i]['id'], information[i]['taskName'], resp['msg']))
        elif information[i]['status'] == 1:
            sio.write("任务{} “{}”未完成".format(information[i]['id'], information[i]['taskName']))
            if len(information[i]['prizes']) > 0:
                sio.write(",手动完成可获得")
                for j in range(len(information[i]['prizes'])):
                    sio.write("{}{}{} ".format(
                        information[i]['prizes'][j]['name'], information[i]['prizes'][j]['num'],
                        information[i]['prizes'][j]['size']))
            sio.write("\n\n")
        elif information[i]['status'] == 2:
            sio.write("任务{} “{}”已完成".format(information[i]['id'], information[i]['taskName']))
            if len(information[i]['prizes']) > 0:
                sio.write(",可获得")
                for j in range(len(information[i]['prizes'])):
                    sio.write("{}{}{} ".format(
                        information[i]['prizes'][j]['name'], information[i]['prizes'][j]['num'],
                        information[i]['prizes'][j]['size']))
            fetchReward_url = 'https://vipapi.wps.cn/task_center/task/receive_reward'
            s.post(fetchReward_url, data={'id': information[i]['id']}, headers=headers)
            sio.write("已自动为您领取奖励\n\n")
        else:
            pass


# Docer网页签到
def docer_webpage_clockin(headers: dict):
    sio.write("\n\n          ---稻壳网页签到---↓\n\n")
    docer_url = 'https://zt.wps.cn/2018/docer_check_in/api/checkin_today'
    r = s.post(docer_url, headers=headers)
    if len(r.history) != 0:
        if r.history[0].status_code == 302:
            sio.write("签到失败: 用户sid错误, 请重新输入\n\n")
            return 0
    resp = json.loads(r.text)
    if resp['result'] == 'ok':
        sio.write("签到信息: {}\n\n".format(r.text))
        return 1
    elif resp['msg'] == 'recheckin':
        sio.write('签到信息: 重复签到\n\n')
        return 1


# Docer网页补签
def docer_webpage_earlyclockin(headers: dict, checkinEarly_times, checkinrecord, max_days):
    now = datetime.datetime.now(tz)
    this_month_start = datetime.datetime(now.year, now.month, 1).date()
    checkin_Earliestdate = datetime.datetime.strptime(checkinrecord[0]['checkin_date'], '%Y-%m-%d').date()
    for i in range(checkinEarly_times):
        if checkin_Earliestdate.day > this_month_start.day:
            checkin_date = checkin_Earliestdate - datetime.timedelta(days=(i + 1))
            checkin_date = datetime.datetime.strptime(str(checkin_date), '%Y-%m-%d').strftime('%Y%m%d')
            checkinEarly_url = 'https://zt.wps.cn/2018/docer_check_in/api/checkin_early'
            s.post(checkinEarly_url, data={'date': checkin_date}, headers=headers)
        else:
            if i == 0:
                sio.write('无需补签\n\n')
                return max_days
            else:
                sio.write('使用补签卡{}张\n\n'.format(i))
                checinRecord_url = 'https://zt.wps.cn/2018/docer_check_in/api/checkin_record'
                r = s.get(checinRecord_url, headers=headers)
                resp = json.loads(r.text)
                sio.write('补签后连续签到: {}天\n\n'.format(resp['data']['max_days']))
                return resp['data']['max_days']
    sio.write('使用补签卡{}张\n\n'.format(i))
    checinRecord_url = 'https://zt.wps.cn/2018/docer_check_in/api/checkin_record'
    r = s.get(checinRecord_url, headers=headers)
    resp = json.loads(r.text)
    sio.write('补签后连续签到: {}天\n\n'.format(resp['data']['max_days']))
    return resp['data']['max_days']


# Docer网页领取礼物
def docer_webpage_giftReceive(headers: dict, max_days):
    userinfo_url = 'https://vip.wps.cn/userinfo'
    r = s.get(userinfo_url, headers=headers)
    resp = json.loads(r.text)
    memberid = [0]
    if len(resp['data']['vip']['enabled']) > 0:
        for i in range(len(resp['data']['vip']['enabled'])):
            memberid.append(resp['data']['vip']['enabled'][i]['memberid'])
    rewardRecord_url = 'https://zt.wps.cn/2018/docer_check_in/api/reward_record'
    rewardReceive_url = 'https://zt.wps.cn/2018/docer_check_in/api/receive_reward'
    r = s.get(rewardRecord_url, headers=headers)
    resp = json.loads(r.text)
    rewardRecord_list = resp['data']
    if len(rewardRecord_list) > 0:
        for i in rewardRecord_list:
            if i['reward_type'] == 'vip' or i['reward_type'] == 'code':
                if int(i['limit_days']) <= max_days and int(i['limit_vip']) in memberid and i[
                    'status'] == 'unreceived' and max_days >= start_giftReceive_day:
                    r1 = s.post(rewardReceive_url, data={'reward_id': i['id'], 'receive_from': 'pc_client'},
                                headers=headers)
                    sio.write('领取礼物: {} '.format(i['reward_name']))
                    if 'reward_info' in r1.text:
                        resp1 = json.loads(r1.text)
                        sio.write('礼物信息: {}'.format(resp1['data']['reward_info']))
                    else:
                        sio.write('领取信息: {}'.format(r1.text))
                    sio.write('\n\n')
                elif i['status'] == 'received':
                    sio.write('已领取礼物: {} '.format(i['reward_name']))
                    if 'reward_info' in i:
                        sio.write('礼物信息: {}'.format(i['reward_info']))
                    sio.write('\n\n')


# wps小程序签到
def wps_miniprogram_clockin(sid: str):
    # sio.write("\n\n          ---wps小程序签到---↓\n\n")
    if len(sid) == 0:
        # sio.write("签到失败: 用户sid为空, 请重新输入\n\n")
        return 0
    elif "*" in sid or sid[0] != "V":
        # sio.write("签到失败: 用户sid错误, 请重新输入\n\n")
        return 0
    # 打卡签到
    clockin_url = 'http://zt.wps.cn/2018/clock_in/api/clock_in'
    r = s.get(clockin_url, headers={'sid': sid})
    if len(r.history) != 0:
        if r.history[0].status_code == 302:
            # sio.write("签到失败: 用户sid错误, 请重新输入\n\n")
            return 0
    try:
        resp = json.loads(r.text)
    except:
        # sio.write("签到失败: {}\n\n".format(r.text))
        return 0
    # 判断是否已打卡
    if resp['msg'] == '已打卡':
        sio.write("签到信息: {}\n\n".format(r.text))
        return 1
    # 判断是否绑定手机
    elif resp['msg'] == '未绑定手机':
        sio.write('签到失败: 未绑定手机, 请绑定手机后重新运行签到\n\n')
        return 0
    # 判断是否重新报名
    elif resp['msg'] == '前一天未报名':
        sio.write('前一天未报名\n\n')
        signup_url = 'http://zt.wps.cn/2018/clock_in/api/sign_up'
        r = s.get(signup_url, headers={'sid': sid})
        resp = json.loads(r.text)
        if resp['result'] == 'ok':
            sio.write('报名信息: 已自动报名, 报名后第二天签到\n\n')
            return 2
        else:
            sio.write('报名失败: 请手动报名, 报名后第二天签到\n\n')
            return 0
    # 打卡签到需要参加活动
    elif resp['msg'] == '答题未通过':
        getquestion_url = 'http://zt.wps.cn/2018/clock_in/api/get_question?member=wps'
        r = s.get(getquestion_url, headers={'sid': sid})
        answer_set = {
            'WPS会员全文检索',
            '100G',
            'WPS会员数据恢复',
            'WPS会员PDF转doc',
            'WPS会员PDF转图片',
            'WPS图片转PDF插件',
            '金山PDF转WORD',
            'WPS会员拍照转文字',
            '使用WPS会员修复',
            'WPS全文检索功能',
            '有，且无限次',
            '文档修复'
        }
        resp = json.loads(r.text)
        # sio.write(resp['data']['multi_select'])
        # 只做单选题 multi_select==1表示多选题
        while resp['data']['multi_select'] == 1:
            r = s.get(getquestion_url, headers={'sid': sid})
            resp = json.loads(r.text)
            # sio.write('选择题类型: {}'.format(resp['data']['multi_select']))
        answer_id = 3
        for i in range(4):
            opt = resp['data']['options'][i]
            if opt in answer_set:
                answer_id = i + 1
                break
        sio.write("选项: {}\n\n".format(resp['data']['options']))
        sio.write("选择答案: {}\n\n".format(answer_id))
        # 提交答案
        answer_url = 'http://zt.wps.cn/2018/clock_in/api/answer?member=wps'
        r = s.post(answer_url, headers={'sid': sid}, data={'answer': answer_id})
        resp = json.loads(r.text)
        # 答案错误
        if resp['msg'] == 'wrong answer':
            sio.write("答案不对, 挨个尝试\n\n")
            for i in range(4):
                r = s.post(answer_url, headers={'sid': sid}, data={'answer': i + 1})
                resp = json.loads(r.text)
                sio.write(i + 1)
                if resp['result'] == 'ok':
                    sio.write(r.text)
                    break
        # 打卡签到
        clockin_url = 'http://zt.wps.cn/2018/clock_in/api/clock_in?member=wps'
        r = s.get(clockin_url, headers={'sid': sid})
        try:
            resp = json.loads(r.text)
            sio.write("签到信息: {}\n\n".format(resp['msg']))
        except:
            sio.write("签到信息: {}\n\n".format(r.text))
        return 1
    elif resp['msg'] == 'ParamData Empty':
        # sio.write('签到失败信息: {}\n\n'.format(r.text))
        signup_url = 'http://zt.wps.cn/2018/clock_in/api/sign_up'
        r = s.get(signup_url, headers={'sid': sid})
        # sio.write('签到接口失效, 请手动打卡\n\n')
        return 2
    elif resp['msg'] == '不在打卡时间内':
        # sio.write('签到失败: 不在打卡时间内\n\n')
        signup_url = 'http://zt.wps.cn/2018/clock_in/api/sign_up'
        r = s.get(signup_url, headers={'sid': sid})
        resp = json.loads(r.text)
        if resp['result'] == 'ok':
            sio.write('已自动报名, 报名后请设置在规定时间内签到\n\n')
            return 2
        else:
            sio.write('报名失败: 请手动报名, 报名后第二天签到\n\n')
            return 0
    # 其他错误
    elif resp['result'] == 'error':
        try:
            resp = json.loads(r.text)
            sio.write("签到失败信息: {}\n\n".format(resp['msg']))
        except:
            sio.write("签到失败信息: {}\n\n".format(r.text))
        signup_url = 'http://zt.wps.cn/2018/clock_in/api/sign_up'
        r = s.get(signup_url, headers={'sid': sid})
        resp = json.loads(r.text)
        if resp['result'] == 'ok':
            sio.write('已自动报名, 报名后请设置在规定时间内签到\n\n')
            return 2
        else:
            sio.write('报名失败: 请手动报名, 报名后第二天签到\n\n')
            return 0


# wps小程序接受邀请
def wps_miniprogram_invite(sid: list, invite_userid: int) -> None:
    invite_url = 'http://zt.wps.cn/2018/clock_in/api/invite'
    k = 0
    for index in range(len(sid)):
        if k < invite_limit:
            headers = {
                'sid': sid[index]['sid']
            }
            r = s.post(invite_url, headers=headers, allow_redirects=False, data={
                'invite_userid': invite_userid, "client_code": "040ce6c23213494c8de9653e0074YX30", "client": "alipay"})
            if r.status_code == 200:
                try:
                    resp = json.loads(r.text)
                    if resp['result'] == 'ok':
                        if success_info == 1:
                            sio.write("邀请对象: {}, Result: {}\n\n".format(sid[index]['name'], resp['result']))
                        k += 1
                    elif resp['msg'] == 'tryLater':
                        sio.write("邀请对象: {}, Result: {}\n\n".format(sid[index]['name'], resp['msg']))
                    else:
                        sio.write("邀请对象: {}, Result: {}\n\n".format(sid[index]['name'], resp['result']))
                except:
                    resp = r.text[:25]
                    sio.write("邀请对象: {}, Result: ID已失效\n\n".format(sid[index]['name']))
            else:
                sio.write("邀请对象: {}, 状态码: {},\n\n 请求信息{}\n\n".format(sid[index]['name'], r.status_code, r.text[:25]))
        else:
            break
        t = random.uniform(3.0, 6.0)
        time.sleep(t)
    return k


# wps会员群集结
# 活动地址: WPS会员公众号-福利签到-打卡免费领会员-群集结
# 奖励: 集结成功3次,获得6天会员+10M空间
#      最好换4个自己小号的sid,默认的可能用的人多就没次数了
def wps_massing(*args):
    sid = data['wps_checkin']
    sio.write("\n\n          ---wps会员群集结---↓\n\n")
    for item in sid:
        sio.write("为{}进行会员群集结\n\n".format(item['name']))
        time = wps_massing_info(item['sid'], 0)
        if time < 3:
            for i in range(3 - time):
                code = wps_massing_group(item['sid'])
                if code:
                    k = wps_massing_join(code, invite_sid)
                    if k < 5:
                        sio.write("第{}次集结失败, 当前集结{}人!!!\n\n".format(i + time, k))
                        dio.write("第{}次WPS会员群集结失败\n\n".format(i + time))
                        time = wps_massing_info(item['sid'], 2)
                        break
            time = wps_massing_info(item['sid'], 0)
            if time >= 3:
                sio.write("{}次WPS会员群集结成功\n\n".format(time))
                dio.write("{}次WPS会员群集结成功\n\n".format(time))
        else:
            sio.write("{}次WPS会员群集结成功\n\n".format(time))
            dio.write("已参与{}次会员群集结\n\n".format(time))
        wps_massing_info(item['sid'], 1)
    desp = sio.getvalue()
    digest = dio.getvalue()

    sendNotify.send(title=digest, msg=desp)
    print(desp)
    return desp


# wps会员群集结开团
def wps_massing_group(sid):
    massing_url = 'https://zt.wps.cn/2020/massing/api'
    r = s.post(massing_url, headers={'sid': sid})
    resp = json.loads(r.text)
    code = ''
    if resp['result'] == "error" and resp['msg'] == "up to limit":
        sio.write("今日集结次数已达到上限,请明日再来\n\n")
    elif resp['data'] and resp['data']['code']:
        code = resp['data']['code']
        sio.write("开团成功, code: " + code + '\n\n')
    else:
        r1 = s.get(massing_url, headers={'sid': sid})
        resp1 = json.loads(r1.text)
        if 'latest_record' in resp1['data']:
            code = resp1['data']['latest_record']['code']
            sio.write("开团成功, code: " + code + '\n\n')
        else:
            sio.write(resp['msg'] + '\n\n')
    return code


# wps会员群集结参团
def wps_massing_join(code, sid):
    massing_url = 'https://zt.wps.cn/2020/massing/api'
    k = 1
    for index in range(len(sid)):
        if k < mass_limit:
            headers = {
                'sid': sid[index]['sid']
            }
            r = s.post(massing_url, data={'code': code}, headers=headers)
            if r.status_code == 200:
                try:
                    resp = json.loads(r.text)
                    if resp['result'] == 'error':
                        sio.write("参团对象: {}, Result: {}\n\n".format(sid[index]['name'], resp['msg']))
                    elif resp['result'] == 'ok':
                        if success_info == 1:
                            sio.write("参团对象: {}, Result: {}\n\n".format(sid[index]['name'], resp['result']))
                        k += 1
                except:
                    resp = r.text[:25]
                    sio.write("参团对象: {}, Result: ID已失效\n\n".format(sid[index]['name']))
            else:
                sio.write(
                    "参团对象ID={}, 状态码: {},\n\n  请求信息: {}\n\n".format(sid[index]['name'], r.status_code, r.text[:25]))
        else:
            break
    return k


# wps会员群集结信息
def wps_massing_info(sid, c):
    massing_url = 'https://zt.wps.cn/2020/massing/api'
    r = s.get(massing_url, headers={'sid': sid})
    resp = json.loads(r.text)
    time = 0
    if resp['result'] == "ok" and resp['data'] and resp['data']['reward']:
        reward = resp['data']['reward']
        time = reward['time']
        if time != 0 and c == 1:
            sio.write('今日集结' + str(reward['time']) + '次,共集结' + str(reward['total_time']) + '次;\n\n获得' + str(
                reward['member']) + '天会员,' + str(reward['drive']) + 'M空间\n\n')
        if 'latest_record' in resp['data'] and c == 2:
            create_time = resp['data']['latest_record']['create_time']
            ts2str_url = 'https://api.a76yyyy.cn/time?function=timestamp2str'
            r1 = s.post(ts2str_url, data={'params1': str(int(create_time) + 1800)})
            resp1 = json.loads(r1.text)
            sio.write("下次集结开团时间:" + resp1['data'] + '\n\n')
    else:
        sio.write("sid已失效,请重新获取sid\n\n")
    return time


def csrf():
    charts = 'ABCDEFGHIJKLMNOPQRSTWXYZadcdedfghijklmnopqrstwxyz234567'
    length = len(charts)
    csrftoken = []
    for _ in range(32):
        csrftoken.append(charts[random.randint(0, length - 1)])
    return "".join(csrftoken)


# 主函数
def main():
    # sio.write("\n            ===模拟WPS签到===")
    sid = data['wps_checkin']
    bdocr_token = gettoken(client_id, client_secret)
    file_set(tmp_dir, 'dir')
    for item in sid:
        sio.write("---为{}签到---↓\n\n".format(item['name']))
        dio.write("{}签到摘要↓\n\n".format(item['name']))
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36'}
        s.headers.update(headers)
        s.cookies.update({'wps_sid': item['sid'], 'csrf': csrf()})
        if bdocr_token:
            j = wps_jifen_clockin(item['sid'], headers, bdocr_token)
            if j == 1:
                dio.write("wps积分签到成功\n\n")
                time.sleep(10)
            elif j == 2:
                dio.write("wps积分签到失败\n\n")
                time.sleep(10)
            else:
                dio.write("wps积分签到失败\n\n")
                desp = sio.getvalue()
                digest = dio.getvalue()
                if digest[-2:] == '\n\n':
                    digest = digest[0:-2]
                sendNotify.send(title=digest, msg=desp)
                print(desp)
                return desp
        b0 = wps_webpage_clockin(item['sid'], headers)
        if b0 == 1:
            # 获取当前网页签到信息
            # dio.write("wps网页签到成功\n\n")
            taskcenter_url = 'https://vipapi.wps.cn/task_center/task/summary'
            r = s.post(taskcenter_url, headers=headers)
            resp = json.loads(r.text)
            if resp['data']['taskNum'] < 12:
                wps_webpage_taskreward(headers)
            r = s.post(taskcenter_url, headers=headers)
            resp = json.loads(r.text)
            sio.write('已领取积分: {}\n\n'.format(resp['data']['wpsIntegral']))
            sio.write('已领取会员: {}天\n\n'.format(resp['data']['member']))
            sio.write('已完成任务: {}项\n\n'.format(resp['data']['taskNum']))
        else:
            dio.write("wps网页签到失败\n\n")
            desp = sio.getvalue()
            digest = dio.getvalue()
            if digest[-2:] == '\n\n':
                digest = digest[0:-2]
            sendNotify.send(title=digest, msg=desp)
            # print(desp)
            # return desp
        b1 = docer_webpage_clockin(headers)
        if b1 == 1:
            checinRecord_url = 'https://zt.wps.cn/2018/docer_check_in/api/checkin_record'
            r = s.get(checinRecord_url, headers=headers)
            resp = json.loads(r.text)
            sio.write('本期连续签到: {}天\n\n'.format(resp['data']['max_days']))
            checkinEarlytimes_url = 'https://zt.wps.cn/2018/docer_check_in/api/checkin_early_times'
            r1 = s.get(checkinEarlytimes_url, headers=headers)
            resp1 = json.loads(r1.text)
            sio.write('拥有补签卡: {}张\n\n'.format(resp1['data']))
            max_days = resp['data']['max_days']
            if resp1['data'] > 0 and len(resp['data']['records']) > 0:
                max_days = docer_webpage_earlyclockin(headers, resp1['data'], resp['data']['records'], max_days)
            if len(resp['data']['records']) > 0:
                docer_webpage_giftReceive(headers, max_days)
            dio.write("稻壳网页签到成功\n\n")
        else:
            dio.write("稻壳网页签到失败\n\n")

        b2 = wps_miniprogram_clockin(item['sid'])
        if b2 == 1 or b2 == 2:
            # 获取小程序当前会员奖励信息
            member_url = 'https://zt.wps.cn/2018/clock_in/api/get_data?member=wps'
            r = s.get(member_url, headers={'sid': item['sid']})
            # 累计在小程序打卡中获得会员天数
            total_add_day = re.search('"total_add_day":(\d+)', r.text).group(1)
            sio.write('小程序打卡中累计获得会员: {}天\n\n'.format(total_add_day))
            if b2 == 1:
                dio.write("小程序打卡成功\n\n")
            else:
                dio.write("小程序打卡中断\n\n")
        else:
            dio.write("小程序打卡失败\n\n")

        # wps签到邀请
        sio.write("\n\n          ---wps小程序邀请---↓\n\n")
        sio.write("为{}邀请\n\n".format(item['name']))
        userinfo_url = 'https://vip.wps.cn/userinfo'
        r = s.get(userinfo_url, headers={'sid': item['sid']})
        resp = json.loads(r.text)
        if type(resp['data']['userid']) == int:
            k = wps_miniprogram_invite(invite_sid, resp['data']['userid'])
            member_url = 'https://zt.wps.cn/2018/clock_in/api/get_data?member=wps'
            r = s.get(member_url, headers={'sid': item['sid']})
            resp = json.loads(r.text)
            # 累计在小程序邀请中邀请成功数
            invite_count = resp['invite_count']
            sio.write('邀请完成 {}人，邀请成功 {}人\n\n'.format(k, invite_count))
            dio.write('小程序成功邀请{}人\n\n'.format(invite_count))
        else:
            sio.write("邀请失败: 用户ID错误, 请检查用户sid\n\n")
            dio.write("小程序邀请失败\n\n")

        # 获取当前用户信息
        sio.write('\n\n          ---当前用户信息---↓\n\n')
        summary_url = 'https://vip.wps.cn/2019/user/summary'
        r = s.post(summary_url, headers=headers)
        resp = json.loads(r.text)
        sio.write('会员积分:{}\n\n"稻米数量":{}\n\n'.format(resp['data']['integral'], resp['data']['wealth']))
        userinfo_url = 'https://vip.wps.cn/userinfo'
        r = s.get(userinfo_url, headers=headers)
        resp = json.loads(r.text)
        if len(resp['data']['vip']['enabled']) > 0:
            sio.write('会员信息:\n\n')
            for i in range(len(resp['data']['vip']['enabled'])):
                sio.write('"类型":{}, "过期时间":{}\n\n'.format(resp['data']['vip']['enabled'][i]['name'],
                                                          datetime.datetime.fromtimestamp(
                                                              resp['data']['vip']['enabled'][i][
                                                                  'expire_time']).strftime("%Y--%m--%d %H:%M:%S")))
                dio.write('"类型":{}, "过期时间":{}\n\n'.format(resp['data']['vip']['enabled'][i]['name'],
                                                          datetime.datetime.fromtimestamp(
                                                              resp['data']['vip']['enabled'][i][
                                                                  'expire_time']).strftime("%Y/%m/%d")))

    desp = sio.getvalue()
    digest = dio.getvalue()
    sendNotify.send(title=digest, msg=desp)
    print(desp)


def main_handler(event, context):
    return main()


if __name__ == '__main__':
    main()
