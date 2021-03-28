# !/usr/bin/env python
# coding=utf-8
import requests
import time
import json
import sys
sys.path.append("My-Actions/function/")
import pytz
import datetime
import re
import os
from sendNotify import *
from io import StringIO

# Python版本 3.6, 该脚本仅供分享交流和学习, 不允许用于任何非法途径, 否则后果自负, 作者对此不承担任何责任
# 20210122更新: 添加WPS小程序会员群集结功能 (如需仅执行群集结功能, 请将执行方法由'index.main_handler'更改为'index.wps_massing' )
# 如群集结失败,请修改相应39-51行invite_sid信息
# 请依次修改 24、28、29行中的需要修改的部分内容
# 邀请用户签到可以额外获得会员, 每日可邀请最多10个用户, 已预置了13个小号用于接受邀请, 39-51行invite_sid信息可选删改

# 参考以下代码解决https访问警告
# from requests.packages.urllib3.exceptions import InsecureRequestWarning,InsecurePlatformWarning
# requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
# requests.packages.urllib3.disable_warnings(InsecurePlatformWarning)

# 初始化信息
Wps_id = ''
sendNotify = sendNotify()

if os.environ['WPS_KEY'] != "":
    Wps_id = os.environ['WPS_KEY']
else:
    print("未填写WPS ID,取消运行")
    exit(0)

data = {
    "wps_checkin": [
        {
            "name": "",
            "sid": Wps_id
        }
    ]
}
# 指定WPS小程序被有效邀请人数
invite_limit = 10
# 指定有效参与群集结人数, 减少因多余人数参与集结导致的invite_sid资源不足
mass_limit = 5
# 这13个账号被邀请,且参与WPS会员群集结,如群集结失败, 请修改以下sid, 修改时注意保留双引号
invite_sid = [
        "V02SC1mOHS0RiUBxeoA8NTliH2h2NGc00a803c35002693584d",
        "V02S2UBSfNlvEprMOn70qP3jHPDqiZU00a7ef4a800341c7c3b",
        "V02StVuaNcoKrZ3BuvJQ1FcFS_xnG2k00af250d4002664c02f",
        "V02SWIvKWYijG6Rggo4m0xvDKj1m7ew00a8e26d3002508b828",
        "V02Sr3nJ9IicoHWfeyQLiXgvrRpje6E00a240b890023270f97",
        "V02SBsNOf4sJZNFo4jOHdgHg7-2Tn1s00a338776000b669579",
        "V02ScVbtm2pQD49ArcgGLv360iqQFLs014c8062e000b6c37b6",
        "V02S2oI49T-Jp0_zJKZ5U38dIUSIl8Q00aa679530026780e96",
        "V02ShotJqqiWyubCX0VWTlcbgcHqtSQ00a45564e002678124c",
        "V02SFiqdXRGnH5oAV2FmDDulZyGDL3M00a61660c0026781be1",
        "V02S7tldy5ltYcikCzJ8PJQDSy_ElEs00a327c3c0026782526",
        "V02SPoOluAnWda0dTBYTXpdetS97tyI00a16135e002684bb5c",
        "V02Sb8gxW2inr6IDYrdHK_ywJnayd6s00ab7472b0026849b17",
        "V02SwV15KQ_8n6brU98_2kLnnFUDUOw00adf3fda0026934a7f",
        "V02SBpDdos7QiFOs_5TOLF0a80pWt-U00a94ce2c003a814a17",
]

# 初始化日志
sio = StringIO('WPS签到日志\n\n')
sio.seek(0, 2)  # 将读写位置移动到结尾
s = requests.session()
tz = pytz.timezone('Asia/Shanghai')
nowtime = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
sio.write("--------------------------"+nowtime+"----------------------------\n\n")

