/****
 *
 * @description 腾讯视频好莱坞会员V力值签到，手机签到和领取任务及奖励。
 * @author BlueSkyClouds
 * @create_at 2020-11-02
 */

const $ = new Env('腾讯视频会员签到');
const notify = $.isNode() ? require('./sendNotify') : '';
let ref_url = ''
const _cookie = process.env.V_COOKIE
const SEND_KEY = process.env.SEND_KEY
const auth = getAuth()
const axios = require('axios')
var date = new Date()
const headers = {
    'Referer': 'https://v.qq.com',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.204 Safari/537.36',
    'Cookie': _cookie
}

/**
 * @description 拼接REF_URL
 */
if (process.env.V_REF_URL) {
    if(process.env.V_REF_URL.indexOf('https://access.video.qq.com/user/auth_refresh') > -1 ) {
        ref_url = process.env.V_REF_URL
    } else {
        console.log("V_REF_URL值填写错误")
    }
    if(process.env.V_COOKIE.indexOf('main_login=') = -1 ) {
        console.log("Cookie填写错误")
    }
    //验证V_REF_URL和cookie是否填写正确
    ref_url_ver()
} else {
    //无意义输出方便调试
    console.log("V_REF_URL值填写错误")
}

/**
 * @description 封装一个解析setCookie的方法
 * @param {*} val
 * @returns obj
 */
function parseSet(c_list) {
    let obj = {}
    c_list.map(t=>{
        const obj = {}
        t.split(', ')[0].split(';').forEach(item=>{
            const [key, val] = item.split('=')
            obj[key] = val
        })
        return obj
    }).forEach(t=>obj = { ...obj, ...t })
    return obj
}

/**
 * @description 获取有效的cookie参数
 * @param {*} [c=_cookie]
 * @returns obj
 */
function getAuth(c = _cookie) {
    let needParams = [""]
    //适配微信登录
    if(_cookie){
        if (_cookie.includes("main_login=wx")) {
            needParams = ["tvfe_boss_uuid","video_guid","video_platform","pgv_pvid","pgv_info","pgv_pvi","pgv_si","_qpsvr_localtk","RK","ptcz","ptui_loginuin","main_login","access_token","appid","openid","vuserid","vusession"]
        } else if (_cookie.includes("main_login=qq")){
            needParams = ["tvfe_boss_uuid","video_guid","video_platform","pgv_pvid","pgv_info","pgv_pvi","pgv_si","_qpsvr_localtk","RK","ptcz","ptui_loginuin","main_login","vqq_access_token","vqq_appid","vqq_openid","vqq_vuserid","vqq_vusession"]
        } else {
            console.log("getAuth - 无法提取有效cookie参数")
        }
    }
    const obj = {}
    if(c){
        c.split('; ').forEach(t=>{
            const [key, val] = t.split(/\=(.*)$/,2)
            needParams.indexOf(key) !=-1 && ( obj[key] = val)
        })
    }
    return obj
}

/**
 * @description 刷新每天更新cookie参数
 * @returns
 */
function refCookie(url = ref_url) {
    return new Promise((resovle, reject)=>{
        axios({ url, headers }).then(e =>{
            const { vusession } = parseSet(e.headers['set-cookie'])
            const { vqq_vusession } = parseSet(e.headers['set-cookie'])
            //微信和QQ参数不同
            if (vusession) {
                auth['vusession'] = vusession
            } else {
                auth['vqq_vusession'] = vqq_vusession
            }
            // 刷新cookie后去签到
            resovle({
                ...headers, Cookie: Object.keys(auth).map(i => i + '=' + auth[i]).join('; '),
                'Referer': 'https://m.v.qq.com'
            })
        }).catch(reject)
    })
}

/**
 * @description 验证ref_url是否正确
 */
function ref_url_ver(url = ref_url,_cookie) {
    $.get({
        url, headers
    }, function(error, response, data) {
        //console.log(data)
        if (error) {
            $.log(error);
            console.log("腾讯视频会员签到", "验证ref_url请求失败 ‼️‼️", error)
        } else {
            if (data.match(/nick/)) { //通过验证获取QQ昵称参数来判断是否正确
                console.log("验证成功，执行主程序")
                exports.main()
            } else {
                console.log("验证ref_url失败,无法获取个人资料 ref_url或Cookie失效 ‼️‼️")
                notify.sendNotify("腾讯视频会员签到", '验证ref_url失败,无法获取个人资料 Cookie失效 ‼️‼️');
            }
        }
    })
}

