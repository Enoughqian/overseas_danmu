import requests
import time
import requests
import hashlib
import os
import re
import json
import time


def md5_string(s):
    # 创建 md5 对象
    md5 = hashlib.md5()
    # 更新要计算的内容，这里需要将字符串转换为字节
    md5.update(s.encode('utf-8'))
    # 获取16进制的哈希值
    return md5.hexdigest()

def get_sign(liveUuid):
    url = 'https://acs-m.lazada.co.id/h5/mtop.lazada.live.query/1.1/'
    params = {
        'jsv': '2.6.1',
        'appKey': '24677475',
        't': str(time.time()*1000).split(".")[0],
        'api': 'mtop.lazada.live.query',
        'v': '1.1',
        'type': 'originaljson',
        'isSec': '1',
        'AntiCreep': 'true',
        'timeout': '12000',
        'dataType': 'json',
        'sessionOption': 'AutoLoginOnly',
        'x-i18n-language': 'id',
        'x-i18n-regionID': 'ID'
    }
    
    headers = {
        'accept': 'application/json',
        'accept-language': 'zh-CN,zh;q=0.9',
        'content-type': 'application/x-www-form-urlencoded',
        'entrance': '',
        'origin': 'https://pages.lazada.co.id',
        'priority': 'u=1, i',
        'referer': 'https://pages.lazada.co.id',
        'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    }


    data = {
        'data': '{"liveUuid":"'+ str(liveUuid) +'","action":0}'
    }

    response = requests.post(url, params=params, headers=headers, data=data)
    
    cookies =  dict(response.cookies)
    
    d_token = cookies["_m_h5_tk"].split("_")[0]
    i = cookies["_m_h5_tk"].split("_")[1]
    
    g = "24677475"
    
    c_data = '{"liveUuid":"'+ liveUuid +'"}'
    pre_encode = d_token + "&" + i + "&" + g + "&" + c_data

    sign = md5_string(pre_encode)

    return sign, i, cookies


def get_data(liveUuid, live_id):
    url = 'https://acs-m.lazada.co.id/h5/mtop.lazada.live.interactive.chatmsg.lastest.query/1.0/'
    
    try:
        params_sign, params_t, params_cookies = get_sign(liveUuid)
        
        params = {
            'jsv': '2.6.1',
            'appKey': '24677475',
            't': str(params_t),
            'sign': params_sign,
            'api': 'mtop.lazada.live.interactive.chatmsg.lastest.query',
            'v': '1.0',
            'type': 'originaljson',
            'isSec': '1',
            'AntiCreep': 'true',
            'timeout': '12000',
            'dataType': 'json',
            'sessionOption': 'AutoLoginOnly',
            'x-i18n-language': 'id',
            'x-i18n-regionID': 'ID'
        }

        headers = {
            'accept': 'application/json',
            'accept-language': 'zh-CN,zh;q=0.9',
            'content-type': 'application/x-www-form-urlencoded',
            'entrance': '',
            'origin': 'https://pages.lazada.co.id',
            'priority': 'u=1, i',
            'referer': 'https://pages.lazada.co.id',
            'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
        }
        
        data = {
            'data': '{"liveUuid":"'+liveUuid+'"}'
        }

        response = requests.post(url, params=params, headers=headers, data=data, cookies=params_cookies)
        json_data = response.json()

        logger.info(json.dumps(json_data, ensure_ascii=False))
        try:
            content_data = json_data["data"]["data"]
        except:
            content_data = []
        # 弹幕获取
        result = []
        for temp in content_data:
            temp_nick_name = temp["userNickname"]
            temp_content = temp["msgBody"]
            print("{}: {}".format(temp_nick_name, temp_content))
            temp_data = {
                "nickname": temp_nick_name,
                "content": temp_content
            }
            result.append(temp_data)
            logger.info(json.dumps(temp_data, ensure_ascii=False))
        
        # 上传直播间
        for temp in result:
            headers = {
                'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
                'X-Token': '1_1723725818_f5f45088c652b49806f89e61c92a2fcc',
                'sec-ch-ua-mobile': '?0',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                'Content-Type': 'application/json',
                'Accept': 'application/json, text/plain, */*',
                'Referer': 'https://c.lnsee.com/lxweb/',
                'sec-ch-ua-platform': '"macOS"',
            }

            params = {
                'api': 'UploadCommentList',
            }

            json_data = {
                'appid': int(live_id),
                'list': [
                    {
                        'content': temp["content"],
                        'nickname': temp["nickname"],
                    },
                ],
                'type': 'other',
            }
            logger.info("请求: " + json.dumps(json_data, ensure_ascii=False))
            response = requests.post('https://c.lnsee.com/lxserv/api.php', params=params, headers=headers, json=json_data)
            logger.info("返回: " + response.text)
    except:
        pass
   
if __name__ == "__main__":
	# 直播间uuid（url中的那段)
    import argparse
    import requests
    from loguru import logger
    import json

    def log_init_simple(name):
        format_str = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {module} {line} | {elapsed} | {message} | {extra}"

        logger.add(f'logs/{name}' + '-{time:YYYYMMDD}.log', rotation="00:00", level="DEBUG", enqueue=True,
                format=format_str)

    log_init_simple("lazada")

    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--live_id", required=True, help="input live room id")
    ap.add_argument("-a", "--app_id", required=True, help="input appid")
    args = vars(ap.parse_args())
    
    while True:
        content = get_data(args["live_id"], args["app_id"])
        time.sleep(2)

