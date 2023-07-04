"""This file run test api get and post."""
"""
File: run.py 
Version: 0.1
Updated: 2023-07
Author: Tang
"""


import json
from pydantic import BaseModel
import os
import uvicorn
from fastapi import FastAPI, Depends, status, Request, Response, HTTPException
app = FastAPI()

from fastapi.responses import HTMLResponse

class LastError(BaseModel):
    code: int
    message: str

LastError = LastError(code=0, message="")

def generate_html_response():
    html_content = """
    <html>
        <head>
            <title>Some HTML in here</title>
        </head>
        <body>
            <h1>Look ma! HTML!</h1>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

# 1. 定义请求和响应模型
# 使用Pydantic模型定义请求和响应的JSON schema:


# 请求通用模型
class ItemRequest(BaseModel):
    code: int
    data: dict


# 请求用户执行命令
class ItemRequestUserCommand(BaseModel):
    code: int       # 命令码
    command: str    # 命令
    data: dict      # 数据


# 请求用户登录模型
class ItemRequestUserInput(BaseModel):
    username: str
    password: str


# 响应模型
class ItemResponse(BaseModel):
    status: bool
    code: int
    message: str
    data: dict


# 响应模型返回的数据格式
class ItemResponseResult(BaseModel):
    status: bool
    code: int
    message: str
    data: dict


# 2. 定义服务类
# 使用类记录相关信息和提供方法:


# 服务通用模板
class ItemModelServic:
    ip = "192.168.1.10"  # 设备ip地址
    port = 8880  # 设备端口号
    username = "admin"  # 设备用户名
    password = "dc123456"  # 设备密码

    # 事件信息返回结构体
    EventInfo = {
        "command": 0,  # 事件码，0-无事件
        "type": 0,  # 事件类型，0-无事件，1-人形检测，2-人形跟踪，3-人形识别，4-人形追踪识别
        "message": "",  # 事件信息
        "other": ""  # 其他信息
    }

    # 报警信息事件结构体
    AlarmInfo = {
        "command": 0,  # 报警码，0-无报警
        "type": 0,  # 报警类型，0-无报警，1-温度报警，2-人形报警，3-人形识别报警
        "message": "",  # 报警信息
        "other": ""  # 其他信息
    }

    def init(self, ip: str, port: int, username: str, password: str) -> None:
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password


# 海康威视，微影摄像头服务模块
class VisionService(ItemModelServic):
    lUserId = -1  # 登录设备返回的用户ID
    lChannel = 1  # 视频通道号，可见光1，热成像2
    LastError = -1  # 错误码

    # 定义VisionPose模型表示p、t和z参数
    class VisionPose(BaseModel):
        wAction: int  # 1-定位PTZ参数，2-定位P参数，3-定位T参数，4-定位Z参数，5-定位PT参数
        wPanPos: int  # 云台水平方向控制，范围0-3600
        wTiltPos: int  # 云台垂直方向控制，范围-900-900
        wZoomPos: int  # 云台变倍控制，范围10-320
    pose = VisionPose(wAction=1, wPanPos=0, wTiltPos=0, wZoomPos=10)

    #  获取摄像头云台位置信息
    def pose_get(self):
        return self.pose

    #  设置摄像头云台位置信息
    def pose_set(self, id: str, lChannel: int, wAction: int, wPanPos: int, wTiltPos: int, wZoomPos: int) -> bool:
        self.lUserId = id
        self.lChannel = lChannel
        self.pose.wAction = wAction
        self.pose.wPanPos = wPanPos
        self.pose.wTiltPos = wTiltPos
        self.pose.wZoomPos = wZoomPos
        return True

    #  摄像头云台调用预置点操作
    def pose_preset(self, id: str, lChannel: int, dwPTZPresetCmd: int = 39, dwPresetIndex: int = 1) -> bool:
        self.lUserId = id
        self.lChannel = lChannel
        self.dwPTZPresetCmd = dwPTZPresetCmd
        self.dwPresetIndex = dwPresetIndex
        return True

GVisionService = VisionService()


# 松灵机器人服务模块
class RobotService(ItemModelServic):
    LastError = -1
    Authorization = "dc123456"  # 登录设备返回的用户ID


    # 定义RobotTask模型表示任务点列表
    class RobotTask(BaseModel):
        taskName: str   # 任务名称
        gridItemIdx: int  # web前端显示所需要的索引
        points: list    # 任务点列表，详细参考下面的任务点参数表
        mode: str       # 任务模式， "point":多点导航 "path":路径导航
        evadible: int   # 避障模式，1避障，2停障
        mapName: str    # 地图名称
        speed: int      # 导航时的速度参数0.1-1.5M/S
        editedName: str  # 任务需要重命名的名称
        remark: str     # 备注信息
        personName: str  # 任务创建人


    # 定义RobotPoints模型表示任务点列表
    class RobotPoints(BaseModel):
        position: object  # 任务点位置
        pointType: int      # 任务点类型，0-普通点，1-充电点，2-充电点，3-充电点
        actions: list       # 子任务点动作列表，目前只支持一个动作，第一个动作
        pointName: str    # 任务点名称
        index: int        # 任务点索引
        isNew: bool       # 是否是新建的任务点
        cpx: float        # 任务点位置x坐标
        cpy: float        # 任务点位置y坐标


    # 定义RobotPose模型表示x、y坐标和θ朝向
    class RobotPose(BaseModel):
        x: float        # 任务点位置x坐标
        y: float        # 任务点位置y坐标
        theta: float    # 任务点朝向X角度
    
    
    # 定义RobotAction模型表示任务点动作列表
    class RobotAction(BaseModel):
        actionContent: str  # 执行动作时长，秒数
        actionType: str     # 动作类型，可填值"rotation":选择 "stop":停止
        actionName: str     # 动作名称
        actionOrder: int    # 执行动作顺序号，0为最优先处理

    pose = RobotPose(x=0, y=0, theta=0)
    action = RobotAction(actionContent="", actionType="",
                         actionName="", actionOrder=0)
    points = RobotPoints(position=pose, pointType=0, actions=[
                         action], pointName="", index=0, isNew=False, cpx=0, cpy=0)
    task = RobotTask(taskName="", gridItemIdx=0, points=[
                     points], mode="", evadible=1, mapName="", speed=0, editedName="", remark="", personName="")

    # 定义RobotRealtimeTask模型表示实时任务
    class RobotRealtimeTask(BaseModel):
        loopTime: int  # 循环次数
        points: list   # 任务点列表，详细参考下面的任务点参数表
        mode: str      # 任务模式， "point":多点导航 "path":路径导航

    # 定义RobotPoint模型表示任务点列表
    class RobotPoint(BaseModel):
        position: object  # 任务点位置
        isNew: bool       # 是否是新建的任务点
        cpx: float        # 任务点位置x坐标
        cpy: float        # 任务点位置y坐标
    point = RobotPoint(position=pose, isNew=False, cpx=0, cpy=0)
    realtime_task = RobotRealtimeTask(loopTime=0, points=[point], mode="")

    # 获取机器人配置参数等的信息
    def config_get(self):
        config = {"battery": 100, "speed": 0.5, "mode": 0, "map": "map1"}
        return config
    #  获取机器人位置信息
    def pose_get(self):
        return self.pose
    # 设置机器人位置信息

    def pose_set(self, x: float, y: float, theta: float) -> bool:
        self.pose.x = x
        self.pose.y = y
        self.pose.theta = theta
        print(self.pose)
        return True

    # 获取机器人任务点信息


GRobotService = RobotService()

# 3. 定义路由函数
# 路由函数调用服务方法,并返回响应模型:
Authorization = "dc123456"

# 定义初始界面，显示说明文档内容
@app.get("/")
async def root():
    with open("api.html",encoding='utf-8') as f:
        return HTMLResponse(content=f.read(), status_code=200)

@app.post("/user/login")
async def user_login(user: ItemRequestUserInput):
    if user.username == "admin":
        if user.password == "dc123456":
            return ItemResponseResult(status=True, code=0, message="Login success", data={"token": Authorization})
        else:
            return ItemResponseResult(status=False, code=1, message="Password error", data={})
    else:
        return ItemResponseResult(status=False, code=1, message="Username error", data={})


@app.get("/user/vision/pose")
async def get_vision_pose():
    return ItemResponseResult(status=True, code=0, message="Get vision pose success", data={"pose": GVisionService.pose_get()})


@app.post("/user/vision/pose")
async def set_vision_pose(pose: GVisionService.VisionPose):
    GVisionService.pose_set(pose.wAction, pose.wPanPos,
                            pose.wTiltPos, pose.wZoomPos)
    return ItemResponseResult(status=True, code=0, message="Set vision pose success", data={})


# 获取机器人参数配置等的信息
@app.get("/user/robot/config")
async def get_robot_config():
    return ItemResponseResult(status=True, code=0, message="Get robot config success", data={"config": GRobotService.config_get()})

@app.get("/user/robot/pose")
async def get_robot_pose():
    return ItemResponseResult(status=True, code=0, message="Get robot pose success", data={"pose": GRobotService.pose_get()})


@app.post("/user/robot/pose")
async def set_robot_pose(pose: GRobotService.RobotPose):
    GRobotService.pose_set(pose.x, pose.y, pose.theta)
    return ItemResponseResult(status=True, code=0, message="Set robot pose success.", data={"pose": GRobotService.pose})

# 获取地图任务路径信息
@app.get("/user/robot/task")
async def get_robot_task():
    return ItemResponseResult(status=True, code=0, message="Get robot task success", data={"task": GRobotService.task})

# 设置地图任务路径信息
@app.post("/user/robot/task")
async def set_robot_task(task: GRobotService.RobotTask):
    GRobotService.task_set(task)
    return ItemResponseResult(status=True, code=0, message="Set robot task success", data={"task": GRobotService.task})
# 执行用户发送的指令code，数据格式为json
@app.post("/user/beta")
async def user_beta(request: ItemRequest):
    if request.code == 0:
        return ItemResponseResult(status=True, code=0, message="Success", data={})
    else:
        return ItemResponseResult(status=False, code=1, message="Error", data={})

# 执行用户发送的命令，数据格式为json


@app.post("/user/command")
async def user_command(command: ItemRequestUserCommand):
    if command.command == "start":
        return ItemResponseResult(status=True, code=0, message="Success", data={})
    elif command.command == "stop":
        return ItemResponseResult(status=True, code=0, message="Success", data={})
    elif command.command == "pause":
        return ItemResponseResult(status=True, code=0, message="Success", data={})
    elif command.command == "resume":
        return ItemResponseResult(status=True, code=0, message="Success", data={})
    elif command.command == "cancel":
        return ItemResponseResult(status=True, code=0, message="Success", data={})
    elif command.command == "reboot":
        return ItemResponseResult(status=True, code=0, message="Success", data={})
    elif command.command == "shutdown":
        return ItemResponseResult(status=True, code=0, message="Success", data={})
    else:
        return ItemResponseResult(status=False, code=1, message="Error", data={})
# 4. 使用依赖注入通 删官道的服务类
# 使用Depends(),让FastAPI自动注入依赖:


# @app.get("/items/{id}")
# def read_item(id: int, item_service: ItemService = Depends()):
#     pass

# 5. 返回正确的响应模型
# 服务方法应当始终返回响应模型,让FastAPI自动序列化为JSON:


# def get_by_id(self, id):
#     item = 1  # 获取对应ID项
#     return ItemResponse(**item)

from datetime import datetime, timedelta
from typing import Union

from fastapi import Depends, FastAPI, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# Union与 Optional 的区别是:
# - Union[X, None] 表示参数可以传 类型X 或 None。
# - Optional[X] 只表示参数可以传 类型X 或省略,但解析时的值还是 类型X 。
# 用户管理模块，用户认证吗，权限管理
# to get a string like this run in git bash:
# openssl rand -hex 32
# e5d05487248b25c0c95b1d36598a202b3b4bda99d555d31aefc3dddcfb1ad7e6
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30
ACCESS_TOKEN_EXPIRE_HOURS = 24

class UserManage:
    
    class UserInput(BaseModel):
        username: str
        password: str


    users_db = {
        "johndoe": {
            "username": "johndoe",
            "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
            "disabled": False,
        },
        "admin": {
            "username": "admin",
            "hashed_password": "$2b$12$OjIKA8m6ATXNZCbkljUYz.v3nwF/zuKOTj5twpoOv2uX6a.NAF6Bu",
            "disabled": False,
        }
    }

    # 用户名验证
    def username_verify(self, username: str)->bool:
        if username in self.users_db:
            return True
        else:
            LastError.code = 1
            LastError.message = "用户名不存在"
            return False
    # 用户密码验证
    def password_verify(self, username: str, password: str)->str:
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        # pwd_context.hash("dc123456")
        user = self.users_db.get(username)
        if user:
            self.user_current_id = user.get("username")
            if pwd_context.verify(password, user.get("hashed_password")):
                return self._create_access_token()
            else:
                LastError.code = 1
                LastError.message = "密码错误"
                return False
        return False

    # 生成token
    def _create_access_token(self)->bool:  
        to_encode = {"sub": self.user_current_id} 
        expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
        to_encode.update({"exp": expire})    
        self.user_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  
        return True 

    # 验证token
    def get_current_user(self, token: str):
        credentials_exception = HTTPException(status_code=400, detail="Incorrect token")
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])    
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception
        return username

GUserManage = UserManage()


# 用户登录获取token
@app.post("/login")
async def login_for_access_token(user: UserManage.UserInput):
    if not GUserManage.username_verify(user.username):
        raise HTTPException(status_code=400, detail="Incorrect username")
    if not GUserManage.password_verify(user.username, user.password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    return ItemResponseResult(status=True, code=0, message="Login Success", data={"token": GUserManage.user_token})



# 获取登录用户信息
@app.get("/login/me")
async def read_users_me(token:str = Header("token")):
    username = GUserManage.get_current_user(token)
    if username:
        return {"username": username}
    else:
        raise HTTPException(status_code=400, detail="Incorrect token")


if __name__ == "__main__":
    uvicorn.run("run:app", reload=True, port=8000, host="0.0.0.0")
