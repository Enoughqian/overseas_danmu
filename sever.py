import pandas as pd
import os
import streamlit as st
import requests
import json

area_map = {
    "越南": "vn",
    "菲律宾": "ph",
    "马来": "com.my"
}

def get_connect_params(session_id, area_params):
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'max-age=0',
        'priority': 'u=0, i',
        'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    }
    cookies = {}

    # 请求接口
    try:
        response = requests.get('https://live.shopee.{}/api/v1/session/{}'.format(area_params, session_id), cookies=cookies, headers=headers, timeout=10)
        response_data = response.json()
        title = response_data["data"]["session"]["title"]
        chatroom_id = response_data["data"]["session"]["chatroom_id"]
        return {"message": "添加成功", "state": 0, "data": {"title": title, "chatroom_id": chatroom_id}}
    except:
        return {"message": "请求信息失败", "state": 1}

# 增加shopee某条
def insert_shopee_table(appid, area, session_id):
    appid = str(appid)
    data = pd.read_csv("config/params_config.csv", encoding="utf-8")
    data["灵犀id"] = data["灵犀id"].apply(lambda x: str(x))

    if area not in area_map.keys():
        return {"message": "国家不存在", "state": 1}
    else:
        if appid in data["灵犀id"].values:
            return {"message": "直播间已经添加过", "state": 1}
        else:
            try:
                area_params = area_map[area]
                result = get_connect_params(session_id, area_params)

                chatroom_id = result["data"]["chatroom_id"]
                title = result["data"]["title"]

                if result["state"] == 0:
                    temp_data = [
                        ["shopee",str(appid), str(session_id), str(area), str(area_params), str(chatroom_id), title, "-"]
                    ]
                    temp_data = pd.DataFrame(temp_data, columns = ['平台名称','灵犀id', '场次id', '地区', '地区参数', '连接参数', '直播间名称',"登录参数"])
                    
                    final_result = pd.concat([data, temp_data], axis=0)
                    final_result = final_result.drop_duplicates(subset=["灵犀id"], inplace=False, keep="first")
                    final_result.to_csv("config/params_config.csv", encoding="utf-8", index=None)
                    gen_csv_command()
                    return {"message": "添加成功!", "state": 0}
                else:
                    return result
            except:
                return {"message": "添加失败,未找到对应参数!", "state": 0}

# 增加支付宝
def insert_zhifubao_table(appid, live_id, token_info):
    try:
        print("接收到的cookie: ", token_info)
        token_info = token_info.strip().split("ALIPAYJSESSIONID=")[1].split(";")[0]
    except:
        return {"message": "添加失败,cookie状态异常!", "state": 0}
    appid = str(appid).strip()
    data = pd.read_csv("config/params_config.csv", encoding="utf-8")
    data["灵犀id"] = data["灵犀id"].apply(lambda x: str(x))

    if appid in data["灵犀id"].values:
        return {"message": "直播间已经添加过", "state": 1}
    else:
        try:
            # 获取appid
            cookies = {
                'ALIPAYJSESSIONID': str(token_info).strip()
            }

            headers = {
                'accept': '*/*',
                'accept-language': 'zh-CN,zh;q=0.9',
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
                'sourceId': 'S',
            }
            
            response = requests.get('https://contentweb.alipay.com/life/getAppEnv.json', params=params, cookies=cookies, headers=headers, timeout=3)

            app_data = response.json()
            zhifubao_appid = app_data["result"]["appId"]

            # 抓取正在直播的room_id,和写的直播间id校验
            params = {
                'appId': str(zhifubao_appid),
                'pageNum': '1',
                'pageSize': '20',
                '_input_charset': 'utf-8',
                '_output_charset': 'utf-8'
            }
            response = requests.get(
                'https://contentweb.alipay.com/life/live/v2/queryAllLiveList.json',
                params=params,
                cookies=cookies,
                headers=headers,
            )

            room_info = response.json()

            now_live_id = ""
            for i in room_info["result"]:
                if i.get("liveRoomStatus","") == "STARTING":
                    now_live_id = str(i["liveId"])
                    now_title = str(i["liveTitle"])
            if now_live_id == live_id:
                temp_data = [
                    ["支付宝直播",str(appid), str(now_live_id), str("中国"), str("-"), str(now_live_id), now_title, token_info]
                ]
                temp_data = pd.DataFrame(temp_data, columns = ['平台名称','灵犀id', '场次id', '地区', '地区参数', '连接参数', '直播间名称',"登录参数"])
                
                final_result = pd.concat([data, temp_data], axis=0)
                final_result = final_result.drop_duplicates(subset=["灵犀id"], inplace=False, keep="first")
                final_result.to_csv("config/params_config.csv", encoding="utf-8", index=None)
                gen_csv_command()
                return {"message": "添加成功!", "state": 0}
            else:
                return {"message": "添加失败,主态cookie状态异常!", "state": 0}

            
        except:
            return {"message": "添加失败,未找到对应登录账号!", "state": 0}

