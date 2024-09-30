
from TikTokLive import TikTokLiveClient
from TikTokLive.events import ConnectEvent, CommentEvent
import argparse
import requests
from loguru import logger
import json

def log_init_simple(name):
    format_str = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {module} {line} | {elapsed} | {message} | {extra}"

    logger.add(f'logs/{name}' + '-{time:YYYYMMDD}.log', rotation="00:00", level="DEBUG", enqueue=True,
               format=format_str)

log_init_simple("tiktok")

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--live_id", required=True, help="input live room id")
ap.add_argument("-a", "--app_id", required=True, help="input appid")
args = vars(ap.parse_args())

# 新建连接
client: TikTokLiveClient = TikTokLiveClient(unique_id = "@" + args["live_id"])

# 解码
@client.on(ConnectEvent)
async def on_connect(event: ConnectEvent):
    print(f"Connected to @{event.unique_id} (Room ID: {client.room_id}")

# 数据连接
async def on_comment(event: CommentEvent) -> None:
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
        'appid': int(args["app_id"]),
        'list': [
            {
                'content': event.comment,
                'nickname': event.user.nickname,
            },
        ],
        'type': 'other',
    }
    logger.info("请求: " + json.dumps(json_data, ensure_ascii=False))
    response = requests.post('https://c.lnsee.com/lxserv/api.php', params=params, headers=headers, json=json_data)
    logger.info("返回: " + response.text)
    print(f"{event.user.nickname} -> {event.comment}")

client.add_listener(CommentEvent, on_comment)

# 主函数
if __name__ == '__main__':
    try:
        client.run()
    except Exception as e:
        logger.info("直播间未开播: " + str(e))
