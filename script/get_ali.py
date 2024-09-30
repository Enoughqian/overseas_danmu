import requests
import time
import requests
import hashlib
import os
import re
import json
import time


# 获取数据
def get_data(live_id, ali_token_id, appid):
    # 获取appid
    try:
        cookies = {
            "ALIPAYJSESSIONID": ali_token_id
        }

        headers = {
            'accept': 'application/json',
            'accept-language': 'zh-CN,zh;q=0.9',
            'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'origin': 'https://zlive.alipay.com',
            'priority': 'u=1, i',
            'referer': 'https://zlive.alipay.com/',
            'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-cookie-deprecation': 'label_only_3',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        }

        params = {
            '_input_charset': 'utf-8',
            '_output_charset': 'utf-8'
        }

        data = {
            'liveId': live_id,
        }
        

        response = requests.post(
            'https://contentweb.alipay.com/life/live/v2/interact/recentList.json',
            params=params,
            cookies=cookies,
            headers=headers,
            data=data,
        )
        
        json_data = response.json()
        logger.info(json.dumps(json_data, ensure_ascii=False))
        
        try:
            content_data = json_data["result"]["liveCommentVOList"]
        except:
            content_data = []

        # 弹幕获取
        result = []
        
        for temp in content_data:
            temp_nick_name = temp["username"]
            temp_content = temp["content"]
            temp_comment_id = temp["commentId"]
            if os.path.exists("ali_map.txt") == False:
                with open("ali_map.txt", "w") as f:
                    f.write("")
            with open("ali_map.txt", "r") as f:
                have_done = f.read()
            have_done = set([i.strip() for i in have_done.strip().split("\n")])
            if temp_comment_id in have_done:
                continue
            else:
                have_done = list(have_done)
                have_done.append(temp_comment_id)
                with open("ali_map.txt", "w") as f:
                    f.write("\n".join(have_done))

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
                'appid': int(appid),
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

    log_init_simple("ali")


    # live_id, ali_token_id, appid
    

    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--live_id", required=True, help="input live room id")
    ap.add_argument("-t", "--ali_token_id", required=True, help="input ali token id")
    ap.add_argument("-a", "--app_id", required=True, help='input lingxi app id')
    args = vars(ap.parse_args())
    
    while True:
        content = get_data(args["live_id"], args["ali_token_id"], args["app_id"])
        time.sleep(2)