def gen_csv_command():
    data = pd.read_csv("config/params_config.csv", encoding="utf-8")
    result = []
    for i in data.values:
        if i[0] == "shopee":
            command = "python -m script.get_shopee -i {} -a {} -c {}".format(i[5], i[1], i[4])
        if i[0] == "tiktok":
            command = "python -m script.get_tiktok -i {} -a {}".format(i[5], i[1])
        if i[0] == "支付宝直播":
            command = "python -m script.get_ali -i {} -a {} -t {}".format(i[5], i[1], i[7])
        if i[0] == "lazada":
            command = "python -m script.get_lazada -i {} -a {}".format(i[5], i[1])
        result.append(command)
    with open("config/commands.txt","w") as f:
        f.write("\n".join(result).strip())

# 增加shopee某条
def insert_tiktok_table(appid, session_id):
    appid = str(appid)
    data = pd.read_csv("config/params_config.csv", encoding="utf-8")
    data["灵犀id"] = data["灵犀id"].apply(lambda x: str(x))

    if appid in data["灵犀id"].values:
        return {"message": "直播间已经添加过", "state": 1}
    else:
        try:
            chatroom_id = session_id
            title = "-"

            temp_data = [
                ["tiktok", str(appid), str(session_id), "不限地区", str(session_id), str(chatroom_id), title,"-"]
            ]
            temp_data = pd.DataFrame(temp_data, columns = ['平台名称','灵犀id', '场次id', '地区', '地区参数', '连接参数', '直播间名称',"登录参数"])
            
            final_result = pd.concat([data, temp_data], axis=0)
            final_result = final_result.drop_duplicates(subset=["灵犀id"], inplace=False, keep="first")
            
            final_result.to_csv("config/params_config.csv", encoding="utf-8", index=None)
            gen_csv_command()
            return {"message": "添加成功!", "state": 0}
        except:
            return {"message": "添加失败,未找到对应参数!", "state": 0}

def insert_lazada_table(appid, session_id):
    appid = str(appid)
    data = pd.read_csv("config/params_config.csv", encoding="utf-8")
    data["灵犀id"] = data["灵犀id"].apply(lambda x: str(x))

    if appid in data["灵犀id"].values:
        return {"message": "直播间已经添加过", "state": 1}
    else:
        try:
            chatroom_id = session_id
            title = "-"

            temp_data = [
                ["lazada", str(appid), str(session_id), "不限地区", str(session_id), str(chatroom_id), title,"-"]
            ]
            temp_data = pd.DataFrame(temp_data, columns = ['平台名称','灵犀id', '场次id', '地区', '地区参数', '连接参数', '直播间名称',"登录参数"])
            
            final_result = pd.concat([data, temp_data], axis=0)
            final_result = final_result.drop_duplicates(subset=["灵犀id"], inplace=False, keep="first")
            
            final_result.to_csv("config/params_config.csv", encoding="utf-8", index=None)
            gen_csv_command()
            return {"message": "添加成功!", "state": 0}
        except:
            return {"message": "添加失败,未找到对应参数!", "state": 0}
