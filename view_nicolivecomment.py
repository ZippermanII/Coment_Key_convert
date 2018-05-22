# -*- coding: utf-8 -*-
import urllib, urllib3, http.cookiejar as cookielib, socket, re
from xml.etree import ElementTree
from urllib.request import build_opener, HTTPCookieProcessor
import asyncio
import keypresser

lv = ""

class NicoliveCommentReceiver:
    def __init__(self):
        self.LOGIN_URL = 'https://secure.nicovideo.jp/secure/login?site=niconico'
        self.LIVE_API_URL = 'http://watch.live.nicovideo.jp/api/'
        self.cookies = cookielib.CookieJar()
        cjhdr = urllib.request.HTTPCookieProcessor(self.cookies)
        self.opener = build_opener(cjhdr)

    def login(self, mail, password):
        if mail == 'user_session':
            self.set_user_session(password)
            return True
        values = {'mail_tel' : mail, 'password' : password}
        postdata = urllib.parse.urlencode(values)
        response = self.opener.open(self.LOGIN_URL, postdata.encode("utf-8"))
        page = response.read()
        for c in self.cookies:
            if c.name == 'user_session': return c.value
        return None

    def set_user_session(self, user_session):
        self.opener.addheaders.append(('Cookie', 'user_session=' + user_session))
        
    def get_lv(self):
        self.community_URL = 'http://com.nicovideo.jp/community/co3097203'
        html = urllib.request.urlopen(self.community_URL).read().decode('utf-8')
        m = re.search('watch/(lv[0-9]+)',html)
        if m is None:
            return None
        else:
            return m.group(1)
        
        

    async def get_comment(self,lv,KEYDICT):
        player_status_xml = self.opener.open(self.LIVE_API_URL + 'getplayerstatus?v=' + lv).read()
        player_status = ElementTree.fromstring(player_status_xml)
        addr = player_status.find("ms/addr").text
        port = int(player_status.find("ms/port").text)
        thread = player_status.find("ms/thread").text

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((addr, port))
        sock.setblocking(False)
        sock.send(bytes('<thread thread="{thread}" version="20061206" res_from="-1"/>\0'.format(thread=thread),"utf-8"))

        data = ''
        while True:
            while data.find("\0") == -1:
                event_loop = asyncio.get_event_loop()
                byetsdata = await event_loop.sock_recv(sock,1024)
                data += byetsdata.decode('utf-8')
            p = data.find("\0")
            d = ElementTree.fromstring(data[:p])
            data = data[p+1:]
            if d.tag == 'chat':
                num = int(d.get('no') or "-1")
                pre = int(d.get('premium') or "-1")
                vpos = int(d.get('vpos') or "-1")
                mail = d.get('mail')
                user_id = d.get('user_id')
                comment = d.text
                if comment == u"/disconnect" and pre == 2 : break
                if comment.startswith('/'): continue
                initial = comment[0]
                second = comment[-1]
                enabled_command = ["a", "b", "x", "y", "u", "d", "l", "r"]
                enabled_second = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
                if initial in enabled_command:
                    initial = 'n' + initial
                    waitsecond = 0.5
                    if second in enabled_second:
                        waitsecond = int(second)
                    print(comment)
                    print(initial)
                    print("コマンドです")
                    key = int(KEYDICT[initial], 0)
                    keypress_convert(key,waitsecond,KEYDICT)
                else:
                    print(comment)

if __name__ == "__main__":
    import os
    import json
    import time


    config_json_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config.json')
    keyditc_json_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'keydict.json')
    CONFIG = json.load(open(config_json_path))
    KEYDICT = json.load(open(keyditc_json_path))

    email = CONFIG['nico_mail']
    password = CONFIG['nico_password']


    event_loop = asyncio.get_event_loop()
    keypress_convert = keypresser.keypress_convert
    receiver = NicoliveCommentReceiver()
    receiver.login(email, password)


    while True:
        while True:
            lv = receiver.get_lv()
            if lv is not None: break
            print("放送URLに接続失敗、15秒後に再接続します。")
            time.sleep(15)
        print("放送URLに接続、コメント取得を開始します。")
        event_loop.run_until_complete(receiver.get_comment(lv,KEYDICT))
        
        