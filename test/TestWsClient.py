import websocket
import json
def on_message(ws, message):
    print("Received message:", message)

def on_error(ws, error):
    print("Error:", error)

def on_close(ws):
    print("Connection closed")

def on_open(ws):
    print("Connection opened")

    # 发送订阅消息给服务器
    subscription_message = {
        "op": "subscribe",
        "topic": "/client_count"
    }
    ws.send(json.dumps(subscription_message))

if __name__ == "__main__":
    # WebSocket服务器的URL
    ws_url = "ws://10.148.193.247:9090"

    # 创建WebSocket连接
    ws = websocket.WebSocketApp(ws_url,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)

    ws.on_open = on_open

    # 启动WebSocket客户端
    ws.run_forever()