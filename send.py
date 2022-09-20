import random
from time import time, localtime
import cityinfo
from requests import get, post
from datetime import datetime, date
import sys
import os
import http.client, urllib
import json
from zhdate import ZhDate


def get_color():
    # 获取随机颜色
    get_colors = lambda n: list(map(lambda i: "#" + "%06x" % random.randint(0, 0xFFFFFF), range(n)))
    color_list = get_colors(100)
    return random.choice(color_list)


def get_access_token():
    # appId
    app_id = config["app_id"]
    # appSecret
    app_secret = config["app_secret"]
    post_url = ("https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}"
                .format(app_id, app_secret))
    try:
        access_token = get(post_url).json()['access_token']
    except KeyError:
        print("获取access_token失败，请检查app_id和app_secret是否正确")
        os.system("pause")
        sys.exit(1)
    # print(access_token)
    return access_token

def get_weather(province, city):
    # 城市id
    try:
        city_id = cityinfo.cityInfo[province][city]["AREAID"]
    except KeyError:
        print("推送消息失败，请检查省份或城市是否正确")
        os.system("pause")
        sys.exit(1)
    # city_id = 101280101
    # 毫秒级时间戳
    t = (int(round(time() * 1000)))
    headers = {
        "Referer": "http://www.weather.com.cn/weather1d/{}.shtml".format(city_id),
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    url = "http://d1.weather.com.cn/dingzhi/{}.html?_={}".format(city_id, t)
    response = get(url, headers=headers)
    response.encoding = "utf-8"
    response_data = response.text.split(";")[0].split("=")[-1]
    response_json = eval(response_data)
    # print(response_json)
    weatherinfo = response_json["weatherinfo"]
    # 天气
    weather = weatherinfo["weather"]
    # 最高气温
    temp = weatherinfo["temp"]
    # 最低气温
    tempn = weatherinfo["tempn"]
    return weather, temp, tempn

# 励志名言
def lizhi():
    if ( lizhi_API != "替换掉我"):
        conn = http.client.HTTPSConnection('api.tianapi.com')  # 接口域名
        params = urllib.parse.urlencode({'key': lizhi_API})
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        conn.request('POST', '/zaoan/index', params, headers)
        res = conn.getresponse()
        data = res.read()
        data = json.loads(data)
        return data["newslist"][0]["content"];
    else:
        return "今天的不开心就止于此吧，明天依旧光芒万丈呀宝贝"

#下雨概率和建议
def tip():
    if (tianqi_API != "替换掉我"):
        conn = http.client.HTTPSConnection('api.tianapi.com')  #接口域名
        params = urllib.parse.urlencode({'key':tianqi_API,'city':city})
        headers = {'Content-type':'application/x-www-form-urlencoded'}
        conn.request('POST','/tianqi/index',params,headers)
        res = conn.getresponse()
        data = res.read()
        data = json.loads(data)
        pop = data["newslist"][0]["pop"]
        tips = data["newslist"][0]["tips"]
        return pop,tips
    else:
        return "",""

# 推送信息
def send_message(to_user, access_token, city_name, weather, max_temperature, min_temperature  ,lizhi , pop, tips):
    url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}".format(access_token)
    week_list = ["星期日", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六"]
    year = localtime().tm_year
    month = localtime().tm_mon
    day = localtime().tm_mday
    today = datetime.date(datetime(year=year, month=month, day=day))
    week = week_list[today.isoweekday() % 7]
    data = {
        "touser": to_user,
        "template_id": config["template_id"],
        "url": "http://weixin.qq.com/download",
        "topcolor": "#FF0000",
        "data": {
            "date": {
                "value": "{} {}".format(today, week),
                "color": get_color()
            },
            "city": {
                "value": "城市:  " + city_name,
                "color": get_color()
            },
            "weather": {
                "value": "天气:  " + weather,
                "color": get_color()
            },
            "min_temperature": {
                "value": "最低气温:  " + min_temperature,
                "color": get_color()
            },
            "max_temperature": {
                "value": "最高气温:  " + max_temperature,
                "color": get_color()
            },
            "lizhi": {
                "value": "早安寄语:  " + lizhi,
                "color": get_color()
            },
            "pop": {
                "value": "降雨概率:  " + pop + "%",
                "color": get_color()
            },
            "tips": {
                "value": "今日建议:  " + tips,
                "color": get_color()
            }
        }
    }
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    response = post(url, headers=headers, json=data).json()
    if response["errcode"] == 40037:
        print("推送消息失败，请检查模板id是否正确")
    elif response["errcode"] == 40036:
        print("推送消息失败，请检查模板id是否为空")
    elif response["errcode"] == 40003:
        print("推送消息失败，请检查微信号是否正确")
    elif response["errcode"] == 0:
        print("推送消息成功")
    else:
        print(response)


if __name__ == "__main__":
    try:
        with open("config.txt", encoding="utf-8") as f:
            config = eval(f.read())
    except FileNotFoundError:
        print("推送消息失败，请检查config.txt文件是否与程序位于同一路径")
        os.system("pause")
        sys.exit(1)
    except SyntaxError:
        print("推送消息失败，请检查配置文件格式是否正确")
        os.system("pause")
        sys.exit(1)

    # 获取accessToken
    accessToken = get_access_token()
    # 接收的用户
    users = config["user"]
    # 传入省份和市获取天气信息
    province, city = config["province"], config["city"]
    weather, max_temperature, min_temperature = get_weather(province, city)
    # 获取励志古言API
    lizhi_API = config["lizhi_API"]
    # 获取天气预报API
    tianqi_API = config["tianqi_API"]
    # # 下雨概率和建议
    pop, tips = tip()
    # 励志名言
    lizhi = lizhi()
    # 公众号推送消息
    for user in users:
        send_message(user, accessToken, city, weather, max_temperature, min_temperature, lizhi , pop, tips )
    import time

    time_duration = 3.5
    time.sleep(time_duration)