# 主函数
def main():
    # sio.write("\n            ===模拟WPS签到===")
    sid = data['wps_checkin']

    for item in sid:
        sio.write("---为{}签到---↓\n\n".format(item['name']))
        b0 = wps_webpage_clockin(item['sid'])
        if b0 == 1:
            # 获取当前网页签到信息
            taskcenter_url = 'https://vipapi.wps.cn/task_center/task/summary'
            r = s.post(taskcenter_url, headers={'sid': item['sid']})
            resp = json.loads(r.text)
            if resp['data']['taskNum'] < 12:
                wps_webpage_taskreward(item['sid'])
            r = s.post(taskcenter_url, headers={'sid': item['sid']})
            resp = json.loads(r.text)
            sio.write('已领取积分: {}\n\n'.format(resp['data']['wpsIntegral']))
            sio.write('已领取会员: {}天\n\n'.format(resp['data']['member']))
            sio.write('已完成任务: {}项\n\n'.format(resp['data']['taskNum']))
        else:
            desp = sio.getvalue()
            sendNotify.send(title = "Wps签到信息",msg = desp)
            print(desp)
            return desp
        b1 = docer_webpage_clockin(item['sid'])
        if b1 == 1:
            checinRecord_url = 'https://zt.wps.cn/2018/docer_check_in/api/checkin_record'
            r = s.get(checinRecord_url, headers={'sid': item['sid']})
            resp = json.loads(r.text)
            sio.write('本期连续签到: {}天\n\n'.format(resp['data']['max_days']))
            checkinEarlytimes_url = 'https://zt.wps.cn/2018/docer_check_in/api/checkin_early_times'
            r1 = s.get(checkinEarlytimes_url, headers={'sid': item['sid']})
            resp1 = json.loads(r1.text)
            sio.write('拥有补签卡: {}张\n\n'.format(resp1['data']))
            max_days = resp['data']['max_days']
            if resp1['data'] > 0 and len(resp['data']['records'])>0:
                max_days = docer_webpage_earlyclockin(item['sid'],resp1['data'],resp['data']['records'],max_days)
            if len(resp['data']['records'])>0:
                docer_webpage_giftReceive(item['sid'],max_days)

        b2 = wps_miniprogram_clockin(item['sid'])
        if b2 == 1:
            # 获取小程序当前会员奖励信息
            member_url = 'https://zt.wps.cn/2018/clock_in/api/get_data?member=wps'
            r = s.get(member_url, headers={'sid': item['sid']})
            # 累计在小程序打卡中获得会员天数
            total_add_day = re.search('"total_add_day":(\d+)', r.text).group(1)
            sio.write('小程序打卡中累计获得会员: {}天\n\n'.format(total_add_day))
        # 获取当前用户信息
        sio.write('\n\n          ---当前用户信息---↓\n\n')
        summary_url = 'https://vip.wps.cn/2019/user/summary'
        r = s.post(summary_url, headers={'sid': item['sid']})
        resp = json.loads(r.text)
        sio.write('会员积分:{}\n\n"稻米数量":{}\n\n'.format(resp['data']['integral'],resp['data']['wealth']))
        userinfo_url = 'https://vip.wps.cn/userinfo'
        r = s.get(userinfo_url, headers={'sid': item['sid']})
        resp = json.loads(r.text)
        if len(resp['data']['vip']['enabled']) > 0:
            sio.write('会员信息:\n\n')
            for i in range(len(resp['data']['vip']['enabled'])):
                sio.write('"类型":{}, "过期时间":{}\n\n'.format(resp['data']['vip']['enabled'][i]['name'],datetime.datetime.fromtimestamp(resp['data']['vip']['enabled'][i]['expire_time']).strftime("%Y--%m--%d %H:%M:%S")))
    # wps签到邀请
    sio.write("\n\n          ==========wps邀请==========\n\n")
    for item in sid:
        sio.write("---为{}邀请---↓\n\n".format(item['name']))
        if type(resp['data']['userid']) == int:
            wps_miniprogram_invite(invite_sid, resp['data']['userid'])
        else:
            sio.write("邀请失败: 用户ID错误, 请检查用户sid\n\n")

    desp = sio.getvalue()
    sendNotify.send(title = "帅气的林老师，Wps签到邀请信息，请查收",msg = desp)
    print(desp)
    return desp