# 删除某条
def delete_table(appid):
    appid = str(appid)
    data = pd.read_csv("config/params_config.csv", encoding="utf-8")
    data["灵犀id"] = data["灵犀id"].apply(lambda x: str(x))
    
    data = data[data["灵犀id"] != appid]
    data.to_csv("config/params_config.csv", encoding="utf-8", index=None)
    gen_csv_command()

# 显示列表
def get_list(dtype):
    data = pd.read_csv("config/params_config.csv", encoding="utf-8")
    result = []
    simple_result = []
    for i in data.values:
        temp_platform = str(i[0])
        temp_appid = str(i[1])
        temp_room_id = str(i[2])
        temp_area = str(i[3])
        temp_title = str(i[6])
        temp_content = temp_platform + "|" +temp_appid + "   |   " + temp_room_id + "   |   " + temp_area + "   |   " + temp_title
        result.append(temp_content)

        simple_result.append(temp_appid)
    if dtype == "str":
        result =  "</p><p>".join(result)
        return "<p>" + result + "</p>"
    else:
        return simple_result

# 触发添加，弹出，刷新
def toggle_button_click_add(platform, appid, session_id, area, token_info):
    if not st.session_state.button_clicked:
        if str(appid) != "" and str(session_id) != "":
            # 执行数据处理函数并将结果输出
            if platform == "shopee":
                result = insert_shopee_table(appid, area, session_id)
            elif platform == "tiktok":
                result = insert_tiktok_table(appid, session_id)
            elif platform == "支付宝直播":
                result = insert_zhifubao_table(appid, session_id, token_info)
            elif platform == "lazada":
                result = insert_lazada_table(appid, session_id)
            st.write("处理结果:", result["message"])

            # 将按钮状态标记为已点击
            st.session_state.button_clicked = True
        else:
            st.write("存在信息未补全")
    else:
        # 如果按钮已经被点击过，可以在这里处理，例如重置状态
        st.session_state.button_clicked = False
        st.write("请输入信息")

# 触发添加，弹出，刷新
def toggle_button_click_del(appid):
    if not st.session_state.button_clicked:
        if str(appid) != "":
            # 执行数据处理函数并将结果输出
            delete_table(appid)
            # 将按钮状态标记为已点击
            st.session_state.button_clicked = True
        else:
            st.write("")
    else:
        # 如果按钮已经被点击过，可以在这里处理，例如重置状态
        st.session_state.button_clicked = False
        st.write("请选择直播间id")
# 主函数
def main():
    st.title('弹幕抓取干预')    
    st.markdown("### 当前监控直播间", unsafe_allow_html=True)
    st.markdown(get_list("str"), unsafe_allow_html=True)

    st.session_state.button_clicked = False

    # 新增直播间，显示地区列表供选择
    st.markdown("### 新增直播间", unsafe_allow_html=True)
    # 平台
    platform_list = ["shopee","tiktok", "支付宝直播","lazada"]
    platform = st.selectbox('请选择直播间平台:', [str(temp) for temp in platform_list])
    appid = st.text_input("请输入appid: ")
    session_id = st.text_input("请输入直播间id: ")
    token_info = st.text_input("请输入主态cookie(仅支付宝): ")

    area = list(area_map.keys())
    area = st.selectbox('请选择直播间国家(仅shopee):', [str(temp) for temp in area])
    st.button("点击新增直播间", on_click=toggle_button_click_add, args = (platform, appid, session_id, area, token_info,))

    # 通过appid删除直播间
    st.markdown("### 删除直播间", unsafe_allow_html=True)
    
    appid_list = get_list("list")
    appid = st.selectbox('请选择待删除直播间:', [str(temp) for temp in appid_list])

    st.button("点击删除直播间", on_click=toggle_button_click_del, args = (appid, ))

if __name__ == '__main__':
    main()