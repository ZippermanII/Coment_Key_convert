# -*- coding: utf-8 -*-

#############################################################################################
###"Webdriver for Chrome","client.json","credentials.json","config.json","keydict.json"
### is required to use this script.
#############################################################################################

import httplib2
from oauth2client import tools
from oauth2client import client
from oauth2client.file import Storage
import time
import json
import os
import keypresser
from multiprocessing import Process
from selenium import webdriver
import asyncio
import websockets



# この関数だけ別プロセスで実行 Websocket送信側
def run_client(video_id):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')

    browser = webdriver.Chrome(chrome_options=chrome_options)
    url = "https://www.youtube.com/live_chat?v=" + video_id
    browser.get(url)
    browser.implicitly_wait(1)

    # サンプルでは↓のように直接文字列で書いているが 見づらいので別ファイル（insert.js）にした
    # browser.execute_script("""。。長い省略。。""")
    with open('insert.js', encoding='utf-8') as f:
        s = f.read()
        browser.execute_script(s)

    # １０秒に意味はない 終了しないようにしてるだけ
    # コメント取得自体はselenium上のjsに全部任せているので特にやることも無い
    while True:
        time.sleep(10)


async def consumer_handler(websocket, path):
    print("start consume")
    while True:
        message = await websocket.recv()  # 非同期で受信待ち
        comments_Json = json.loads(message)  # comments:複数のコメントデータ
        for comment_data in comments_Json:  # comment:1件のコメントデータ
            comment = ""
            for run in comment_data:
                comment += run["text"]

            initial = comment[0]
            second = comment[-1]
            enabled_command = ["a", "b", "x", "y", "u", "d", "l", "r"]
            enabled_second = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
            if initial in enabled_command:
                initial = 'y' + initial
                waitsecond = 0.5
                if second in enabled_second:
                    waitsecond = int(second)
                print(comment)
                print("コマンドです")
                key = int(KEYDICT[initial], 0)
                keypress_convert(key, waitsecond, KEYDICT)
            else:
                print(comment)



if __name__ == "__main__":

    config_json_path = os.path.join(os.path.abspath(os.path.dirname(__file__)) + "/ignore", 'config.json')
    keyditc_json_path = os.path.join(os.path.abspath(os.path.dirname(__file__)) + "/ignore", 'keydict.json')
    CONFIG = json.load(open(config_json_path))
    KEYDICT = json.load(open(keyditc_json_path))

    credentials_path = os.path.join(os.path.abspath(os.path.dirname(__file__)) + "/ignore", "credentials.json")
    if os.path.exists(credentials_path):
        # 認証済み
        store = Storage(credentials_path)
        credentials = store.get()
    else:
        # 認証処理
        f = os.path.join(os.path.abspath(os.path.dirname(__file__)) + "/ignore", "client.json")
        scope = "https://www.googleapis.com/auth/youtube.readonly"
        flow = client.flow_from_clientsecrets(f, scope)
        flow.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36"
        credentials = tools.run_flow(flow, Storage(credentials_path))

    http = credentials.authorize(httplib2.Http())
    url_get_livestremingVideoID = "https://www.googleapis.com/youtube/v3/search?part=id&channelId=UCwBkMy_K3XrQoWqQkXZvZiA&eventType=live&type=video&key="
    url_get_livestremingVideoID += CONFIG['YoutubeAPIkey']
    res, receivedata = http.request(url_get_livestremingVideoID)
    data = json.loads(receivedata.decode())
    video_id = data["items"][0]["id"]["videoId"]

    client = Process(target=run_client, args=(video_id,))
    client.start()

    keypress_convert = keypresser.keypress_convert
    event_loop = asyncio.get_event_loop()

    start_server = websockets.serve(consumer_handler, 'localhost', 8089)
    event_loop.run_until_complete(start_server)
    event_loop.run_forever()

