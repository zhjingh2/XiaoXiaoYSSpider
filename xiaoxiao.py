from flask import Flask
from flask import request
import requests
import time
import json

XIAOXIAO_SEARCH_URL = 'http://fe2wzffedps4ejknbnnv.xiaoxiaoapps.com/search'
XIAOXIAO_M3U8_QUERY = 'https://fe2wzffedps4ejknbnnv.xiaoxiaoapps.com/vod/reqplay/'

headers = {
        "Accept" : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        "Upgrade-Insecure-Requests" : "1",
        "Accept-Language" : 'zh-cn',
        "User-Agent" : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.5 Safari/605.1.15',
    }

__all__ = ['app']
app = Flask(__name__)

@app.route('/')
def index():
    return 'XiaoXiao m3u8 Finder. Please use /search?wd=名称'

@app.route('/search', methods=['GET'])
def search():
    searchword = request.args.get('wd', '')
    return requestXiaoXiaoSearchWithWd(searchword)

def requestXiaoXiaoSearchWithWd(wd):
    params = {
        '_t' : (int(time.time()) * 1000),
        'pid' : '',
        's_device_id' : '5C5E1143-A51A-4D9D-935A-00B663A01142',
        's_os_version' : '13.3.1',
        's_platform' : 'ios',
        'wd' : wd,
    }

    response = requests.get(XIAOXIAO_SEARCH_URL, headers=headers, params=params, verify=False)
    jsonDic = json.loads(response.text)
    print(jsonDic)
    result = []
    for info in parseXiaoXiaoSearchWithResponse(jsonDic):
        m3u8url = requestM3U8WithInfo(info)
        result.append({'名称' : info[1], '集数' : info[3], '播放地址' : m3u8url})
    print(result)
    if len(result) > 0:
        return str(result)
    else:
        return "无搜索结果"

def parseXiaoXiaoSearchWithResponse(jsonDic):
    try:
        data = jsonDic['data']
        vodrows = data['vodrows']
        for vodrow in vodrows:
            vodid = vodrow['vodid']
            title = vodrow['title']
            playlist = vodrow['playlist']
            for play in playlist:
                playindex = play['playindex']
                play_name = play['play_name']
                yield (vodid, title, str(playindex), play_name)
    except:
        return None
    return None

def requestM3U8WithInfo(info):
    url = XIAOXIAO_M3U8_QUERY + info[0]
    params = {
        '_t': (int(time.time()) * 1000),
        'pid': '',
        'playindex' : info[2],
        's_device_id': '5C5E1143-A51A-4D9D-935A-00B663A01142',
        's_os_version': '13.3.1',
        's_platform': 'ios',
    }
    response = requests.get(url, headers=headers, params=params, verify=False)
    jsonDic = json.loads(response.text)
    return parseXiaoXiaoM3U8WithResponse(jsonDic)

def parseXiaoXiaoM3U8WithResponse(jsonDic):
    try:
        data = jsonDic['data']
        httpurl = data['httpurl']
        return httpurl
    except:
        return None
    return None

if __name__ == '__main__':
    app.run(host='0.0.0.0')