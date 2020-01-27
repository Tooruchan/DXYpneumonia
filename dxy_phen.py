import requests
from bs4 import BeautifulSoup
import json
import re
from pyrogram import Client, InlineKeyboardButton, InlineKeyboardMarkup
import time
from datetime import datetime,timedelta,timezone
import pytz

app = Client("pneumonia_bot",
             proxy=dict(hostname="127.0.0.1", port=1090),
             bot_token="939655223:AAH7iLIVCrQUAssICSYukHVkjsCOlsRPnP4",
             api_id=135843,
             api_hash='777bebb1fd9b98eb2980fd1e7c3de9ab')

headers = {
    'authority': '3g.dxy.cn',
    'user-agent':
    'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Mobile Safari/537.36',
    'cookie': 'DXY_USER_GROUP=34',
}
def get_data():
    global date,newstr,province_str,app,timestamp
    response = requests.get('https://3g.dxy.cn/newh5/view/pneumonia',
                            headers=headers)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    province_rawdata = str(soup.find_all("script", id="getAreaStat")[0])[52:-20]
    stat_rawdata = str(soup.find_all("script",
                                    id="getStatisticsService")[0])[70:-20]
    stat_data = json.loads(stat_rawdata)
    pro_data = json.loads(province_rawdata)
    numbers = re.findall(r"\d*", str(stat_data["countRemark"]))
    timestamp = stat_data["modifyTime"] / 1000
    # print(timestamp)
    loctime = datetime.fromtimestamp(timestamp).astimezone(timezone(timedelta(hours=8)))
    dt = loctime.strftime("%Y-%m-%d %H:%M")
    date = '#2019新型冠状病毒\n截至 **{0}** (UTC +8)数据统计'.format(dt)
    while '' in numbers:
        numbers.remove('')
    # 数据格式：
    # 全国 确诊 1372 例 疑似 1983 例 \n
    # 死亡 41 例 治愈 39 例
    # print(numbers)
    newstr = "\n在中国境内确诊 **{0}** 例，疑似 **{1}** 例，死亡 **{2}** 例，治愈 **{3}** 例。\n".format(
        numbers[0], numbers[1], numbers[2], numbers[3])
    provinces = []
    for province in pro_data:
        #数据格式：
        #{
        #    "provinceName": "山西省",
        #    "provinceShortName": "山西",
        #    "confirmedCount": 6,
        #    "suspectedCount": 0,
        #    "curedCount": 0,
        #    "deadCount": 0
        #}
        province_name = "#{0}".format(province['provinceShortName'])
        if province['confirmedCount'] != 0:
            confirmed_count = '确诊 **{0}** 例'.format(province['confirmedCount'])
        else:
            confirmed_count = ''
        if province['suspectedCount'] != 0:
            suspected_count = '疑似 **{0}** 例'.format(province['suspectedCount'])
        else:
            suspected_count = ''
        if province['deadCount'] != 0:
            dead_count = '死亡 **{0}** 例'.format(province['deadCount'])
        else:
            dead_count = ''
        seperated_province = ' '.join(
            [province_name, confirmed_count, suspected_count, dead_count])
        provinces.append(seperated_province)
    province_str = '\n'.join(provinces)
def sendmsg():
    global date,newstr,province_str,app
    app.start()
    app.send_message(
        -1001146723984,
        #请在此处自行填写频道/群组ID，可以通过 Group Bulter 的 /id 命令来查询。
        '\n'.join([date, newstr, province_str]),
        parse_mode='md',
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("数据来源：丁香园", url="https://3g.dxy.cn/newh5/view/pneumonia")]]))
    app.stop()

def main():
    global date,newstr,province_str,app,timestamp
    #启动时先更新一次数据
    get_data()
    sendmsg()
    oldtimestamp = timestamp
    while True:
        #5分钟更新一次，这里的数据要改请按秒为单位计算。
        time.sleep(60*60)
        try:
            get_data()
            if timestamp == oldtimestamp:
                # 数据相同，不更新
                pass
            else:
                sendmsg()
        except KeyboardInterrupt as k:
            quit()
        except Exception as e:
            pass
        else:
            pass

if __name__ =="__main__":
    main()