# wps网页签到
def wps_webpage_clockin(sid: str):
    sio.write("          ---wps网页签到---↓\n\n")
    if len(sid) == 0:
        sio.write("签到失败: 用户sid为空, 请重新输入\n\n")
        return 0
    elif "*" in sid or sid[0] != "V":
        sio.write("签到失败: 用户sid错误, 请重新输入\n\n")
        return 0
    # 打卡签到
    clockin_url = 'https://vip.wps.cn/sigin/do'
    r = s.post(clockin_url, headers={'sid': sid})
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
    elif resp['msg'] == 'need_captcha' :
        getquestion_url = 'https://vip.wps.cn/checkcode/signin/question'
        r = s.get(getquestion_url, headers={'sid': sid})
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
            r = s.get(getquestion_url, headers={'sid': sid})
            resp = json.loads(r.text)
            # sio.write('选择题类型: {}'.format(resp['data']['multi_select']))
        answer_id = 3
        for i in range(4):
            opt = resp['data']['options'][i]
            if opt in answer_set:
                answer_id = i+1
                break
        sio.write("选项: {}\n\n".format(resp['data']['options']))
        sio.write("选择答案: {}\n\n".format(answer_id))
        # 提交答案
        answer_url = 'https://vip.wps.cn/sigin/do'
        r = s.post(answer_url, headers={'sid': sid}, data={'platform':2, 'answer':answer_id, 'auth_type':'answer'})
        resp = json.loads(r.text)
        # 答案错误
        if resp['msg'] == 'wrong answer':
            sio.write("答案不对, 挨个尝试\n\n")
            for i in range(4):
                r = s.post(answer_url, headers={'sid': sid}, data={'platform':2, 'answer':i+1, 'auth_type':'answer'})
                resp = json.loads(r.text)
                sio.write(i+1)
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
def wps_webpage_taskreward(sid: str):
    tasklist_url = 'https://vipapi.wps.cn/task_center/task/list'
    r = s.post(tasklist_url, headers={'sid': sid})
    if len(r.history) != 0:
        if r.history[0].status_code == 302:
            sio.write("任务检查失败: 用户sid错误, 请重新输入\n\n")
            return 0
    resp = json.loads(r.text)
    # 完善账户信息任务检查
    resplist = ([resp['data']['1']['task'], resp['data']['2']['task'],
                 resp['data']['3']['task']])
    statustask = 1
    for i in range(len(resplist)):
        checkinformation(resplist[i],sid)

# 检查wps网页任务提示信息
def checkinformation(information,sid):
    for i in range(len(information)):
        if information[i]['status'] == 0:
            fetchMission_url = 'https://vipapi.wps.cn/task_center/task/receive_task'
            r = s.post(fetchMission_url, data= {'id': information[i]['id']}, headers={'sid': sid})
            resp = json.loads(r.text)
            sio.write("任务{} “{}”领取情况: {}\n\n".format(information[i]['id'],information[i]['taskName'],resp['msg']))
        elif information[i]['status'] == 1:
            sio.write("任务{} “{}”未完成".format(information[i]['id'],information[i]['taskName']))
            if len(information[i]['prizes']) > 0:
                sio.write(",手动完成可获得")
                for j in range(len(information[i]['prizes'])):
                    sio.write("{}{}{} ".format(
                        information[i]['prizes'][j]['name'], information[i]['prizes'][j]['num'], information[i]['prizes'][j]['size']))
            sio.write("\n\n")
        elif information[i]['status'] == 2:
            sio.write("任务{} “{}”已完成".format(information[i]['id'],information[i]['taskName']))
            if len(information[i]['prizes']) > 0:
                sio.write(",可获得")
                for j in range(len(information[i]['prizes'])):
                    sio.write("{}{}{} ".format(
                        information[i]['prizes'][j]['name'], information[i]['prizes'][j]['num'], information[i]['prizes'][j]['size']))
            fetchReward_url = 'https://vipapi.wps.cn/task_center/task/receive_reward'
            s.post(fetchReward_url, data= {'id': information[i]['id']}, headers={'sid': sid})
            sio.write("已自动为您领取奖励\n\n")
        else:
            pass