// 手机端签到
function txVideoSignIn(headers) {
    $.get({
        url: `https://vip.video.qq.com/fcgi-bin/comm_cgi?name=hierarchical_task_system&cmd=2&_=${ parseInt(Math.random()*1000) }`,headers
    }, function(error, response, data) {
        if (error) {
            $.log(error);
            console.log("腾讯视频会员签到", "签到请求失败 ‼️‼️", error)
        } else {
            if (data.match(/Account Verify Error/)) {
                if(SEND_KEY){
                    notify.sendNotify("腾讯视频会员签到", "签到失败, Cookie失效 ‼️‼️");
                    console.log("腾讯视频会员签到", "", "签到失败, Cookie失效 ‼️‼️")
                }else{
                    console.log("腾讯视频会员签到", "", "签到失败, Cookie失效 ‼️‼️")
                }
            } else if (data.match(/checkin_score/)) {
                msg = data.match(/checkin_score": (.+?),"msg/)[1]
                //通过分数判断是否重复签到
                if(msg == '0'){
                    msg = '签到失败，重复签到 ‼️‼️'
                }else{
                    msg = "签到成功，签到分数：" + msg  + "分 🎉"
                }
                //签到成功才执行任务签到
                console.log("腾讯视频会员签到", "", "以下任务仅领取,需要手动完成,如没有完成请无视" )
                Collect_task()
                //判断是否为Cookie失效时才提醒
                if(SEND_KEY){
                    console.log("腾讯视频会员签到", "", date.getMonth() + 1 + "月" + date.getDate() + "日, " + msg )
                }else{
                    notify.sendNotify("腾讯视频会员签到", msg);
                    console.log("腾讯视频会员签到", "", date.getMonth() + 1 + "月" + date.getDate() + "日, " + msg )
                }
            } else if (data.match(/Not VIP/)) {
                console.log("腾讯视频会员签到", "", "非会员无法签到" )
            } else {
                console.log("腾讯视频会员签到", "", "脚本待更新 ‼️‼️")
                //输出日志查找原因
                console.log(data)
            }
        }
    })
}

