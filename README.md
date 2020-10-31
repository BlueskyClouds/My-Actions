# My-Actions

<p align="center">
    <img alt="Version" src="https://img.shields.io/badge/release-0.0.1-blue"/>
    <a href="https://github.com/BlueSkyClouds">
        <img alt="Author" src="https://img.shields.io/badge/author-BlueSkyClouds-blueviolet"/>
    </a>
</p>


# 项目更新
[保持和原作者同步的代码更新](https://blog.blueskyclouds.com/jsfx/58.html)  尽量跟原作者同步。
# 使用方式
1. 右上角fork本仓库
2. 点击Settings -> Secrets -> 点击绿色按钮 (如无绿色按钮说明已激活。直接到第四步。)
3. 新增 new secret 并设置 Secrets:
4. 点击Actions并选择你要签到的项目后点击Run workflow

**本项目需要设置的 Secrets:**

| 名称     | 内容           |   说明|
| -------- | ------------- |   ----- |
| `IQIYI_COOKIE` |爱奇艺authcookie|爱奇艺cookie中 P00001的值 详情[文字教程](https://www.bilibili.com/read/cv7437179) [视频教程](https://www.bilibili.com/video/BV1B541157DE) 电脑版有效期三个月
| `BILI_USER` |哔哩哔哩账号|B站账号(由于是账号密码登录,Cookie不会过期,不提供消息失效提醒,并只有Server酱提醒，因为懒.)|
| `BILI_PASS` |哔哩哔哩密码|B站密码|
| `V_REF_URL` |腾讯视频Request URL|https://access.video.qq.com/user/auth_refresh|
| `V_COOKIE` |access.video.qq.com下Cookie||
| `TELECOM_MOBILE` |中国电信手机号|只需要手机号 无需Cookie|
| `WA_COOKIE` | 吾爱破解论坛Cookie||
| `PUSH_KEY` | Server酱SCKEY值 | cookie失效推送[server酱的微信通知](http://sc.ftqq.com/3.version) |
| `BARK_PUSH` | Bark推送值 | 此内容支持自建Bark添加整个链接即可(自建链接切记删除最后一个/  比如你的是https://a.a.com/ 只需要填写https://a.a.com即可)|
| `BARK_SOUND` | BARK app推送铃声|BARK app推送铃声,铃声列表去APP查看复制填写|
| `TG_BOT_TOKEN`          |   telegram推送    | tg推送,填写自己申请[@BotFather](https://t.me/BotFather)的Token,如`10xxx4:AAFcqxxxxgER5uw` , [具体教程](https://github.com/lxk0301/scripts/pull/37#issuecomment-692415594) |
| `TG_USER_ID`            |   telegram推送    | tg推送,填写[@getuseridbot](https://t.me/getuseridbot)中获取到的纯数字ID, [具体教程](https://github.com/lxk0301/scripts/pull/37#issuecomment-692415594) |
| `SEND_KEY` | 推送开关|如果你想只在COOKIE失效时提醒,就加一个这个,参数值随便写就行|

可使用Star触发，点击自己仓库右上角Star即可激活，如是Unstar状态需要点击两次即可。

#### 取消自动运行部分项目：
<p align="center">
    <img src="https://cdn.jsdelivr.net/gh/BlueskyClouds/BlueskyClouds.github.io/2020/10/19/img/2020-10-19.jpg">
</p>
#### 获取腾讯视频Cookie:
<p align="center">
    <img src="https://cdn.jsdelivr.net/gh/BlueskyClouds/BlueskyClouds.github.io/2020/10/19/img/V_video-1.jpg">
    <img src="https://cdn.jsdelivr.net/gh/BlueskyClouds/BlueskyClouds.github.io/2020/10/19/img/V_video-2.jpg">
</p>

