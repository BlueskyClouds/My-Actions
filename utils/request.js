const axios = require('axios');
const axiosCookieJarSupport = require('axios-cookiejar-support').default;
const tough = require('tough-cookie');
axiosCookieJarSupport(axios);

const err = (error) => {
  return Promise.reject(error)
}

var parseDefaultCookie = function (cookies) {
  let cookie = []
  if (Object.prototype.toString.call(cookies) === '[object String]') {
    cookie = cookies ? [cookies] : []
  } else if (Object.prototype.toString.call(cookies) === '[object Object]') {
    Object.keys(cookies).forEach(item => {
      cookie.push(item + '=' + cookies[item])
    })
  }
  return cookie.join('; ')
}

var setCookieString = function (jar, cookies, config) {
  let url
  if (config.url.indexOf('http') === 0) {
    url = config.url
  } else {
    url = config.baseURL + config.url
  }
  let uuuu = new URL(url)
  // console.log('setCookieString for', uuuu.origin)
  cookies = parseDefaultCookie(cookies)
  if (Object.prototype.toString.call(cookies) === '[object String]') {
    cookies.length && cookies.split('; ').forEach(cookie => {
      jar.setCookieSync(cookie, uuuu.origin + '/', {})
    })
  }
  return jar
}

module.exports = cookies => {
  const service = axios.create({
    headers: {
      Cookie: parseDefaultCookie(cookies)
    },
    jar: new tough.CookieJar(),
    timeout: 60000,
    withCredentials: true
  })
  service.interceptors.request.use(async config => {
    if (!('user-agent' in config.headers)) {
      config.headers['user-agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'
    }
    let jar = config.jar
    if (!jar) {
      jar = new tough.CookieJar()
    } else {
      config.headers['Cookie'] = ''
    }
    config.jar = setCookieString(jar, cookies, config)
    return config
  }, err)
  service.interceptors.response.use(async response => {
    return response
  }, err)
  return service;
}