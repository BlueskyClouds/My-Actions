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

**本项目需要设置的 Secrets:**

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
| `PUSH_KEY`              |   Server酱SCKEY值      | cookie失效推送[server酱的微信通知](http://sc.ftqq.com/3.version) |
| `BARK_PUSH`             |   Bark推送值           | 此内容支持自建Bark添加整个链接即可(自建链接切记删除最后一个/  比如你的是https://a.a.com/ 只需要填写https://a.a.com 即可)|
| `BARK_SOUND`            |   BARK app推送铃声     |BARK app推送铃声,铃声列表去APP查看复制填写|
| `TG_BOT_TOKEN`          |   telegram推送        | tg推送,填写自己申请[@BotFather](https://t.me/BotFather)的Token,如`10xxx4:AAFcqxxxxgER5uw` , [具体教程](https://github.com/lxk0301/scripts/pull/37#issuecomment-692415594) |
| `TG_USER_ID`            |   telegram推送        | tg推送,填写[@getuseridbot](https://t.me/getuseridbot)中获取到的纯数字ID, [具体教程](https://github.com/lxk0301/scripts/pull/37#issuecomment-692415594) |
| `DD_BOT_TOKEN`          |   钉钉推送                | 钉钉推送[官方文档](https://ding-doc.dingtalk.com/doc#/serverapi2/qf2nxq) ,只需`https://oapi.dingtalk.com/robot/send?access_token=XXX` 等于符号后面的 XXX， 注：如果钉钉推送只填写`DD_BOT_TOKEN`，那么安全设置需勾选`自定义关键词`，内容输入输入`账号`即可，其他安全设置不要勾选 |
| `DD_BOT_SECRET`         |   钉钉推送              | 密钥，机器人安全设置页面，加签一栏下面显示的 SEC 开头的字符串,填写了`DD_BOT_TOKEN`和`DD_BOT_SECRET`，钉钉机器人安全设置只需勾选`加签`即可，其他选项不要勾选 |
| `SEND_KEY`              |   推送开关            |如果你想只在COOKIE失效时发送推送信息,就加一个这个,参数值随便写就行|


### 同步Fork后的代码

#### 手动同步

[手动同步 https://blog.blueskyclouds.com/jsfx/58.html](https://blog.blueskyclouds.com/jsfx/58.html)

#### 自动同步

##### 方案A - 强制远程分支覆盖自己的分支
1. 参考[这里](https://github.com/lxk0301/scripts/blob/master/backUp/gitSync.md)，安装[pull插件](https://github.com/apps/pull)，并确认此项目已在pull插件的作用下（参考文中1-d）。
2. 确保.github/pull.yml文件正常存在，yml内上游作者填写正确(此项目已填好，无需更改)。
3. 确保pull.yml里面是`mergeMethod: hardreset`(默认就是hardreset)。
4. ENJOY!上游更改三小时左右就会自动发起同步。

##### 方案B - 保留自己分支的修改

> 上游变动后pull插件会自动发起pr，但如果有冲突需要自行**手动**确认。
> 如果上游更新涉及workflow里的文件内容改动，需要自行**手动**确认。

1. 参考[这里](https://github.com/lxk0301/scripts/blob/master/backUp/gitSync.md)，安装[pull插件](https://github.com/apps/pull)，并确认此项目已在pull插件的作用下（参考文中1-d）。
2. 确保.github/pull.yml文件正常存在，yml内上游作者填写正确(此项目已填好，无需更改)。
3. 将pull.yml里面的`mergeMethod: hardreset`修改为`mergeMethod: merge`保存。
4. ENJOY!上游更改三小时左右就会自动发起同步。

### 访问量

![](http://profile-counter.glitch.me/BlueSkyClouds/count.svg)

