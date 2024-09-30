import requests
import time
import requests
import hashlib
import os
import re
import json
import time


# 获取数据
def get_data(live_uuid, live_id):
    # 构造请求参数
    # 请求
    try:
        cookie = {}

        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'client-info': 'os=2;platform=9',
            # 'cookie': '_gcl_au=1.1.992100025.1718725774; SPC_F=s0LLuwT38Hbu1uiB0n5tkzvZx4XtMXl3; REC_T_ID=5cd60ae2-2d8a-11ef-8899-8265810d11dc; SPC_R_T_ID=eI1lphFk1zCKBftlKLvN1qwUloNkzL7KY01sNrJeaDvBQ6Vqq+0N0ihISx9ZEL9Yv7h2YoK13mnTp8OBk1bBuWZklyhLvhNJ4Y3qvtdTZY3Zs+lB27jp5obZPpTypshAhG8ewE0F3NuX1R1ypy9iOJ2w+AW1jl5RILCGlGrhTBU=; SPC_R_T_IV=MGNtRDlOcDAxMHhoVURGNA==; SPC_T_ID=eI1lphFk1zCKBftlKLvN1qwUloNkzL7KY01sNrJeaDvBQ6Vqq+0N0ihISx9ZEL9Yv7h2YoK13mnTp8OBk1bBuWZklyhLvhNJ4Y3qvtdTZY3Zs+lB27jp5obZPpTypshAhG8ewE0F3NuX1R1ypy9iOJ2w+AW1jl5RILCGlGrhTBU=; SPC_T_IV=MGNtRDlOcDAxMHhoVURGNA==; _fbp=fb.1.1718725944031.874405298671171448; _gid=GA1.2.173620926.1718876408; SPC_SI=KB9oZgAAAABJUG15TzhQQ+QeYAIAAAAAWVNzNjl3Znc=; AMP_TOKEN=%24NOT_FOUND; _ga=GA1.2.1210307198.1718725774; _ga_EZBZ7XZP0H=GS1.1.1718966399.9.1.1718966619.14.0.0',
            'origin': 'https://live.shopee.ph',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://live.shopee.ph/',
            'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            'x-livestreaming-source': 'shopee',
        }

        params = {
            'uuid': "2ff43941-649a-492b-afb1-71009d6530ac",
            'timestamp': '1718967059',
            'version': 'v2',
        }

        response = requests.get(
            'https://chatroom-live.shopee.{}/api/v1/fetch/chatroom/{}/message'.format(args["country"], live_uuid),
            params=params,
            headers=headers,
            cookies=cookie
        )
        json_data = response.json()
        logger.info(json.dumps(json_data, ensure_ascii=False))
        try:
            content_data = json_data["data"]["message"][0]["msgs"]
        except:
            content_data = []
        # 弹幕获取
        result = []
        for temp in content_data:
            temp_nick_name = temp["nickname"]
            temp_content = json.loads(temp["content"])["content"]
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

    log_init_simple("shopee")

    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--live_id", required=True, help="input live room id")
    ap.add_argument("-a", "--app_id", required=True, help="input appid")
    ap.add_argument("-c", "--country", required=True, help='input country')
    args = vars(ap.parse_args())
    
    while True:
        content = get_data(args["live_id"], args["app_id"])
        time.sleep(2)