# Docer网页签到
def docer_webpage_clockin(sid: str):
    sio.write("\n\n          ---稻壳网页签到---↓\n\n")
    docer_url = 'https://zt.wps.cn/2018/docer_check_in/api/checkin_today'
    r = s.post(docer_url, headers={'sid': sid})
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
def docer_webpage_earlyclockin(sid,checkinEarly_times,checkinrecord,max_days):
    now = datetime.datetime.now(tz)
    this_month_start = datetime.datetime(now.year, now.month, 1).date()
    checkin_Earliestdate = datetime.datetime.strptime(checkinrecord[0]['checkin_date'], '%Y-%m-%d').date()
    for i in range(checkinEarly_times):
        if checkin_Earliestdate.day > this_month_start.day:
            checkin_date = checkin_Earliestdate - datetime.timedelta(days=(i+1))
            checkin_date = datetime.datetime.strptime(str(checkin_date), '%Y-%m-%d').strftime('%Y%m%d')
            checkinEarly_url = 'https://zt.wps.cn/2018/docer_check_in/api/checkin_early'
            s.post(checkinEarly_url, data= {'date':checkin_date}, headers={'sid': sid})
        else:
            if i == 0:
                sio.write('无需补签\n\n')
                return max_days
            else:
                sio.write('使用补签卡{}张\n\n'.format(i))
                checinRecord_url = 'https://zt.wps.cn/2018/docer_check_in/api/checkin_record'
                r = s.get(checinRecord_url, headers={'sid': sid})
                resp = json.loads(r.text)
                sio.write('补签后连续签到: {}天\n\n'.format(resp['data']['max_days']))
                return resp['data']['max_days']
    sio.write('使用补签卡{}张\n\n'.format(i))
    checinRecord_url = 'https://zt.wps.cn/2018/docer_check_in/api/checkin_record'
    r = s.get(checinRecord_url, headers={'sid': sid})
    resp = json.loads(r.text)
    sio.write('补签后连续签到: {}天\n\n'.format(resp['data']['max_days']))
    return resp['data']['max_days']

