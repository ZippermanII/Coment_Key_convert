window.onload = function () {
    var WebSocketServer = require('ws').Server
    var wss = new WebSocketServer({
        host: 'localhost',
        port: 8091
    });
    wss.on('connection', function (ws) {
        ws.on('message', function (message) {
            console.log('received: %s', message);
            ws.send(message);
        });
    });
    //var ws = new WebSocket('ws://localhost:8089');
    //console.log("#####################################################")
    //// 接続を開く
    //ws.addEventListener('open', function (event) {
    //    console.log('111111111111111111111111111111111111111111111111');
    //});
    //ws.addEventListener('message', function (event) {
    //    // サーバーからメッセージを受け取ったときに実行される
    //    console.log('22222222222222222222222222222222222222222222222');
    //});
    //ws.addEventListener('close', function (event) {
    //    console.log('33333333333333333333333333333333333333333333333');
    //});
    let nico = new nicoJS({
        app: document.getElementById('app'),
        width: 600,
        height: 400,
        font_size: 50,     // opt
        color: '#fff'  // opt
    })
    document.getElementById('btn').onclick = function () {
        var text = document.getElementById('comment').value;
        nico.send(text);
        nico.send(text, '#ff0000'); // 色変更
    }
    nico.loop(['88888', 'かわいい', 'なんだこれw']);
    $(function () {
        var your_generated_table = $('table'),
            dynamic_data = JSON.parse(your_generated_table.attr('data-dynamic'));
    });
}