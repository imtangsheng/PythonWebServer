import websockets
import asyncio  
import json  
import time 
import random

class WebSocketClient:
    def __init__(self, ws_url, client_id):
        self.ws_url = ws_url
        self.websocket = None
        self.client_id = client_id
        self.connected = False
        self.heartbeat_timer = None

    async def connect(self):
        self.websocket = await websockets.connect(self.ws_url, timeout=10)
        self.connected = True
        

    async def send_data(self, data):
        if self.connected is True:
            await self.websocket.send(json.dumps(data))
            if(data["op"] !="ping"):
                print(f"Data sent: {data}")

    async def receive_data(self):
        while True:
            try:
                response = await self.websocket.recv()
                print(self.client_id)
                print(f"Received data: {response}")
                # 在这里处理接收到的数据
            except websockets.exceptions.ConnectionClosedError:
                print("Connection closed error, reconnecting...")
                await self.reconnect()
    
    async def reconnect(self):
       
        await self.disconnect()
        # await self.connect()
        # await self.send_initial_messages()
        await subscribe_data(self)
        

    async def disconnect(self):
        if self.websocket and self.websocket.open:
            await self.websocket.close()
            self.connected = False

    async def send_heartbeat(self):
        while self.websocket and self.websocket.open:
            message = {
                "op": "ping",
                "id": self.client_id,
                "timeStamp": str(time.time()*1000).split(".")[0]
            }
            # print("发送心跳了", index)
            await self.send_data(message)
            
            await asyncio.sleep(5)  # 每隔5秒发送一次心跳数据

    async def start_heartbeat_timer(self):
        self.heartbeat_timer = asyncio.get_event_loop().call_later(20,  self.switch_client_id)  # 5分钟后切换id
        

    async def switch_client_id(self):
        self.client_id = str(random.randint(1, 1000))  # 生成一个新的id
        print(f"Switched to new client id: {self.client_id}")
        await self.reconnect()

    
    async def send_initial_messages(self):
        # await self.send_data({
        #     "op": "subscribe",
        #     "topic": "/uptime"
        # })

        # await self.send_data({
        #     "op": "subscribe",
        #     "topic": "/slam_status"
        # })
      
        # await self.send_data({
        #     "op": "subscribe",
        #     "topic": "/charge_data"
        # })

        await self.send_data({   
            "op": "subscribe",
            "topic": "/run_management/task_progress",
            "type":"std_msgs/Float64" 
        })

        await self.send_data({   
            "op": "subscribe",
            "topic": "/run_management/global_status",
            "type":"support_ros/GlobalStatus" 
        })


async def subscribe_data(client):
    try:
        await client.connect()
        await client.send_initial_messages()
        await client.send_heartbeat()
        # await client.w3eq()

        time.sleep(1)
    except asyncio.CancelledError:
        print("===================", asyncio.CancelledError)



async def total_func():
    ws_urls = ["ws://10.148.193.247:9090"] * 1  # 生成包含100个WebSocket服务器URL的列表
    clients = [WebSocketClient(url, str(random.randint(1, 10000))) for url in ws_urls]  # 创建100个WebSocketClient实例，每个实例分配一个随机id
    tasks = [subscribe_data(client) for client in clients]  # 创建订阅任务列表

    # loop = asyncio.get_event_loop()
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(total_func())
