/****
 *
 * @description 腾讯视频好莱坞会员V力值签到，手机签到和领取任务及奖励。
 * @author BlueSkyClouds
 * @create_at 2020-10-30
 */

const $ = new Env('腾讯视频会员签到');
const notify = $.isNode() ? require('../sendNotify') : '';
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
    if(process.env.V_REF_URL.indexOf('https://access.video.qq.com/user/auth_refresh?') > -1 ) {
        ref_url = process.env.V_REF_URL
    } else {
        ref_url = `https://access.video.qq.com/user/auth_refresh?${process.env.V_REF_URL}`
    }
    //验证V_REF_URL和cookie是否填写正确
    ref_url_ver()
} else {
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
    const needParams = ["tvfe_boss_uuid","video_guid","video_platform","pgv_pvid","pgv_info","pgv_pvi","pgv_si","_qpsvr_localtk","RK","ptcz","ptui_loginuin","main_login","vqq_access_token","vqq_appid","vqq_openid","vqq_vuserid","vqq_vusession"]
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
            const { vqq_vusession } = parseSet(e.headers['set-cookie'])
            auth['vqq_vusession'] = vqq_vusession
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
        if (error) {
            $.log(error);
            console.log("腾讯视频会员签到", "验证ref_url请求失败 ‼️‼️", error)
        } else {
            if (data.match(/nick/)) { //通过验证获取QQ昵称参数来判断是否正确
                console.log("验证成功，执行主程序")
                //console.log(data)
                exports.main()
            } else {
                console.log("验证失败,无法获取个人资料")

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
                //判断是否为Cookie失效时才提醒
                if(SEND_KEY){
                    console.log("腾讯视频会员签到", "", date.getMonth() + 1 + "月" + date.getDate() + "日, " + msg )
                }else{
                    notify.sendNotify("腾讯视频会员签到", msg);
                    console.log("腾讯视频会员签到", "", date.getMonth() + 1 + "月" + date.getDate() + "日, " + msg )
                }
                //签到成功才执行任务签到
                Collect_task()
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
                console.log("腾讯视频会员下载任务签到", "", "签到失败, 任务未完成 ‼️‼️")
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
                console.log("腾讯视频会员赠送任务签到", "", "签到失败, 任务未完成 ‼️‼️")
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
                console.log("腾讯视频会员弹幕任务签到", "", "签到失败, 任务未完成 ‼️‼️")
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
                console.log("腾讯视频会员观看任务签到", "", "签到失败, 任务未完成 ‼️‼️")
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
function Env(t,s){return new class{constructor(t,s){this.name=t,this.data=null,this.dataFile="box.dat",this.logs=[],this.logSeparator="\n",this.startTime=(new Date).getTime(),Object.assign(this,s),this.log("",`\ud83d\udd14${this.name}, \u5f00\u59cb!`)}isNode(){return"undefined"!=typeof module&&!!module.exports}isQuanX(){return"undefined"!=typeof $task}isSurge(){return"undefined"!=typeof $httpClient&&"undefined"==typeof $loon}isLoon(){return"undefined"!=typeof $loon}getScript(t){return new Promise(s=>{$.get({url:t},(t,e,i)=>s(i))})}runScript(t,s){return new Promise(e=>{let i=this.getdata("@chavy_boxjs_userCfgs.httpapi");i=i?i.replace(/\n/g,"").trim():i;let o=this.getdata("@chavy_boxjs_userCfgs.httpapi_timeout");o=o?1*o:20,o=s&&s.timeout?s.timeout:o;const[h,a]=i.split("@"),r={url:`http://${a}/v1/scripting/evaluate`,body:{script_text:t,mock_type:"cron",timeout:o},headers:{"X-Key":h,Accept:"*/*"}};$.post(r,(t,s,i)=>e(i))}).catch(t=>this.logErr(t))}loaddata(){if(!this.isNode())return{};{this.fs=this.fs?this.fs:require("fs"),this.path=this.path?this.path:require("path");const t=this.path.resolve(this.dataFile),s=this.path.resolve(process.cwd(),this.dataFile),e=this.fs.existsSync(t),i=!e&&this.fs.existsSync(s);if(!e&&!i)return{};{const i=e?t:s;try{return JSON.parse(this.fs.readFileSync(i))}catch(t){return{}}}}}writedata(){if(this.isNode()){this.fs=this.fs?this.fs:require("fs"),this.path=this.path?this.path:require("path");const t=this.path.resolve(this.dataFile),s=this.path.resolve(process.cwd(),this.dataFile),e=this.fs.existsSync(t),i=!e&&this.fs.existsSync(s),o=JSON.stringify(this.data);e?this.fs.writeFileSync(t,o):i?this.fs.writeFileSync(s,o):this.fs.writeFileSync(t,o)}}lodash_get(t,s,e){const i=s.replace(/\[(\d+)\]/g,".$1").split(".");let o=t;for(const t of i)if(o=Object(o)[t],void 0===o)return e;return o}lodash_set(t,s,e){return Object(t)!==t?t:(Array.isArray(s)||(s=s.toString().match(/[^.[\]]+/g)||[]),s.slice(0,-1).reduce((t,e,i)=>Object(t[e])===t[e]?t[e]:t[e]=Math.abs(s[i+1])>>0==+s[i+1]?[]:{},t)[s[s.length-1]]=e,t)}getdata(t){let s=this.getval(t);if(/^@/.test(t)){const[,e,i]=/^@(.*?)\.(.*?)$/.exec(t),o=e?this.getval(e):"";if(o)try{const t=JSON.parse(o);s=t?this.lodash_get(t,i,""):s}catch(t){s=""}}return s}setdata(t,s){let e=!1;if(/^@/.test(s)){const[,i,o]=/^@(.*?)\.(.*?)$/.exec(s),h=this.getval(i),a=i?"null"===h?null:h||"{}":"{}";try{const s=JSON.parse(a);this.lodash_set(s,o,t),e=this.setval(JSON.stringify(s),i)}catch(s){const h={};this.lodash_set(h,o,t),e=this.setval(JSON.stringify(h),i)}}else e=$.setval(t,s);return e}getval(t){return this.isSurge()||this.isLoon()?$persistentStore.read(t):this.isQuanX()?$prefs.valueForKey(t):this.isNode()?(this.data=this.loaddata(),this.data[t]):this.data&&this.data[t]||null}setval(t,s){return this.isSurge()||this.isLoon()?$persistentStore.write(t,s):this.isQuanX()?$prefs.setValueForKey(t,s):this.isNode()?(this.data=this.loaddata(),this.data[s]=t,this.writedata(),!0):this.data&&this.data[s]||null}initGotEnv(t){this.got=this.got?this.got:require("got"),this.cktough=this.cktough?this.cktough:require("tough-cookie"),this.ckjar=this.ckjar?this.ckjar:new this.cktough.CookieJar,t&&(t.headers=t.headers?t.headers:{},void 0===t.headers.Cookie&&void 0===t.cookieJar&&(t.cookieJar=this.ckjar))}get(t,s=(()=>{})){t.headers&&(delete t.headers["Content-Type"],delete t.headers["Content-Length"]),this.isSurge()||this.isLoon()?$httpClient.get(t,(t,e,i)=>{!t&&e&&(e.body=i,e.statusCode=e.status),s(t,e,i)}):this.isQuanX()?$task.fetch(t).then(t=>{const{statusCode:e,statusCode:i,headers:o,body:h}=t;s(null,{status:e,statusCode:i,headers:o,body:h},h)},t=>s(t)):this.isNode()&&(this.initGotEnv(t),this.got(t).on("redirect",(t,s)=>{try{const e=t.headers["set-cookie"].map(this.cktough.Cookie.parse).toString();this.ckjar.setCookieSync(e,null),s.cookieJar=this.ckjar}catch(t){this.logErr(t)}}).then(t=>{const{statusCode:e,statusCode:i,headers:o,body:h}=t;s(null,{status:e,statusCode:i,headers:o,body:h},h)},t=>s(t)))}post(t,s=(()=>{})){if(t.body&&t.headers&&!t.headers["Content-Type"]&&(t.headers["Content-Type"]="application/x-www-form-urlencoded"),delete t.headers["Content-Length"],this.isSurge()||this.isLoon())$httpClient.post(t,(t,e,i)=>{!t&&e&&(e.body=i,e.statusCode=e.status),s(t,e,i)});else if(this.isQuanX())t.method="POST",$task.fetch(t).then(t=>{const{statusCode:e,statusCode:i,headers:o,body:h}=t;s(null,{status:e,statusCode:i,headers:o,body:h},h)},t=>s(t));else if(this.isNode()){this.initGotEnv(t);const{url:e,...i}=t;this.got.post(e,i).then(t=>{const{statusCode:e,statusCode:i,headers:o,body:h}=t;s(null,{status:e,statusCode:i,headers:o,body:h},h)},t=>s(t))}}time(t){let s={"M+":(new Date).getMonth()+1,"d+":(new Date).getDate(),"H+":(new Date).getHours(),"m+":(new Date).getMinutes(),"s+":(new Date).getSeconds(),"q+":Math.floor(((new Date).getMonth()+3)/3),S:(new Date).getMilliseconds()};/(y+)/.test(t)&&(t=t.replace(RegExp.$1,((new Date).getFullYear()+"").substr(4-RegExp.$1.length)));for(let e in s)new RegExp("("+e+")").test(t)&&(t=t.replace(RegExp.$1,1==RegExp.$1.length?s[e]:("00"+s[e]).substr((""+s[e]).length)));return t}msg(s=t,e="",i="",o){const h=t=>!t||!this.isLoon()&&this.isSurge()?t:"string"==typeof t?this.isLoon()?t:this.isQuanX()?{"open-url":t}:void 0:"object"==typeof t&&(t["open-url"]||t["media-url"])?this.isLoon()?t["open-url"]:this.isQuanX()?t:void 0:void 0;$.isMute||(this.isSurge()||this.isLoon()?$notification.post(s,e,i,h(o)):this.isQuanX()&&$notify(s,e,i,h(o))),this.logs.push("","==============\ud83d\udce3\u7cfb\u7edf\u901a\u77e5\ud83d\udce3=============="),this.logs.push(s),e&&this.logs.push(e),i&&this.logs.push(i)}log(...t){t.length>0?this.logs=[...this.logs,...t]:console.log(this.logs.join(this.logSeparator))}logErr(t,s){const e=!this.isSurge()&&!this.isQuanX()&&!this.isLoon();e?$.log("",`\u2757\ufe0f${this.name}, \u9519\u8bef!`,t.stack):$.log("",`\u2757\ufe0f${this.name}, \u9519\u8bef!`,t)}wait(t){return new Promise(s=>setTimeout(s,t))}done(t={}){const s=(new Date).getTime(),e=(s-this.startTime)/1e3;this.log("",`\ud83d\udd14${this.name}, \u7ed3\u675f! \ud83d\udd5b ${e} \u79d2`),this.log(),(this.isSurge()||this.isQuanX()||this.isLoon())&&$done(t)}}(t,s)}