//下载任务签到请求
function txVideoDownTask1(headers) {
    $.get({
        url: `https://vip.video.qq.com/fcgi-bin/comm_cgi?name=spp_MissionFaHuo&cmd=4&task_id=7`, headers
    }, function(error, response, data) {
        if (error) {
            $.log(error);
            console.log("腾讯视频会员签到", "下载任务签到请求 ‼️‼️", error)
        } else {
            if (data.match(/已发过货/)) {
                console.log("腾讯视频会员下载任务签到", "", "签到失败, 请勿重复领取任务 ‼️‼️")
            } else if (data.match(/score/)) {
                msg = data.match(/score":(.*?)}/)[1]
                console.log("腾讯视频会员下载任务签到", "", "签到成功，签到分数：" + msg + "分 🎉")
            } else {
                //console.log("腾讯视频会员下载任务签到", "", "签到失败, 任务未完成 ‼️‼️")
                console.log("腾讯视频会员下载任务签到", "", data)
            }
        }
    })
}

//赠送任务签到请求
function txVideoDownTask2(headers) {
    $.get({
        url: `https://vip.video.qq.com/fcgi-bin/comm_cgi?name=spp_MissionFaHuo&cmd=4&task_id=6`, headers
    }, function(error, response, data) {
        if (error) {
            $.log(error);
            console.log("腾讯视频会员签到", "赠送任务签到请求 ‼️‼️", error)
        } else {
            if (data.match(/已发过货/)) {
                console.log("腾讯视频会员赠送任务签到", "", "签到失败, 请勿重复领取任务 ‼️‼️")
            } else if (data.match(/score/)) {
                msg = data.match(/score":(.*?)}/)[1]
                console.log("腾讯视频会员赠送任务签到", "", "签到成功，签到分数：" + msg + "分 🎉")
            } else {
                //console.log("腾讯视频会员赠送任务签到", "", "签到失败, 任务未完成 ‼️‼️")
                console.log("腾讯视频会员赠送任务签到", "", data)
            }
        }
    })
}

//弹幕任务签到请求
function txVideoDownTask3(headers) {
    $.get({
        url: `https://vip.video.qq.com/fcgi-bin/comm_cgi?name=spp_MissionFaHuo&cmd=4&task_id=3`, headers
    }, function(error, response, data) {
        if (error) {
            $.log(error);
            console.log("腾讯视频会员签到", "弹幕任务签到请求 ‼️‼️", error)
        } else {
            if (data.match(/已发过货/)) {
                console.log("腾讯视频会员弹幕任务签到", "", "签到失败, 请勿重复领取任务 ‼️‼️")
            } else if (data.match(/score/)) {
                msg = data.match(/score":(.*?)}/)[1]
                console.log("腾讯视频会员弹幕任务签到", "", "签到成功，签到分数：" + msg + "分 🎉")
            } else {
                //console.log("腾讯视频会员弹幕任务签到", "", "签到失败, 任务未完成 ‼️‼️")
                console.log("腾讯视频会员弹幕任务签到", "", data)
            }
        }
    })
}

//观看60分钟任务签到请求
function txVideoDownTask4(headers) {
    $.get({
        url: `https://vip.video.qq.com/fcgi-bin/comm_cgi?name=spp_MissionFaHuo&cmd=4&task_id=1`, headers
    }, function(error, response, data) {
        if (error) {
            $.log(error);
            console.log("腾讯视频会员签到", "观看任务签到请求 ‼️‼️", error)
        } else {
            if (data.match(/已发过货/)) {
                console.log("腾讯视频会员观看任务签到", "", "签到失败, 请勿重复领取任务 ‼️‼️")
            } else if (data.match(/score/)) {
                msg = data.match(/score":(.*?)}/)[1]
                console.log("腾讯视频会员观看任务签到", "", "签到成功，签到分数：" + msg + "分 🎉")
            } else {
                //console.log("腾讯视频会员观看任务签到", "", "签到失败, 任务未完成 ‼️‼️")
                console.log("腾讯视频会员观看任务签到", "", data)
            }
        }
    })
}

//任务领取
function Collect_task() {
    refCookie().then(data => {
        this.provinces = data
        txVideoDownTask1(data)
        txVideoDownTask2(data)
        txVideoDownTask3(data)
        txVideoDownTask4(data)
    })
}

//主程序入口
exports.main = () => new Promise(
    (resovle, reject) => refCookie()
        .then(params=>Promise.all([ txVideoSignIn(params)])
            .then(e=>resovle())
            .catch(e=>reject())
        ).catch(e=>{
            //如果有错误自行取消下面这行注释
            //console.log(e)
            console.log('腾讯视频签到通知-Cookie已失效')
        })
)

// prettier-ignore
function Env(t,e){class s{constructor(t){this.env=t}send(t,e="GET"){t="string"==typeof t?{url:t}:t;let s=this.get;return"POST"===e&&(s=this.post),new Promise((e,i)=>{s.call(this,t,(t,s,r)=>{t?i(t):e(s)})})}get(t){return this.send.call(this.env,t)}post(t){return this.send.call(this.env,t,"POST")}}return new class{constructor(t,e){this.name=t,this.http=new s(this),this.data=null,this.dataFile="box.dat",this.logs=[],this.isMute=!1,this.isNeedRewrite=!1,this.logSeparator="\n",this.startTime=(new Date).getTime(),Object.assign(this,e),this.log("",`\ud83d\udd14${this.name}, \u5f00\u59cb!`)}isNode(){return"undefined"!=typeof module&&!!module.exports}isQuanX(){return"undefined"!=typeof $task}isSurge(){return"undefined"!=typeof $httpClient&&"undefined"==typeof $loon}isLoon(){return"undefined"!=typeof $loon}toObj(t,e=null){try{return JSON.parse(t)}catch{return e}}toStr(t,e=null){try{return JSON.stringify(t)}catch{return e}}getjson(t,e){let s=e;const i=this.getdata(t);if(i)try{s=JSON.parse(this.getdata(t))}catch{}return s}setjson(t,e){try{return this.setdata(JSON.stringify(t),e)}catch{return!1}}getScript(t){return new Promise(e=>{this.get({url:t},(t,s,i)=>e(i))})}runScript(t,e){return new Promise(s=>{let i=this.getdata("@chavy_boxjs_userCfgs.httpapi");i=i?i.replace(/\n/g,"").trim():i;let r=this.getdata("@chavy_boxjs_userCfgs.httpapi_timeout");r=r?1*r:20,r=e&&e.timeout?e.timeout:r;const[o,h]=i.split("@"),a={url:`http://${h}/v1/scripting/evaluate`,body:{script_text:t,mock_type:"cron",timeout:r},headers:{"X-Key":o,Accept:"*/*"}};this.post(a,(t,e,i)=>s(i))}).catch(t=>this.logErr(t))}loaddata(){if(!this.isNode())return{};{this.fs=this.fs?this.fs:require("fs"),this.path=this.path?this.path:require("path");const t=this.path.resolve(this.dataFile),e=this.path.resolve(process.cwd(),this.dataFile),s=this.fs.existsSync(t),i=!s&&this.fs.existsSync(e);if(!s&&!i)return{};{const i=s?t:e;try{return JSON.parse(this.fs.readFileSync(i))}catch(t){return{}}}}}writedata(){if(this.isNode()){this.fs=this.fs?this.fs:require("fs"),this.path=this.path?this.path:require("path");const t=this.path.resolve(this.dataFile),e=this.path.resolve(process.cwd(),this.dataFile),s=this.fs.existsSync(t),i=!s&&this.fs.existsSync(e),r=JSON.stringify(this.data);s?this.fs.writeFileSync(t,r):i?this.fs.writeFileSync(e,r):this.fs.writeFileSync(t,r)}}lodash_get(t,e,s){const i=e.replace(/\[(\d+)\]/g,".$1").split(".");let r=t;for(const t of i)if(r=Object(r)[t],void 0===r)return s;return r}lodash_set(t,e,s){return Object(t)!==t?t:(Array.isArray(e)||(e=e.toString().match(/[^.[\]]+/g)||[]),e.slice(0,-1).reduce((t,s,i)=>Object(t[s])===t[s]?t[s]:t[s]=Math.abs(e[i+1])>>0==+e[i+1]?[]:{},t)[e[e.length-1]]=s,t)}getdata(t){let e=this.getval(t);if(/^@/.test(t)){const[,s,i]=/^@(.*?)\.(.*?)$/.exec(t),r=s?this.getval(s):"";if(r)try{const t=JSON.parse(r);e=t?this.lodash_get(t,i,""):e}catch(t){e=""}}return e}setdata(t,e){let s=!1;if(/^@/.test(e)){const[,i,r]=/^@(.*?)\.(.*?)$/.exec(e),o=this.getval(i),h=i?"null"===o?null:o||"{}":"{}";try{const e=JSON.parse(h);this.lodash_set(e,r,t),s=this.setval(JSON.stringify(e),i)}catch(e){const o={};this.lodash_set(o,r,t),s=this.setval(JSON.stringify(o),i)}}else s=this.setval(t,e);return s}getval(t){return this.isSurge()||this.isLoon()?$persistentStore.read(t):this.isQuanX()?$prefs.valueForKey(t):this.isNode()?(this.data=this.loaddata(),this.data[t]):this.data&&this.data[t]||null}setval(t,e){return this.isSurge()||this.isLoon()?$persistentStore.write(t,e):this.isQuanX()?$prefs.setValueForKey(t,e):this.isNode()?(this.data=this.loaddata(),this.data[e]=t,this.writedata(),!0):this.data&&this.data[e]||null}initGotEnv(t){this.got=this.got?this.got:require("got"),this.cktough=this.cktough?this.cktough:require("tough-cookie"),this.ckjar=this.ckjar?this.ckjar:new this.cktough.CookieJar,t&&(t.headers=t.headers?t.headers:{},void 0===t.headers.Cookie&&void 0===t.cookieJar&&(t.cookieJar=this.ckjar))}get(t,e=(()=>{})){t.headers&&(delete t.headers["Content-Type"],delete t.headers["Content-Length"]),this.isSurge()||this.isLoon()?(this.isSurge()&&this.isNeedRewrite&&(t.headers=t.headers||{},Object.assign(t.headers,{"X-Surge-Skip-Scripting":!1})),$httpClient.get(t,(t,s,i)=>{!t&&s&&(s.body=i,s.statusCode=s.status),e(t,s,i)})):this.isQuanX()?(this.isNeedRewrite&&(t.opts=t.opts||{},Object.assign(t.opts,{hints:!1})),$task.fetch(t).then(t=>{const{statusCode:s,statusCode:i,headers:r,body:o}=t;e(null,{status:s,statusCode:i,headers:r,body:o},o)},t=>e(t))):this.isNode()&&(this.initGotEnv(t),this.got(t).on("redirect",(t,e)=>{try{if(t.headers["set-cookie"]){const s=t.headers["set-cookie"].map(this.cktough.Cookie.parse).toString();s&&this.ckjar.setCookieSync(s,null),e.cookieJar=this.ckjar}}catch(t){this.logErr(t)}}).then(t=>{const{statusCode:s,statusCode:i,headers:r,body:o}=t;e(null,{status:s,statusCode:i,headers:r,body:o},o)},t=>{const{message:s,response:i}=t;e(s,i,i&&i.body)}))}post(t,e=(()=>{})){if(t.body&&t.headers&&!t.headers["Content-Type"]&&(t.headers["Content-Type"]="application/x-www-form-urlencoded"),t.headers&&delete t.headers["Content-Length"],this.isSurge()||this.isLoon())this.isSurge()&&this.isNeedRewrite&&(t.headers=t.headers||{},Object.assign(t.headers,{"X-Surge-Skip-Scripting":!1})),$httpClient.post(t,(t,s,i)=>{!t&&s&&(s.body=i,s.statusCode=s.status),e(t,s,i)});else if(this.isQuanX())t.method="POST",this.isNeedRewrite&&(t.opts=t.opts||{},Object.assign(t.opts,{hints:!1})),$task.fetch(t).then(t=>{const{statusCode:s,statusCode:i,headers:r,body:o}=t;e(null,{status:s,statusCode:i,headers:r,body:o},o)},t=>e(t));else if(this.isNode()){this.initGotEnv(t);const{url:s,...i}=t;this.got.post(s,i).then(t=>{const{statusCode:s,statusCode:i,headers:r,body:o}=t;e(null,{status:s,statusCode:i,headers:r,body:o},o)},t=>{const{message:s,response:i}=t;e(s,i,i&&i.body)})}}time(t){let e={"M+":(new Date).getMonth()+1,"d+":(new Date).getDate(),"H+":(new Date).getHours(),"m+":(new Date).getMinutes(),"s+":(new Date).getSeconds(),"q+":Math.floor(((new Date).getMonth()+3)/3),S:(new Date).getMilliseconds()};/(y+)/.test(t)&&(t=t.replace(RegExp.$1,((new Date).getFullYear()+"").substr(4-RegExp.$1.length)));for(let s in e)new RegExp("("+s+")").test(t)&&(t=t.replace(RegExp.$1,1==RegExp.$1.length?e[s]:("00"+e[s]).substr((""+e[s]).length)));return t}msg(e=t,s="",i="",r){const o=t=>{if(!t)return t;if("string"==typeof t)return this.isLoon()?t:this.isQuanX()?{"open-url":t}:this.isSurge()?{url:t}:void 0;if("object"==typeof t){if(this.isLoon()){let e=t.openUrl||t.url||t["open-url"],s=t.mediaUrl||t["media-url"];return{openUrl:e,mediaUrl:s}}if(this.isQuanX()){let e=t["open-url"]||t.url||t.openUrl,s=t["media-url"]||t.mediaUrl;return{"open-url":e,"media-url":s}}if(this.isSurge()){let e=t.url||t.openUrl||t["open-url"];return{url:e}}}};if(this.isMute||(this.isSurge()||this.isLoon()?$notification.post(e,s,i,o(r)):this.isQuanX()&&$notify(e,s,i,o(r))),!this.isMuteLog){let t=["","==============\ud83d\udce3\u7cfb\u7edf\u901a\u77e5\ud83d\udce3=============="];t.push(e),s&&t.push(s),i&&t.push(i),console.log(t.join("\n")),this.logs=this.logs.concat(t)}}log(...t){t.length>0&&(this.logs=[...this.logs,...t]),console.log(t.join(this.logSeparator))}logErr(t,e){const s=!this.isSurge()&&!this.isQuanX()&&!this.isLoon();s?this.log("",`\u2757\ufe0f${this.name}, \u9519\u8bef!`,t.stack):this.log("",`\u2757\ufe0f${this.name}, \u9519\u8bef!`,t)}wait(t){return new Promise(e=>setTimeout(e,t))}done(t={}){const e=(new Date).getTime(),s=(e-this.startTime)/1e3;this.log("",`\ud83d\udd14${this.name}, \u7ed3\u675f! \ud83d\udd5b ${s} \u79d2`),this.log(),(this.isSurge()||this.isQuanX()||this.isLoon())&&$done(t)}}(t,e)}
