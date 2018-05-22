
//youtubeliveチャットページのajaxを傍受してlocalhostのWebSocketに流す
//元ネタ https://stackoverflow.com/questions/26481212/capture-ajax-response-with-selenium-and-python/26917962#26917962
//日本語 https://qiita.com/non0/items/7f24bc1f308be9e10c21
//       https://qiita.com/non0/items/2e7a7fdce4b16278f290

//jsはさっぱりだがonReadyStateChangeの中だけフィーリングで改変

(function (XHR) {
    "use strict";

    //確認用 チャットページ最上部に表示
    //var element = document.createElement('div');
    //element.id = "interceptedResponse";
    //element.appendChild(document.createTextNode(""));
    //document.body.insertBefore(element, document.body.firstChild);

    var open = XHR.prototype.open;
    var send = XHR.prototype.send;
    //ポート8089に深い意味はない サンプル通り
    var socket = new WebSocket("ws://localhost:8089");

    XHR.prototype.open = function (method, url, async, user, pass) {
        this._url = url; // want to track the url requested
        open.call(this, method, url, async, user, pass);
    };

    XHR.prototype.send = function (data) {
        var self = this;
        var oldOnReadyStateChange;
        var url = this._url;

        function onReadyStateChange() {
            if (self.status === 200 && self.readyState === 4) {
                try {
                    var json = JSON.parse(self.responseText);

                    var actions = json.response.continuationContents.liveChatContinuation.actions;
                    var comments = actions.map(function (value) {
                        return value.addChatItemAction.item.liveChatTextMessageRenderer.message.runs;
                    });

                    //送信jsonのイメージ 辞書の配列の配列
                    //[
                    //	[{ "text": "あああ" }],                    1件目
                    //	[{ "text": "いいい" }, { "text": "!!!" }], 2件目 英数字等があると? 分割されるが合わせて1つのコメント
                    //]
                    socket.send(JSON.stringify(comments));
                    }
                catch {}
                //確認用 チャットページ最上部に表示
                //document.getElementById("interceptedResponse").innerHTML = JSON.stringify(comments);
            }
            if (oldOnReadyStateChange) {
                oldOnReadyStateChange();
            }
        }

        if (this.addEventListener) {
            this.addEventListener("readystatechange", onReadyStateChange, false);
        } else {
            oldOnReadyStateChange = this.onreadystatechange;
            this.onreadystatechange = onReadyStateChange;
        }

        send.call(this, data);
    };

})(XMLHttpRequest);