# Docer网页领取礼物
def docer_webpage_giftReceive(sid,max_days):
    userinfo_url = 'https://vip.wps.cn/userinfo'
    r = s.get(userinfo_url, headers={'sid': sid})
    resp = json.loads(r.text)
    memberid = [0]
    if len(resp['data']['vip']['enabled']) > 0:
        for i in range(len(resp['data']['vip']['enabled'])):
            memberid.append(resp['data']['vip']['enabled'][i]['memberid'])
    rewardRecord_url = 'https://zt.wps.cn/2018/docer_check_in/api/reward_record'
    rewardReceive_url = 'https://zt.wps.cn/2018/docer_check_in/api/receive_reward'
    r = s.get(rewardRecord_url, headers={'sid': sid})
    resp = json.loads(r.text)
    rewardRecord_list = resp['data']
    if len(rewardRecord_list) > 0:
        for i in rewardRecord_list:
            if i['reward_type'] == 'vip' or i['reward_type'] == 'code':
                if int(i['limit_days']) <= max_days and int(i['limit_vip']) in memberid and i['status'] == 'unreceived':
                    r1 = s.post(rewardReceive_url, data={'reward_id': i['id'],'receive_from':'pc_client'},headers={'sid': sid})
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
    sio.write("\n\n          ---wps小程序签到---↓\n\n")
    if len(sid) == 0:
        sio.write("签到失败: 用户sid为空, 请重新输入\n\n")
        return 0
    elif "*" in sid or sid[0] != "V":
        sio.write("签到失败: 用户sid错误, 请重新输入\n\n")
        return 0
    # 打卡签到
    clockin_url = 'http://zt.wps.cn/2018/clock_in/api/clock_in'
    r = s.get(clockin_url, headers={'sid': sid})
    if len(r.history) != 0:
        if r.history[0].status_code == 302:
            sio.write("签到失败: 用户sid错误, 请重新输入\n\n")
            return 0
    resp = json.loads(r.text)
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
        r=s.get(signup_url, headers={'sid': sid})
        resp = json.loads(r.text)
        if resp['result'] == 'ok':
            sio.write('报名信息: 已自动报名, 报名后第二天签到\n\n')
            return 1
        else:
            sio.write('报名失败: 请手动报名, 报名后第二天签到\n\n')
            return 0
    # 打卡签到需要参加活动
    elif resp['msg'] == '答题未通过' :
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
                answer_id = i+1
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
                r = s.post(answer_url, headers={'sid': sid}, data={'answer': i+1})
                resp = json.loads(r.text)
                sio.write(i+1)
                if resp['result'] == 'ok':
                    sio.write(r.text)
                    break
        # 打卡签到
        clockin_url = 'http://zt.wps.cn/2018/clock_in/api/clock_in?member=wps'
        r = s.get(clockin_url, headers={'sid': sid})
        sio.write("签到信息: {}\n\n".format(r.text))
        return 1
    elif resp['msg'] == 'ParamData Empty' :
        sio.write('签到失败信息: {}\n\n'.format(r.text))
        signup_url = 'http://zt.wps.cn/2018/clock_in/api/sign_up'
        r=s.get(signup_url, headers={'sid': sid})
        sio.write('签到接口失效, 请手动打卡\n\n')
        return 1
    elif resp['msg'] == '不在打卡时间内':
        sio.write('签到失败: 不在打卡时间内\n\n')
        signup_url = 'http://zt.wps.cn/2018/clock_in/api/sign_up'
        r=s.get(signup_url, headers={'sid': sid})
        resp = json.loads(r.text)
        if resp['result'] == 'ok':
            sio.write('已自动报名, 报名后请设置在规定时间内签到\n\n')
            return 1
        else:
            sio.write('报名失败: 请手动报名, 报名后第二天签到\n\n')
            return 0
    # 其他错误
    elif resp['result'] == 'error':
        sio.write('签到失败信息: {}\n\n'.format(r.text))
        signup_url = 'http://zt.wps.cn/2018/clock_in/api/sign_up'
        r=s.get(signup_url, headers={'sid': sid})
        resp = json.loads(r.text)
        if resp['result'] == 'ok':
            sio.write('已自动报名, 报名后请设置在规定时间内签到\n\n')
            return 1
        else:
            sio.write('报名失败: 请手动报名, 报名后第二天签到\n\n')
            return 0

# wps小程序接受邀请
def wps_miniprogram_invite(sid: list, invite_userid: int) -> None:
    invite_url = 'http://zt.wps.cn/2018/clock_in/api/invite'
    k = 0
    for index, i in enumerate(sid):
        time.sleep(5)
        if k < invite_limit:
            headers = {
                'sid': i
            }
            r = s.post(invite_url, headers=headers, data={
                'invite_userid': invite_userid})
            if r.status_code == 200:
                try:
                    resp = json.loads(r.text)
                    sio.write("邀请对象ID={}, Result: {}\n\n".format(str(index+1).zfill(2),resp['result']))
                    k += 1
                except:
                    resp = r.text[:25]
                    sio.write("邀请对象ID={}, Result: ID已失效\n\n".format(str(index+1).zfill(2)))
            else:
                sio.write("邀请对象ID={}, 状态码: {},\n\n  请求信息{}\n\n".format(str(index+1).zfill(2), r.status_code, r.text[:25]))
    return k


def main_handler(event, context):
    return main()

if __name__ == '__main__':
    main()
