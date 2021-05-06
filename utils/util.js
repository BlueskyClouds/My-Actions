const os = require('os')
const path = require('path')
const fs = require('fs-extra')

module.exports = {
    async delCookiesFile(key) {
        let dir = path.join(os.homedir(), '.AutoSignMachine')
        if ('TENCENTCLOUD_RUNENV' in process.env && process.env.TENCENTCLOUD_RUNENV === 'SCF') {
            dir = path.join('/tmp', '.AutoSignMachine')
        }
        if (!fs.existsSync(dir)) {
            fs.mkdirpSync(dir)
        }
        let cookieFile = path.join(dir, 'cookieFile_' + key + '.txt')
        if (fs.existsSync(cookieFile)) {
            fs.unlinkSync(cookieFile)
        }
    },
    getCookies: (key) => {
        let dir = path.join(os.homedir(), '.AutoSignMachine')
        if ('TENCENTCLOUD_RUNENV' in process.env && process.env.TENCENTCLOUD_RUNENV === 'SCF') {
            dir = path.join('/tmp', '.AutoSignMachine')
        }
        if (!fs.existsSync(dir)) {
            fs.mkdirpSync(dir)
        }
        let cookieFile = path.join(dir, 'cookieFile_' + key + '.txt')
        if (fs.existsSync(cookieFile)) {
            let cookies = fs.readFileSync(cookieFile).toString('utf-8')
            return cookies
        }
        return ''
    },
    saveCookies: (key, cookies, cookiesJar) => {
        let dir = path.join(os.homedir(), '.AutoSignMachine')
        if ('TENCENTCLOUD_RUNENV' in process.env && process.env.TENCENTCLOUD_RUNENV === 'SCF') {
            dir = path.join('/tmp', '.AutoSignMachine')
        }
        if (!fs.existsSync(dir)) {
            fs.mkdirpSync(dir)
        }
        let cookieFile = path.join(dir, 'cookieFile_' + key + '.txt')
        let allcookies = {}
        if (cookies) {
            cookies.split('; ').map(c => {
                let item = c.split('=')
                allcookies[item[0]] = item[1] || ''
            })
        }
        if (cookiesJar) {
            cookiesJar.toJSON().cookies.map(c => {
                allcookies[c.key] = c.value || ''
            })
        }
        let cc = []
        for (let key in allcookies) {
            cc.push({
                key: key,
                value: allcookies[key] || ''
            })
        }
        fs.ensureFileSync(cookieFile)
        fs.writeFileSync(cookieFile, cc.map(c => c.key + '=' + c.value).join('; ')
        )
    },
    buildUnicomUserAgent: (options, tplname) => {
        var tpl = {
            'p': 'Mozilla/5.0 (Linux; Android {android_version}; {deviceModel} Build/{buildSn}; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/75.0.3770.143 Mobile Safari/537.36; unicom{version:{unicom_version},desmobile:{desmobile}};devicetype{deviceBrand:{deviceBrand},deviceModel:{deviceModel}};{yw_code:}'
        }
        var rdm = {
            android_version: '7.1.2',
            unicom_version: 'android@8.0100',
            deviceBrand: 'samsung',
            deviceModel: 'SM-G977N',
            buildSn: 'LMY48Z',
            desmobile: options.user
        }
        var fmt = (str, params) => {
            for (let key in params) {
                str = str.replace(new RegExp("\\{" + key + "\\}", "g"), params[key]);
            }
            return str
        }
        return fmt(tpl[tplname], Object.assign(rdm, options))
    }
}