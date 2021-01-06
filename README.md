 ![BlueskyClouds’s github stats](https://github-readme-stats.vercel.app/api?username=BlueskyClouds&show_icons=true&theme=merko)
<div align="center">
<h1 align="center">My-Actions</h1>
<img src="https://img.shields.io/github/issues/BlueskyClouds/My-Actions?color=green">
<img src="https://img.shields.io/github/stars/BlueskyClouds/My-Actions?color=yellow">
<img src="https://img.shields.io/github/forks/BlueskyClouds/My-Actions?color=orange">
<img src="https://img.shields.io/github/license/BlueskyClouds/My-Actions?color=ff69b4">
<img src="https://img.shields.io/github/languages/code-size/BlueskyClouds/My-Actions?color=blueviolet">
</div>

个人收集并适配Github Actions的各类签到大杂烩

### 本项目已可以实现自动同步上游更改！[具体点击](#自动同步)

# 使用方式
1. 右上角fork本仓库
2. 点击Settings -> Secrets -> 点击绿色按钮 (如无绿色按钮说明已激活。直接到第三步。)
3. 新增 new secret 并设置 Secrets:
4. 双击右上角自己仓库Star触发，如有不使用项目请[禁用部分项目](https://cdn.jsdelivr.net/gh/BlueskyClouds/BlueskyClouds.github.io/2020/10/19/img/2020-10-19.jpg)
5. **必须** - 请随便找个文件(例如`README.md`)，加个空格提交一下，否则可能会出现无法定时执行的问题
6. 由于规则更新,可能会Fork后会默认禁用,请手动点击Actions 选择要签到的项目 `enable workflows`激活
7. [定时执行](#定时执行)

# 定时执行
1. 支持手动执行，具体在Actions中选中要执行的Workflows后再在右侧可以看到Run workflow，点击即可运行此workflow。

2. 如果嫌上一步麻烦的，也可以直接点击一下star，你会发现所有的workflow都已执行。

3. 如需修改执行时间自行修改`.github\workflows\`下面的yaml内的` cron:` 执行时间为国际标准时间 [时间转换](http://www.timebie.com/cn/universalbeijing.php) 分钟在前 小时在后 尽量提前几分钟,因为下载安装部署环境需要一定时间

##### Cookie变量设置 Secrets:**

| 名称     | 内容           |   说明  |
| -------- | -------------|   ----- |
| `IQIYI_COOKIE`          |   爱奇艺authcookie    |P00001的值 详情[文字教程](https://www.bilibili.com/read/cv7437179) [视频教程](https://www.bilibili.com/video/BV1B541157DE) 电脑版有效期三个月|
| `BILI_USER`             |   哔哩哔哩账号   |B站账号|
| `BILI_PASS`             |   哔哩哔哩密码   |B站密码|
| `BIKA_USER`             |   哔咔漫画用户名   |记住是登录用户名而不是邮箱|
| `BIKA_PASS`             |   哔咔漫画密码   |哔咔漫画密码|
| `V_REF_URL`             |   腾讯视频Request URL |电脑端搜索auth_refresh复制整段Request url[图片教程](https://cdn.jsdelivr.net/gh/BlueskyClouds/BlueskyClouds.github.io/2020/11/1/img/v_1.jpg)|
| `V_COOKIE`              |   腾讯视频Cookie   |电脑端搜索auth_refresh复制Cookie[图片教程](https://cdn.jsdelivr.net/gh/BlueskyClouds/BlueskyClouds.github.io/2020/11/1/img/v_2.jpg)|
| `TELECOM_MOBILE`        |   中国电信手机号         |只需要手机号 单账号 `多账号将会暴露手机号` 自行考虑,多账号使用`,`分割 部分地区或手机号暂无法签到，自行测试使用|
| `V2EXCK`                |   V2EX的Cookie         |V2EX的Cookie|
| `BDUSS`                 |   百度BDUSS         |BDUSS值切勿使用双击复制 (结尾有一个`符号`双击复制可能无法复制完整)|
##### 推送通知环境变量(目前提供`微信server酱`、`pushplus(推送加)`、`iOS Bark APP`、`telegram机器人`、`钉钉机器人`、`企业微信机器人`、`iGot`、`QQ酷推`等通知方式)

| Name                    |   归属   | 属性   | 说明                                                         |
| :---------------------: | :----------: | --------- | ------------------------------------------------------------ |
| `SEND_KEY`              |   推送开关        | 非必须 | 仅在Cookie失效时发送推送,值随意|
| `PUSH_KEY`              |   微信server酱推送   | 非必须 | server酱的微信通知[官方文档](http://sc.ftqq.com/3.version) |
| `BARK_PUSH`             |   [BARK推送](https://apps.apple.com/us/app/bark-customed-notifications/id1403753865)   | 非必须 | IOS用户下载BARK这个APP,填写内容是app提供的`设备码`，例如：https://api.day.app/123 ，那么此处的设备码就是`123`，再不懂看 [这个图](https://github.com/lxk0301/jd_scripts/tree/master/icon/bark.jpg)（注：支持自建填完整链接即可） |
| `BARK_SOUND`            |   [BARK推送](https://apps.apple.com/us/app/bark-customed-notifications/id1403753865)   | 非必须 | bark推送声音设置，例如`choo`,具体值请在`bark`-`推送铃声`-`查看所有铃声` |
| `TG_BOT_TOKEN`          |   telegram推送   | 非必须 | tg推送(需设备可连接外网),`TG_BOT_TOKEN`和`TG_USER_ID`两者必需,填写自己申请[@BotFather](https://t.me/BotFather)的Token,如`10xxx4:AAFcqxxxxgER5uw` , [具体教程](https://github.com/lxk0301/jd_scripts/tree/master/backUp/TG_PUSH.md) |
| `TG_USER_ID`            |   telegram推送   | 非必须 | tg推送(需设备可连接外网),`TG_BOT_TOKEN`和`TG_USER_ID`两者必需,填写[@getuseridbot](https://t.me/getuseridbot)中获取到的纯数字ID, [具体教程](https://github.com/lxk0301/jd_scripts/tree/master/backUp/TG_PUSH.md) |
| `DD_BOT_TOKEN`          |   钉钉推送   | 非必须 | 钉钉推送(`DD_BOT_TOKEN`和`DD_BOT_SECRET`两者必需)[官方文档](https://ding-doc.dingtalk.com/doc#/serverapi2/qf2nxq) ,只需`https://oapi.dingtalk.com/robot/send?access_token=XXX` 等于`=`符号后面的XXX即可 |
| `DD_BOT_SECRET`         |   钉钉推送   | 非必须 | (`DD_BOT_TOKEN`和`DD_BOT_SECRET`两者必需) ,密钥，机器人安全设置页面，加签一栏下面显示的SEC开头的`SECXXXXXXXXXX`等字符 , 注:钉钉机器人安全设置只需勾选`加签`即可，其他选项不要勾选,再不懂看 [这个图](https://github.com/lxk0301/jd_scripts/tree/master/icon/DD_bot.png) |
| `QYWX_KEY`              |   企业微信推送   | 非必须 | 密钥，企业微信推送 webhook 后面的 key [详见官方说明文档](https://work.weixin.qq.com/api/doc/90000/90136/91770) |
| `IGOT_PUSH_KEY`         |   iGot推送   | 非必须 | iGot聚合推送，支持多方式推送，确保消息可达。 [参考文档](https://wahao.github.io/Bark-MP-helper ) |
| `QQ_SKEY`               |   酷推(Cool Push)推送   | 非必须 | 推送所需的Skey,登录后获取Skey [参考文档](https://cp.xuthus.cc/) |
| `QQ_MODE`               |   酷推(Cool Push)推送   | 非必须 | 推送方式(send或group或者wx，默认send) [参考文档](https://cp.xuthus.cc/) |
| `PUSH_PLUS_TOKEN`       |   pushplus推送  | 非必须 | 微信扫码登录后一对一推送或一对多推送下面的token(您的Token) [官方网站](http://pushplus.hxtrip.com/)                     |
| `PUSH_PLUS_USER`        |   pushplus推送  | 非必须 | 一对多推送的“群组编码”（一对多推送下面->您的群组(如无则新建)->群组编码）注:(1、需订阅者扫描二维码 2、如果您是创建群组所属人，也需点击“查看二维码”扫描绑定，否则不能接受群组消息推送)，只填`PUSH_PLUS_TOKEN`默认为一对一推送                    |
| `TG_PROXY_HOST`         |  Telegram 代理的 IP  | 非必须 | 代理类型为 http。例子：http代理 http://127.0.0.1:1080 则填写 127.0.0.1 |
| `TG_PROXY_PORT`         |  Telegram 代理的端口  | 非必须 | 例子：http代理 http://127.0.0.1:1080 则填写 1080 |

### 同步Fork后的代码

#### 手动同步

[手动同步 https://blog.blueskyclouds.com/jsfx/58.html](https://blog.blueskyclouds.com/jsfx/58.html)

#### 自动同步

##### 方案A - 强制远程分支覆盖自己的分支
1. 参考[这里](https://github.com/lxk0301/jd_scripts/blob/master/backUp/gitSync.md)，安装[pull插件](https://github.com/apps/pull)，并确认此项目已在pull插件的作用下（参考文中1-d）。
2. 确保.github/pull.yml文件正常存在，yml内上游作者填写正确(此项目已填好，无需更改)。
3. 确保pull.yml里面是`mergeMethod: hardreset`(默认就是hardreset)。
4. ENJOY!上游更改三小时左右就会自动发起同步。

##### 方案B - 保留自己分支的修改

> 上游变动后pull插件会自动发起pr，但如果有冲突需要自行**手动**确认。
> 如果上游更新涉及workflow里的文件内容改动，需要自行**手动**确认。

1. 参考[这里](https://github.com/lxk0301/jd_scripts/blob/master/backUp/gitSync.md)，安装[pull插件](https://github.com/apps/pull)，并确认此项目已在pull插件的作用下（参考文中1-d）。
2. 确保.github/pull.yml文件正常存在，yml内上游作者填写正确(此项目已填好，无需更改)。
3. 将pull.yml里面的`mergeMethod: hardreset`修改为`mergeMethod: merge`保存。
4. ENJOY!上游更改三小时左右就会自动发起同步。

### 鸣谢

特别感谢 [JetBrains](https://www.jetbrains.com/?from=My-Actions) 为开源项目提供免费的 [WebStrom](https://www.jetbrains.com/?from=My-Actions) 等 IDE 的授权  
[<img src="https://cdn.jsdelivr.net/gh/BlueskyClouds/BlueskyClouds.github.io/2020/12/1/img/idea/jetbrains.png" width="200"/>](https://www.jetbrains.com/?from=My-Actions)
### 访问量

![](http://profile-counter.glitch.me/BlueSkyClouds/count.svg)

