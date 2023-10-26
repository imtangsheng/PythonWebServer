"""This file run test api get and post."""
"""
File: run.py 
Version: 0.1
Updated: 2023-07
Author: Tang
"""

from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Union, Optional, List, Dict
import json
from pydantic import BaseModel, Field, confloat, validator
import os
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, status, Request, Response, HTTPException, Header, Body

app_description = """
# 机器人后端API说明

目前支持HTTP协议，WS 接口未开发。

注:无说明，则GET方法返回的数据即是POST修改提交的数据格式也是一样的。

## 2023-10-19 更新说明
    1.增加指针算法模块
    2.更新云台设置ptz的pose接口参数

## 2023-07-15 更新说明
    1.配置文件格式修改，增加了一个配置文件，config/config.json
    2.支持保存修改的配置：用户模块，视觉模块，机器人模块，日志配置的配置更新

## 2023-07-12 更新说明
    1.请求接口数据统一格式，{方法：数据}，参考示例
    2.所有模块的配置方法，增加删除更新的方法
    
## 2023-07-11 更新说明
    1.云台的控制接口增加了一个参数，接收控制云台的指令
    2.每个模块分别增加了一个请求方法以获取配置信息
    3.用户模块的配置添加删除更新方法
    
## 2023-07-7 更新说明
    1.更新了通用响应模型返回的数据格式
    2.增加了新的请求方法，机器人任务的增加，删除方法
    3.增加了一个接口，用于获取机器人的状态信息
    4.增加了一个接口，用于传感器信息
 
"""


class CustomFastAPI(FastAPI):
    def __init__(self, *args, **kwargs):
        self.models_to_show = kwargs.pop("models_to_show", [])
        super().__init__(*args, **kwargs)

    def openapi(self):
        openapi_schema = super().openapi()
        if self.models_to_show:
            all_models = openapi_schema["components"]["schemas"]
            openapi_schema["components"]["schemas"] = {
                model_name: model_info
                for model_name, model_info in all_models.items()
                if model_name in [model.__name__ for model in self.models_to_show]
            }
        return openapi_schema


app = CustomFastAPI()

# app = FastAPI()

app.title = '机器人后端API说明'
app.description = app_description
app.version = "0.2"
# app.openapi(exclude_schemas=True)
# app.openapi_tags = []
# from fastapi.openapi.utils import get_openapi

"""## 数据库使用说明
- 数据库使用json文件，格式如下：
    config = {"db":{"type":"json","path":"config/config.json"},"log":{"level":"info","path":"./test.log"}}
- 数据库文件路径：config/config.json
- 数据库文件格式：json
- 数据库文件内容说明：
    - UserDB: 用户数据库
        - 用户配置信息: 用户名，密码，用户组，是否禁用，权限列表
- 数据库文件内容示例：
"""


class JsonDB:
    def __init__(self, db_path: str = "config/db.json"):
        self.db_path = db_path

    def load(self, file_path: str = None):
        if file_path is not None:
            self.db_path = file_path
        with open(self.db_path, encoding='utf-8', mode='r') as f:
            data = json.load(f, encoding="utf-8")
        return data

    def save(self, data: dict, file_path: str = None):
        if file_path is None:
            file_path = self.db_path
        with open(file_path, mode='w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)


ConfigAPP_path = "config/config.json"
ConfigAPP = json.load(open(ConfigAPP_path, encoding='utf-8', mode='r'))
if ConfigAPP["db"]["type"] == "json":
    APP_JsonDB = JsonDB(ConfigAPP["db"]["path"])
    print(ConfigAPP["db"]["path"])
    APP_DB = APP_JsonDB.load()

elif ConfigAPP["db"]["type"] == "sqlite":
    import sqlite3
    # APP_DB = sqlite3.connect(ConfigAPP["db"]["path"])
else:
    raise ValueError("db type error")

"""# 通用响应模型返回的数据格式
"""


# @exclude
class LastErrorBase(BaseModel):
    """## 返回最后操作的错误码和错误信息
    - 参数
        - **ERROR_TYPE**: str,错误类型
        - **code**: int,错误值
        - **message**: str,错误信息
    """
    ERROR_TYPE: str = ""
    code: int = 0
    message: str = "没有错误"


LastError = LastErrorBase()


class ResponseReturn(BaseModel):
    """## 通用响应模型返回的数据格式
    - 参数
        - **status**: bool,请求状态 True 成功  False 失败
        - **code**: int,状态码 0 成功  -1 失败
        - **message**: str,消息
        - **data**: [str,dict数据],返回的数据，也是对应POST的数据
    """
    status: bool = False
    code: Union[int, str] = -1
    message: str = ""
    data: Union[Dict, LastErrorBase] = LastErrorBase()


class ResponseModel(BaseModel):
    """## 通用响应模型返回的数据格式
    - 参数
        - **status**: bool,请求状态 True 成功  False 失败
        - **code**: str,请求的类型代码，为对应的请求路由
        - **message**: str,消息
        - **data**: [str,dict数据],返回的数据，也是对应POST的数据
    """
    status: bool = False
    code: str = ""
    message: str = ""
    data: Union[Dict, LastErrorBase] = LastErrorBase()


# ResponseReturn = ResponseReturn()

class CommandBase(BaseModel):
    """## 发送指令、命令格式模型
    - 参数
        - **name**: str,命令名称
        - **description**: str,命令描述
        - **code**: str,命令代码
        - **data**: dict,命令参数
    """
    name: str = "command"
    description: str = "命令描述"
    code: str = "command code"
    data: dict = {}


"""END
# 通用响应模型返回的数据格式
"""

"""# UserManage 用户管理模块
"""
"""# 用户管理模块，用户认证吗，权限管理
"""


class UserInput(BaseModel):
    """## 用户输入模型
        - **username**: str,用户名
        - **password**: str,密码
    """
    username: str = "admin"  # 用户名
    password: str = "abcd1234"  # 密码


# to get a string like this run in git bash:
# openssl rand -hex 32
# e5d05487248b25c0c95b1d36598a202b3b4bda99d555d31aefc3dddcfb1ad7e6
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30
ACCESS_TOKEN_EXPIRE_HOURS = 24
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class UserSetting(BaseModel):
    """## 用户配置模型结构体
    - **name**: str,用户名
    - **group**: str,用户组
    - **disabled**: bool,是否禁用
    - **permissions**: list,权限列表
    """
    name: str = "admin"
    group: str = "administator"
    disabled: bool = False
    permissions: List[str] = ["administator"]


class UserManage:
    """#  用户管理模块，用户认证吗，权限管理
    """
    # 密码加密
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    # pwd_context.hash("dc123456")
    # pwd_context.verify(password, hashed_password)):
    user_current_id = ""  # 当前用户ID
    user_token = ""  # 当前用户token
    users_db = APP_DB["UsersDB"]  # 用户数据库
    user_setting = {}  # 用户配置
    for user in users_db:
        user_setting[user] = UserSetting(**users_db[user])

    def get_user_setting(self) -> bool:
        # 获取用户配置
        self.user_setting = {}  # 用户配置
        self.users_db = APP_DB["UsersDB"]
        for user in self.users_db:
            self.user_setting[user] = UserSetting(**self.users_db[user])
        return True

    def set_user_setting(self, setting: dict) -> bool:
        # 设置用户配置
        self.user_setting = {}  # 用户配置
        for user in self.users_db:
            self.user_setting[user] = UserSetting(**self.users_db[user])
        # 保存修改
        APP_JsonDB.save(APP_DB)
        return True

    def update_user_setting(self, setting: dict) -> bool:
        # 更新用户配置
        username = setting['name']
        if username == "admin" or username not in self.users_db.keys():
            return False
        print("group")
        for key in setting.keys():
            if key in self.users_db[username].keys():
                self.users_db[username][key] = setting[key]

        if self.get_user_setting():
            # 保存修改
            APP_JsonDB.save(APP_DB)
            return True
        return False

    def add_user_setting(self, setting: dict) -> bool:
        # 添加用户配置
        username = setting['name']
        if username == "admin" or username in self.users_db.keys():
            return False
        self.users_db[username] = setting
        if self.get_user_setting():
            # 保存修改
            APP_JsonDB.save(APP_DB)
            return True
        return False

    def del_user_setting(self, username: str) -> bool:
        # 删除用户配置
        if username == "admin" or username not in self.users_db.keys():
            return False
        self.users_db.pop(username)
        if self.get_user_setting():
            # 保存修改
            APP_JsonDB.save(APP_DB)
            return True
        return False

    def username_verify(self, username: str) -> bool:
        """# 用户名验证
        - **username**: str,用户名
        # 返回值:用户名存在返回True,否则返回False
        """
        if username in self.users_db:
            self.user_current_id = username
            return True
        return False

    def password_verify(self, password: str) -> bool:
        """# 用户密码验证
        - **password**: str,密码
        # 返回值:密码正确返回True,否则返回False
        """
        if self.password_hash_check(password, self.users_db[self.user_current_id].get("hashed_password")):
            return True
        return False

    def check_permissions(self, permissions: str, token: str = Header("token")):
        """# 用户权限验证
        - **permissions**: str,权限
        # 返回值:权限正确返回True,否则返回False
        """

        def check_authorization(func):
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
                if permissions in self.users_db[self.user_current_id].get("permissions"):
                    return func(*args, **kwargs)
                return False

            return wrapper

        return check_authorization

    def password_hash(self, password: str) -> str:
        # 用户密码哈希值加密
        return self.pwd_context.hash(password)

    def password_hash_check(self, password: str, hashed_password: str) -> bool:
        # 用户密码哈希值验证
        if self.pwd_context.verify(password, hashed_password):
            return True
        else:
            return False

    def token_get(self, user_id: str) -> str:
        # 生成token
        to_encode = {"sub": self.user_current_id}
        expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
        expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
        to_encode.update({"exp": expire})
        user_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return user_token

    def get_current_username(self, token: str) -> Union[str, None]:
        # 验证token
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                LastError.ERROR_TYPE = "TOKEN_ERROR"
                LastError.code = 2
                LastError.message = "Token 验证用户不存在:username is None"
                return None
            return username
        except JWTError:
            LastError.ERROR_TYPE = "TOKEN_ERROR"
            LastError.code = 2
            LastError.message = "Token 验证错误：JWTError"
            return None


GUserManage = UserManage()

"""END
用户管理模块UserManage
"""

"""
用户管理模块 请求路径与方法
"""


@app.post("/login", summary="用户登录，返回token值", tags=["用户管理"], include_in_schema=False)
async def user_login(user: UserInput) -> ResponseReturn:
    """## 用户登录，返回token值
    - Parameters:
        - **username**: string, 用户名
        - **password**: string, 密码
    - example:
        - {"username": "admin", "password": "dc123456"}
    ## 返回值:
    - response:
        - {"token":string(token值)}
    """
    LastError = LastErrorBase()
    if not GUserManage.username_verify(user.username):
        LastError.ERROR_TYPE = "USER_LOGIN_ERROR"
        LastError.code = 1
        LastError.message = "用户名不存在"
        return ResponseReturn(status=False, code=-1, message=LastError.message, data=LastError)
    if not GUserManage.password_verify(user.password):
        LastError.ERROR_TYPE = "USER_LOGIN_ERROR"
        LastError.code = 1
        LastError.message = "用户密码错误"
        return ResponseReturn(status=False, code=-1, message=LastError.message, data=LastError)
    return ResponseReturn(status=True, code=0, message="用户登录:" + user.username,
                          data={"token": GUserManage.token_get(user.username)})


@app.get("/login/me", summary="获取当前登录用户的信息", tags=["用户管理"])
async def user_read_me(token: str = Header("token")) -> ResponseReturn:
    """## 返回当前登录用户的信息
    - Parameters:
        - 无
    ## 返回值:
    - response:
        - {"username":username}
    """
    global LastError
    LastError = LastErrorBase()
    if token is None:
        LastError.ERROR_TYPE = "TOKEN_ERROR"
        LastError.code = 2
        LastError.message = "Token 验证错误：token is None"
        return ResponseReturn(status=False, code=-1, message=LastError.message, data=LastError)
    username = GUserManage.get_current_username('token')
    if username is None:
        return ResponseReturn(status=False, code=-1, message=LastError.message, data=LastError)
    return ResponseReturn(status=True, code=0, message="获取当前登录用户的信息", data={"username": username})


@app.post("/user/login", summary="用户登录，返回token值", tags=["用户管理"], response_model_exclude={BaseModel})
async def user_login_2(user: UserInput) -> ResponseReturn:
    """## 用户登录，返回token值
    - Parameters:
        - **username**: string, 用户名
        - **password**: string, 密码
    - example:
        - {"username": "admin", "password": "dc123456"}
    # 返回值:
    - response:
        - {"token":string(token值)}
    """
    LastError = LastErrorBase()
    if not GUserManage.username_verify(user.username):
        LastError.ERROR_TYPE = "USER_LOGIN_ERROR"
        LastError.code = 1
        LastError.message = "用户名不存在"
        return ResponseReturn(status=False, code=-1, message=LastError.message, data=LastError)
    if not GUserManage.password_verify(user.password):
        LastError.ERROR_TYPE = "USER_LOGIN_ERROR"
        LastError.code = 1
        LastError.message = "用户密码错误"
        return ResponseReturn(status=False, code=-1, message=LastError.message, data=LastError)
    return ResponseReturn(status=True, code=0, message="用户登录:" + user.username,
                          data={"token": GUserManage.token_get(user.username)})


@app.get("/user/config", summary="获取用户配置信息", tags=["用户管理"])
async def user_get_config(token: str = Header("token")) -> ResponseReturn:
    """## 获取用户配置信息
    - Parameters:
        - 需要先验证登录（暂时不用验证）
    - response:
        - {"config":{"usrname":[UserSetting]}
    """
    global LastError
    LastError = LastErrorBase()
    # return ResponseReturn(status=True, code=0, message="获取当前登录用户的信息", data={"userSetting": GUserManage.user_setting})
    # username = GUserManage.get_current_username('token')
    username = "admin"
    if username is None:
        return ResponseReturn(status=False, code=-1, message=LastError.message, data=LastError)
    if GUserManage.get_user_setting():
        print(GUserManage.user_setting.keys())
        return ResponseReturn(status=True, code=0, message="获取当前登录用户的信息",
                              data={"config": GUserManage.user_setting})
    return ResponseReturn(status=False, code=-1, message=LastError.message, data=LastError)


@app.post("/user/config/update", summary="更新用户配置信息", tags=["用户管理"])
async def user_update_config(config: Dict = Body(), token: str = Header("token")) -> ResponseReturn:
    """## 更新用户配置信息
    - Parameters:
        - userSetting: Dict, 用户配置信息
                - **name**: str,用户名
                - **password**: str,密码
                - **group**: str,用户组
                - **disabled**: bool,是否禁用
                - **permissions**: list,权限列表
    - example:
        - {"name": "test", "password": "dc123456", "group": "admin", "disabled": False, "permissions": ["admin", "user"]}
    ## 返回值:
    - response:
        - {"config":[UserSetting]}
    """
    LastError = LastErrorBase()
    if config is None:
        LastError.ERROR_TYPE = "USER_CONFIG_UPDATE_ERROR"
        LastError.code = 1
        LastError.message = "输入为空"
        return ResponseReturn(status=False, code=-1, message=LastError.message, data=LastError)
    if config['name'] == "admin":
        LastError.ERROR_TYPE = "USER_CONFIG_UPDATE_ERROR"
        LastError.code = 1
        LastError.message = "输入的用户非法，不能修改"
        return ResponseReturn(status=False, code=-1, message=LastError.message, data=LastError)
    if GUserManage.update_user_setting(config):
        return ResponseReturn(status=True, code=0, message="用户配置更新成功",
                              data={"config": GUserManage.user_setting[config['name']]})
    return ResponseReturn(status=False, code=-1, message=LastError.message, data=LastError)


@app.post("/user/config/add", summary="添加用户配置信息", tags=["用户管理"])
async def user_add_config(config: Dict = Body(), token: str = Header("token")) -> ResponseReturn:
    """## 添加用户配置信息
    - Parameters:
        - userSetting: Dict, 用户配置信息
                - **name**: str,用户名
                - **password**: str,密码
                - **group**: str,用户组
                - **disabled**: bool,是否禁用
                - **permissions**: list,权限列表
    - example:
        - {"name": "test", "password": "dc123456", "group": "admin", "disabled": False, "permissions": ["admin", "user"]}
    ## 返回值:
    - response:
        - {"config":[UserSetting]}
    """
    global LastError
    LastError = LastErrorBase()
    if config is None or config['name'] == "admin":
        LastError.ERROR_TYPE = "USER_CONFIG_ADD_ERROR"
        LastError.code = 1
        LastError.message = "用户配置添加失败"
        return ResponseReturn(status=False, code=-1, message=LastError.message, data=LastError)
    if GUserManage.add_user_setting(config):
        return ResponseReturn(status=True, code=0, message="用户配置添加成功",
                              data={"config": GUserManage.user_setting[config['name']]})
    return ResponseReturn(status=False, code=-1, message=LastError.message, data=LastError)


@app.post("/user/config/del", summary="删除用户配置信息", tags=["用户管理"])
async def user_del_config(config: Dict = Body(), token: str = Header("token")) -> ResponseReturn:
    """## 删除用户配置信息
    - Parameters:
        - userSetting: Dict, 用户配置信息
                - **name**: str,用户名
    - example:
        - {"name": "test"}
    ## 返回值:
    - response:
        - {"config":{"usrname":[UserSetting]}
    """
    global LastError
    LastError = LastErrorBase()
    if config is None or config['name'] == "admin":
        LastError.ERROR_TYPE = "USER_CONFIG_DEL_ERROR"
        LastError.code = 1
        LastError.message = "用户配置删除失败"
        return ResponseReturn(status=False, code=-1, message=LastError.message, data=LastError)
    if GUserManage.del_user_setting(config['name']):
        return ResponseReturn(status=True, code=0, message="用户配置删除成功",
                              data={"config": GUserManage.user_setting})
    return ResponseReturn(status=False, code=-1, message=LastError.message, data=LastError)


"""END
用户管理模块 请求路径与方法
"""

"""# 视觉管理模块
"""


class VisionBase(BaseModel):
    """## VisionBase模型表示视觉参数
    - ip: string, IP地址
    - port: int, 端口号
    - username: string, 用户名
    - password: string, 密码
    """
    ip: str = "192.168.1.64"
    port: int = 8000
    username: str = "admin"
    password: str = "abcd1234"


class VisionPose(BaseModel):
    """## VisionPose模型表示p、t和z参数
    - **lChannel**: int, 通道号，1-可见光，2-热成像
    - **wAction**: int, 1-定位PTZ参数，2-定位P参数，3-定位T参数，4-定位Z参数，5-定位PT参数
    - **wPanPos**: int, 云台水平方向控制，范围0-3600
    - **wTiltPos**: int, 云台垂直方向控制，范围-900-900
    - **wZoomPos**: int, 云台变倍控制，范围10-320
    """
    lUserId: int = 0  # 云台登录id
    lChannel: int = 1  # 通道号，1-可见光，2-热成像
    wAction: int = 1  # 1-定位PTZ参数，2-定位P参数，3-定位T参数，4-定位Z参数，5-定位PT参数
    wPanPos: int = 0  # 云台水平方向控制，范围0-3600
    wTiltPos: int = 0  # 云台垂直方向控制，范围-900-900
    wZoomPos: int = 10  # 云台变倍控制，范围10-320


class VisionPreset(BaseModel):
    """# VisionPreset模型表示预置点
    - **lChannel**: int, 通道号，1-可见光，2-热成像
    - **dwPTZPresetCmd**: int = 39, 命令 GOTO_PRESET = 39 
    - **dwPresetIndex**: int = 1, 预置点索引，范围1-300
    """
    lChannel: int = 1  # 通道号，1-可见光，2-热成像
    dwPTZPresetCmd: int = 39  # 命令 GOTO_PRESET = 39
    dwPresetIndex: int = 1  # 预置点索引，范围1-300


class VisionEvent(BaseModel):
    # 定义事件信息返回结构
    command: int = 0  # 事件码，0-无事件
    code: int = 0  # 事件类型，0-无事件，1-人形检测，2-人形跟踪，3-人形识别，4-人形追踪识别
    message: str = ""  # 事件信息
    other: str = ""  # 其他信息


class VisionSetting(BaseModel):
    """## 定义配置信息结构体
    - 参数
        - **command**: List[CommandBase], 命令列表
            - **name**: str, 命令名称
            - **description**: str, 命令描述
            - **code**: str, 命令代码
            - **data**: Dict, 命令数据       
        - **file_path**: Dict, 文件保存信息字典
            - **video**: str, 视频文件保存路径
            - **image**: str, 图片文件保存路径
    """
    command: List[CommandBase] = []
    file_path: Dict = {}


GVisionSetting = APP_DB["VisionSetting"]


class VisionManage:
    """# 海康威视，微影摄像头服务模块
    """
    ip = "192.168.1.64"  # 设备ip地址
    port = 8000  # 设备端口号
    username = "admin"  # 设备用户名
    password = "dc123456"  # 设备密码

    lUserId = -1  # 登录设备返回的用户ID
    lChannel = 1  # 视频通道号，可见光1，热成像2
    LastErrorCode = -1  # 错误码
    pose = VisionPose()  # 云台位置信息
    event = VisionEvent()  # 事件信息
    setting: dict = VisionSetting(**GVisionSetting).dict()

    def __init__(self, base: VisionBase = VisionBase()):
        # 初始化设备信息
        self.ip = base.ip
        self.port = base.port
        self.username = base.username
        self.password = base.password

        # self.setting: dict = VisionSetting(**GVisionSetting).dict()

    def login(self, base: VisionBase = VisionBase()) -> bool:
        # 登录设备
        self.ip = base.ip
        self.port = base.port
        self.username = base.username
        self.password = base.password
        return True

    def get_config(self) -> bool:
        # 获取配置信息
        self.setting: dict = VisionSetting(**GVisionSetting).dict()
        return True

    def set_config(self, setting: dict) -> bool:
        # 设置配置信息
        GVisionSetting = setting
        if self.get_config():
            # 保存修改
            APP_JsonDB.save(APP_DB)
            return True
        return False

    def update_config(self, setting: dict) -> bool:
        # 更新配置信息
        for key in setting.keys():
            if key in GVisionSetting.keys():
                GVisionSetting[key] = setting[key]
        if self.get_config():
            # 保存修改
            APP_JsonDB.save(APP_DB)
            return True
        return False

    def get_pose(self, lChannel: int = 1) -> bool:
        #  获取摄像头云台位置信息
        self.pose.lChannel = lChannel
        return True

    def set_pose(self, pose: VisionPose) -> bool:
        #  设置摄像头云台位置信息
        self.pose = pose
        return True

    def preset(self, lChannel: int = 1, dwPTZPresetCmd: int = 39, dwPresetIndex: int = 1) -> bool:
        #  摄像头云台调用预置点操作
        self.lChannel = lChannel
        # self.dwPTZPresetCmd = dwPTZPresetCmd
        # self.dwPresetIndex = dwPresetIndex
        return True


GVisionManage = VisionManage()
"""END
视觉管理模块VisionManage
"""

"""
视觉管理模块 请求路径与方法
"""


@app.post("/user/vision/login", summary="登录摄像头", tags=["视觉管理"])
async def vision_login(base: VisionBase = Body(embed=True)) -> ResponseReturn:
    """## 登录摄像头
    - Parameters:
        - VisionBase 设备信息
            - ip: str ,  唯一标识,为ip地址
            - port: int = 8000, 设备端口号
            - username: str = "admin", 设备用户名
            - password: str = "dc123456", 设备密码
        - example:
            - {"base":{VisionBase}
    - 返回：
        - {'base':VisionBase} 登录信息 (暂时，返回密码时不安全的，后期修改为空)
        - {} 返回空
    """
    LastError = LastErrorBase()
    global GVisionManage
    GVisionManage = VisionManage(base)
    if GVisionManage.login():
        return ResponseReturn(status=True, code=0, message="Login success", data={'base': base})
    return ResponseReturn(status=False, code=LastError, message=LastError.message, data=LastError)


@app.get("/user/vision/config", summary="获取视觉模块的配置", tags=["视觉管理"])
async def vision_get_config(ip: str = Body("192.168.1.64")) -> ResponseReturn:
    """## 获取视觉模块的配置
    - 参数：
        - ip: str = "", 设备ip地址(非必须)
    - 示例：
        - {"ip":"192.168.1.64"} 
    - 返回：
        - {'config':VisionSetting} 配置信息
    """
    LastError = LastErrorBase()
    if GVisionManage.get_config():
        return ResponseReturn(status=True, code=0, message="Get vision config success",
                              data={'config': GVisionManage.setting})
    return ResponseReturn(status=False, code=LastError, message=LastError.message, data=LastError)


@app.post("/user/vision/config", summary="设置视觉模块的配置", tags=["视觉管理"], include_in_schema=False)
async def vision_set_config(config: dict = Body(), ip: str = Body("192.168.1.64")) -> ResponseReturn:
    """## 设置视觉模块的配置
    - 参数：
        - config: dict 配置信息
        - ip: str = "", 设备ip地址(非必须)
    - 示例：
        - {"config":VisionSetting,"ip":"192.168.1.64"}
    - 返回：
        - {'config':VisionSetting} 配置信息
    """
    LastError = LastErrorBase()
    if GVisionManage.set_config(config):
        return ResponseReturn(status=True, code=0, message="Set vision config success",
                              data={'config': GVisionManage.setting})
    return ResponseReturn(status=False, code=LastError, message=LastError.message, data=LastError)


@app.post("/user/vision/config/update", summary="更新视觉模块的配置", tags=["视觉管理"])
async def vision_update_config(config: dict = Body(), ip: str = Body("192.168.1.64")) -> ResponseReturn:
    """## 更新视觉模块的配置
    - 参数：
        - config: dict  配置信息(**更新传入的键值**，比如传入command或者file_path)
        - ip: str = "", 设备ip地址(非必须)
    - 示例：
        ```json    
        {"config": 
            {
                "command": 
                    [
                        {
                            "name": "可见光拍照",
                            "description": "可见光拍照",
                            "code": "capture",
                            "data": 
                                {
                                    "lChannel": 1,
                                    "sPicFileName": "%日期+可见光拍照.jpg"
                                }
                        }
                    ],
                "file_path": 
                    {
                        "video": "D:/DRobot/video/",
                        "image": "D:/DRobot/image/"
                    }
            },
        "ip":"192.168.1.64"
        }
    - 返回：
        - {'config':VisionSetting} 配置信息
    """
    LastError = LastErrorBase()
    if GVisionManage.update_config(config):
        return ResponseReturn(status=True, code=0, message="Update vision config success",
                              data={'config': GVisionManage.setting})
    return ResponseReturn(status=False, code=LastError, message=LastError.message, data=LastError)


@app.get("/user/vision/pose", summary="获取摄像头的PTZ坐标角度信息", tags=["视觉管理"])
async def vision_get_pose(pose: VisionPose = VisionPose(lUserId=0, lChannel=1), ip: str = Body(None)) -> ResponseReturn:
    """# 获取摄像头的PTZ坐标角度信息
    - 参数：
        - VisionPose 视觉信息
            - lChannel: int = 1, 通道号，1-可见光，2-热成像
            - 其他无效
    - 示例：
        - {'pose':VisionPose} 视觉信息
    """
    LastError = LastErrorBase()
    if not ip:
        ip = GVisionManage.ip
        print(ip)
    if GVisionManage.get_pose(pose.lChannel):
        return ResponseReturn(status=True, code=0, message="Get vision pose success1",
                              data={'pose': GVisionManage.pose, 'ip': ip})
    return ResponseReturn(status=False, code=-1, message=LastError.message, data=LastError)


@app.post("/user/vision/pose", summary="设置摄像头的PTZ坐标角度信息", tags=["视觉管理"])
async def vision_set_pose(pose: VisionPose) -> ResponseReturn:
    """# 设置摄像头的PTZ坐标角度信息
    - 参数：
        - VisionPose 视觉信息模型
            - lUserId: int = 0, 用户登录接口返回值,默认0
            - lChannel: int = 1, 通道号，1-可见光，2-热成像， 默认1
            - wAction: int =1, 1-定位PTZ参数，2-定位P参数，3-定位T参数，4-定位Z参数，5-定位PT参数
            - wPanPos: int  =0, 云台水平方向控制，范围0-3600
            - wTiltPos: int  =0, 云台垂直方向控制，范围-900-900
            - wZoomPos: int  =10, 云台变倍控制，范围10-320
    - 示例：
        - {'pose':VisionPose} 视觉信息
        - {"lUserId":0,"lChannel":1,"wAction": 1,"wPanPos":0,"wTiltPos":0,"wZoomPos":10}
    """
    LastError = LastErrorBase()
    if GVisionManage.set_pose(pose):
        return ResponseReturn(status=True, code="/user/vision/pose", message="Set vision pose success",
                              data={'pose': GVisionManage.pose})
    return ResponseReturn(status=False, code=-1, message=LastError.message, data=LastError)


@app.post("/user/vision/preset", summary="摄像头云台调用预置点操作", tags=["视觉管理"])
async def vision_preset(preset: VisionPreset) -> ResponseReturn:
    """# 摄像头云台调用预置点操作
    - 参数：
        - VisionPreset 视觉预置点模型
            - lChannel: int = 1, 通道号，1-可见光，2-热成像
            - dwPTZPresetCmd: int = 39, 预置点操作命令，39-调用预置点
            - dwPresetIndex: int = 1, 预置点索引，范围1-300,设置使用的预置点索引
    """
    LastError = LastErrorBase()
    if GVisionManage.preset(preset.lChannel, preset.dwPTZPresetCmd, preset.dwPresetIndex):
        return ResponseReturn(status=True, code=0, message="Set vision preset success")
    return ResponseReturn(status=False, code=-1, message=LastError.message, data=LastError)


"""END
视觉管理模块 请求路径与方法
"""

"""# 机器人相关模块
"""


# 模型不支持类中定义，需要定义为全局变量

class RobotBase(BaseModel):
    """# 定义RobotBase模型参数
    - 参数：
        - ip: str = "" , 机器人ip，唯一标识，为ip地址
        - port: int = 8000, 机器人端口号
        - username: str = "admin", 机器人用户名
        - password: str = "dc123456", 机器人密码
    """
    ip: str = "1"  # 机器人ip，唯一标识，为ip地址
    port: int = 8000  # 机器人端口号
    username: str = "admin"  # 机器人用户名
    password: str = "dc123456"  # 机器人密码


class RobotPose(BaseModel):
    """# 定义RobotPose模型参数:x、y坐标和θ朝向
    - 参数：
        - x: float = 0, 任务点位置x坐标
        - y: float = 0, 任务点位置y坐标
        - theta: float = 0, 任务点朝向X角度
    """
    x: float = 0  # 任务点位置x坐标
    y: float = 0  # 任务点位置y坐标
    theta: float = 0  # 任务点朝向X角度


class RobotAction(BaseModel):
    # 定义RobotAction模型表示任务点动作参数列表
    actionContent: str = ""  # 执行动作时长，秒数
    actionType: str = ""  # 动作类型，可填值"rotation":选择 "stop":停止
    actionName: str = ""  # 动作名称
    actionOrder: int = 0  # 执行动作顺序号，0为最优先处理


class RobotPoints(BaseModel):
    # 定义RobotPoints模型表示任务点参数列表
    position: RobotPose = RobotPose()  # 任务点位置
    pointType: str = ""  # 子任务点类型 可填值 "navigation":导航点， "charge":充电点，未填写默认为导航点
    # 子任务点动作列表，目前只支持一个动作，第一个动作
    actions: List[RobotAction] = [RobotAction()]
    pointName: str = ""  # 任务点名称
    index: int = 0  # 任务点索引
    isNew: bool = False  # 是否是新建的任务点
    cpx: float = 0  # 任务点位置x坐标
    cpy: float = 0  # 任务点位置y坐标


class RobotTask(BaseModel):
    taskName: str = "task"  # 任务名称
    gridItemIdx: int = 0  # web前端显示所需要的索引
    points: List[RobotPoints] = [RobotPoints()]  # 任务点列表，详细参考下面的任务点参数表
    mode: str = ""  # 任务模式， "point":多点导航 "path":路径导航
    evadible: int = 1  # 避障模式，1避障，2停障
    mapName: str = "taskMap"  # 地图名称
    speed: float = 0.5  # = Field(0.6, gt=0, lt=1.5)     # 导航时的速度参数0.1-1.5M/S
    editedName: str = ""  # 任务需要重命名的名称
    remark: str = "remark"  # 备注信息
    personName: str = "tang"  # 任务创建人

    @validator('speed')
    def speed_coerce(cls, v):
        # 导航时的速度参数0.1-1.5M/S
        if v < 0:
            return 0
        if v > 1.5:
            return 1.5
        return v


class RobotRealTimePoint(BaseModel):
    # 定义RobotRealTimePoint模型表示任务点列表
    position: RobotPose = RobotPose()  # 任务点位置
    isNew: bool = False  # 注意只有"mode"="path"的路径模式下有效，决定是否是新路径点的起点
    cpx: float = 0  # 曲线点x坐标，注意只有"mode"="path"的路径模式下，曲线点有效，将线段上的某个点作为贝塞尔曲线点
    cpy: float = 0  # 曲线点y坐标，注意只有"mode"="path"的路径模式下，曲线点有效，将线段上的某个点作为贝塞尔曲线点


class RobotRealTimeTask(BaseModel):
    # 定义RobotRealTimeTask模型表示实时任务请求模型
    loopTime: int = 1  # 循环次数
    points: List[RobotRealTimePoint] = [RobotRealTimePoint()]  # 实时任务模型任务点列表
    mode: str = ""  # 导航类型，可能值为 "point":多点导航 "path":多路径导航


# actions: Dict[str, RobotTask] = {}


class RobotTaskDict(BaseModel):
    # 定义RobotTaskDict模型表示任务字典
    tasksName: str = "tasks"  # 任务名称
    tasks: Dict[str, RobotTask]  # 任务点列表


"""# 机器人状态相关模块
"""


class RobotStatus(BaseModel):
    """## 定义RobotStatus模型表示机器人状态
    - 参数：
        - slam: 机器人程序启动状态
            - nav: str 机器人导航状态
                - state: bool 机器人导航状态 ture:开启 false:关闭
                - name: str 机器人导航地图名称，或者当前录制地图名称
                - task: str 机器人当前任务名称
        - robot: 机器人状态
            - angular_velocity: float 机器人角速度
            - linear_velocity: float 机器人线速度
            - fault_code: int 机器人底盘错误信息反馈
            - base_state: int 机器人底盘状态 0:正常状态
            - control_mode: int 机器人底盘控制模式 1-空闲状态 3-手柄控制
        - BMS: 机器人电池状态
            - batteryCurrent: float 机器人电池电流
            - batteryTemperature: float 机器人电池温度
            - batteryVoltage: float 机器人电池电压
            - SOH: int 机器人电池健康状态
            - SOC: int 机器人电池电量
        - sensor: 机器人传感器状态
            - imu_status: str 机器人imu状态：ON/OFF ON:开启 OFF:关闭
            - lidar_status: str 机器人激光雷达状态：ON/OFF ON:开启 OFF:关闭
            - RTK_status: str 机器人RTK状态：ON/OFF ON:开启 OFF:关闭
            - camera_status: str 机器人摄像头状态：ON/OFF ON:开启 OFF:关闭
    """
    slam: Dict[str, dict] = {
        "nav": {"state": False, "name": "", "task": ""}}  # 机器人slam状态
    robot: Dict[str, Union[int, float]] = {
        "angular_velocity": 0.0, "linear_velocity": 0.0, "fault_code": 0, "base_state": 0, "control_mode": 1}  # 机器人状态
    BMS: Dict[str, Union[int, float]] = {
        "batteryCurrent": 0.0, "batteryTemperature": 0.0, "batteryVoltage": 0.0, "SOH": 0, "SOC": 0}  # 机器人电池状态
    sensor: Dict[str, str] = {"imu_status": "ON", "lidar_status": "ON",
                              "RTK_status": "OFF", "camera_status": "OFF"}  # 机器人传感器状态


"""# 机器人上报的日志相关模块
"""


class RobotLog(BaseModel):
    """# 定义RobotLog模型表示机器人上报的日志
    参数：
        - stamp: Dict[str,int] 时间戳
            - sec: int 秒
            - nsec: int 纳秒
        - level: int 日志等级 1:debug 2:info 4:warn 8:error 16:fatal
        - msg: str 日志信息
    """
    stamp: Dict[str, int] = {"sec": 1680848214, "nsec": 679842222}
    level: int = 2
    msg: str = ""


class RobotSetting(BaseModel):
    """# 定义RobotSetting模型表示机器人配置
    - 参数：
        - **command**: List[CommandBase], 命令列表
            - **name**: str, 命令名称
            - **description**: str, 命令描述
            - **code**: str, 命令代码
            - **data**: Dict, 命令数据
        - **mapLimit**: List[Dict], 地图限制
            - **min**: Dict, 地图最小限制
                - **minX**: float, 地图最小x坐标
                - **minY**: float, 地图最小y坐标
                - **minTheta**: float, 地图最小角度
            - **max**: Dict, 地图最大限制
                - **maxX**: float, 地图最大x坐标
                - **maxY**: float, 地图最大y坐标
                - **maxTheta**: float, 地图最大角度
        - **sensorLimit**: List[Dict], 传感器限制
            - **name**: str, 传感器名称
            - **description**: str, 传感器描述
            - **code**: str, 传感器代码
            - **min**: float, 传感器最小值
            - **max**: float, 传感器最大值
            - **unit**: str, 传感器单位
        - **taskTime**: List[Dict], 任务限制
            - **name**: str, 任务名称
            - **description**: str, 任务描述
            - **times**:List[dict] , 任务时间
                - **startTime**: str, 任务开始时间
                - **endTime**: str, 任务结束时间
            - **remark**: str, 任务备注
        - **curisePoints**: List[Dict], 巡航点
            - **name**: str, 巡航点名称
            - **description**: str, 巡航点描述
            - **position**: List[dict], 巡航点列表
                - **x**: float, 巡航点x坐标
                - **y**: float, 巡航点y坐标
                - **theta**: float, 巡航点角度
            - **vision**:List[dict] , 巡航点视觉
                - **name**: str, 视觉名称
                - **command**: str, 视觉指令
                - **time**: int, 视觉等待时间
                - **description**: str, 视觉描述
            curiseFlag: bool, 是否巡航
            lightFlag: bool, 是否开灯
            - **remark**: str, 巡航点备注
    """
    command: List[CommandBase]
    mapLimit: List[Dict] = []
    sensorLimit: List[Dict]
    taskTime: List[Dict]
    curisePoints: List[Dict]


GRobotSetting = APP_DB["RobotSetting"]


class RobotManage:
    """# 机器人管理类
    """
    ip = "192.168.1.68"  # 设备ip地址
    port = 8880  # 设备端口号
    username = "admin"  # 设备用户名
    password = "dc123456"  # 设备密码

    LastError = -1
    Authorization = ""  # 登录设备返回的用户验证信息，24小时有效
    pose = RobotPose(x=0, y=0, theta=0)
    task = RobotTask()
    tasks: Dict[str, RobotTask] = {task.taskName: task}
    realtime_task = RobotRealTimeTask()
    status = RobotStatus()
    logs: List[RobotLog] = [RobotLog()]

    # setting: dict = RobotSetting(**GRobotSetting).dict()

    def __init__(self, ip: str = "192.168.1.68", port: int = 8880, username: str = "admin", password: str = "dc123456"):
        # 初始化机器人管理类
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        # self.Authorization = self.login()
        self.setting: dict = RobotSetting(**GRobotSetting).dict()

    def login(self, base: RobotBase = RobotBase()) -> bool:
        # 登录设备
        self.ip = base.ip
        self.port = base.port
        self.username = base.username
        self.password = base.password
        return True

    def get_config(self) -> bool:
        # 获取机器人配置信息
        self.setting: dict = RobotSetting(**GRobotSetting).dict()
        return True

    def set_config(self, config: RobotSetting) -> bool:
        # 设置机器人配置信息
        return True

    def update_config(self, setting: dict) -> bool:
        # 更新机器人配置信息
        for key in setting.keys():
            if key in GRobotSetting.keys():
                GRobotSetting[key] = setting[key]
        if self.get_config():
            # 保存修改
            APP_JsonDB.save(APP_DB)
            return True
        return False

    def get_status(self) -> bool:
        # 获取机器人状态信息
        return True

    def get_logs(self) -> bool:
        # 获取机器人日志信息
        return True

    def get_pose(self) -> bool:
        # 获取机器人位置信息
        return True

    def get_task(self) -> bool:
        # 获取机器人任务点信息
        return True

    def get_realtime_task(self) -> bool:
        # 获取机器人实时任务信息
        return True

    def set_pose(self, pose: RobotPose) -> bool:
        # 设置机器人位置信息
        self.pose = pose
        return True

    def set_task(self, task: RobotTask) -> bool:
        # 设置机器人任务点信息
        self.task = task
        return True

    def set_realtime_task(self, realtime_task: RobotRealTimeTask) -> bool:
        # 设置机器人实时任务信息
        self.realtime_task = realtime_task
        return True

    def get_tasks(self) -> Dict[str, RobotTask]:
        # 获取机器人任务列表
        return self.tasks

    def set_tasks(self, tasks: Dict[str, RobotTask]) -> bool:
        # 设置机器人任务列表
        self.tasks = tasks
        return True

    def update_tasks(self, tasks: Dict[str, RobotTask]) -> bool:
        # 更新机器人任务列表
        self.tasks.update(tasks)
        return True

    def add_task(self, task: RobotTask) -> bool:
        # 添加机器人任务
        self.tasks[task.taskName] = task
        return True

    def del_task(self, task_name: str) -> bool:
        # 删除机器人任务
        self.tasks.pop(task_name)
        return True


GRobotManage = RobotManage()

"""END
# 机器人管理模块
"""

"""
机器人管理模块 请求路径与方法
"""


@app.post("/user/robot/login", summary="登录机器人", tags=["机器人管理"])
async def robot_login(base: RobotBase = RobotBase()) -> ResponseReturn:
    """## 登录机器人
    - 参数：
        - base: RobotBase 机器人
            - ip: str 机器人ID
            - port: int 机器人端口号
            - username: str 机器人用户名
            - password: str 机器人密码
        - 示例：{"base":{"ip":"ip","port":port,"username":"username","password":"password"}}
    - 返回：
        - {"base":RobotBase 机器人信息}
    """
    LastError = LastErrorBase()
    if GRobotManage.login(base):
        return ResponseReturn(status=True, code=0, message="Login robot success.", data={"base": base})
    return ResponseReturn(status=False, code=-1, message=LastError.message, data=LastError)


@app.get("/user/robot/config", summary="获取机器人配置信息", tags=["机器人管理"])
async def robot_get_config(ip: str = Body("1")) -> ResponseReturn:
    """## 获取机器人配置信息
    - 参数：
        - ip: str 机器人ip (可不填)
        - 示例：
            - {"ip":"192.168.1.10"}
    - 返回：
        - {"config":RobotSetting 机器人配置信息}
    """
    LastError = LastErrorBase()
    if GRobotManage.get_config():
        return ResponseReturn(status=True, code=0, message="Get robot config success.",
                              data={"config": GRobotManage.setting})
    return ResponseReturn(status=False, code=-1, message=LastError.message, data=LastError)


@app.post("/user/robot/config/update", summary="更新机器人配置信息", tags=["机器人管理"])
async def robot_update_config(config: dict = Body(), ip: str = Body("1")) -> ResponseReturn:
    """## 更新机器人配置信息
    - 参数：
        - config: dict 机器人配置信息
        - ip: str 机器人ip (可不填)
    - 示例：
    ```json
        {
            "config":{
                "curisePoints":[
                    {
                        "name":"巡航点设置1",
                        "position":{
                            "x":0,
                            "y":0,
                            "theta":0
                        },
                        "vision":[
                            {
                                "name":"云台指令1",
                                "commad":"指令1",
                                "time":10#等待时间间隔
                            },
                            {
                                "name":"云台指令2",
                                "commad":"指令2",
                                "time":10#等待时间间隔
                            }
                        ],
                        "curiseFlag":True,#巡航开关
                        "LightFlag":True,#灯光开关
                        "remark":"巡航设置备注1"  
                    }
                ]
            },
            "ip":"192.168.1.10"
        }
    ```
    - 返回：
        - {"config":RobotSetting 机器人配置信息}
    """
    LastError = LastErrorBase()
    if GRobotManage.update_config(config):
        return ResponseReturn(status=True, code=0, message="Update robot config success.",
                              data={"config": GRobotManage.setting})
    return ResponseReturn(status=False, code=-1, message=LastError.message, data=LastError)


@app.get("/user/robot/status", summary="获取机器人状态相关的信息", tags=["机器人管理"])
async def robot_get_status(ip: str = Body("1")) -> ResponseReturn:
    """## 获取机器人状态相关的信息
    - 参数：
        - ip: str 机器人ip (可不填)
    - 返回：
        - {"status":RobotStatus 机器人状态信息}
    """
    LastError = LastErrorBase()
    if GRobotManage.get_status():
        return ResponseReturn(status=True, code=0, message="Get robot status success.",
                              data={"status": GRobotManage.status})
    return ResponseReturn(status=False, code=-1, message=LastError.message, data=LastError)


@app.get("/user/robot/pose", summary="获取机器人位置信息", tags=["机器人管理"])
async def robot_get_pose(ip: str = Body("1")) -> ResponseReturn:
    """## 获取机器人位置信息
    - 参数：
        - ip: str 机器人ip (可不填)
    - 返回：
        - {"pose":RobotPose 机器人位置信息}
    """
    LastError = LastErrorBase()
    if GRobotManage.get_pose():
        return ResponseReturn(status=True, code=0, message="Get robot pose success.", data={"pose": GRobotManage.pose})
    return ResponseReturn(status=False, code=-1, message=LastError.message, data=LastError)


@app.post("/user/robot/pose", summary="设置机器人位置信息", tags=["机器人管理"])
async def robot_set_pose(pose: RobotPose, ip: str = Body("1")) -> ResponseReturn:
    """## 设置机器人位置信息
    - 参数：
        - pose: RobotPose 机器人位置信息（必须）
            - x: float 机器人x坐标
            - y: float 机器人y坐标
            - theta: float 机器人角度
        - ip: str 机器人ip (可不填)
    - 示例：
        - {"pose":RobotPose 机器人位置信息, "ip":str 机器人ip}
    - 返回：
        - {"pose":RobotPose 机器人位置信息}
    """
    LastError = LastErrorBase()
    if GRobotManage.set_pose(pose):
        return ResponseReturn(status=True, code="/user/robot/pose", message="Set robot pose success.",
                              data={"pose": GRobotManage.pose})
    return ResponseReturn(status=False, code=-1, message=LastError.message, data=LastError)


@app.get("/user/robot/task", summary="获取地图任务路径信息", tags=["机器人管理"])
async def robot_get_task(ip: str = Body("1")) -> ResponseReturn:
    """## 获取地图任务路径信息
    - 参数：
        - ip: str 机器人ip (可不填)
    - 返回：
        - {"task":RobotTask 任务信息}
    """
    LastError = LastErrorBase()
    if GRobotManage.get_task():
        return ResponseReturn(status=True, code=0, message="Get robot task success.", data={"task": GRobotManage.task})
    return ResponseReturn(status=False, code=-1, message=LastError.message, data=LastError)


@app.post("/user/robot/task", summary="设置地图任务路径信息", tags=["机器人管理"])
async def robot_set_task(task: RobotTask, ip: str = Body("1")) -> ResponseReturn:
    """## 设置地图任务路径信息
    - 参数：
        - RobotTask 任务信息模型
        - ip: str 机器人ip (可不填)
    - 示例：        
        - {"task":{GET方法返回的task的数据}, "ip":str 机器人ip}
    - 返回：
        - {"task":RobotTask 任务信息}
    """
    LastError = LastErrorBase()
    print(task.taskName)
    if GRobotManage.set_task(task):
        return ResponseReturn(status=True, code=0, message="Set robot task success.", data={"task": GRobotManage.task})
    return ResponseReturn(status=False, code=-1, message=LastError.message, data=LastError)


@app.get("/user/robot/tasks", summary="获取所有机器人任务信息", tags=["机器人管理"])
async def robot_get_tasks(ip: str = Body("1")) -> ResponseReturn:
    """## 获取所有机器人任务路径信息
    - 参数：
        - ip: str 机器人ip (可不填)
    - 返回：
        - {"tasks":Dict[str, RobotTask], "ip":str 机器人ip}
    """
    LastError = LastErrorBase()
    if GRobotManage.get_tasks():
        return ResponseReturn(status=True, code=0, message="Get robot task list success.",
                              data={"tasks": GRobotManage.tasks})
    return ResponseReturn(status=False, code=-1, message=LastError.message, data=LastError)


@app.post("/user/robot/tasks", summary="设置机器人所有任务信息", tags=["机器人管理"])
async def robot_set_tasks(tasks: Dict[str, RobotTask], ip: str = Body("1")) -> ResponseReturn:
    """## 设置所有机器人实时任务信息
    - 参数：
        - tasks:Dict[str,RobotTask] 任务信息字典
        - ip: str 机器人ip (可不填)
    - 示例：
        - {"tasks":Dict[str, RobotTask], "ip":str 机器人ip}
    - 返回：
        - {"tasks":Dict[str, RobotTask]}
    """
    LastError = LastErrorBase()
    if GRobotManage.set_tasks(tasks):
        return ResponseReturn(status=True, code=0, message="Set robot task slist success.",
                              data={"tasks": GRobotManage.tasks})
    return ResponseReturn(status=False, code=-1, message=LastError.message, data=LastError)


@app.post("/user/robot/tasks/update", summary="更新机器人任务信息", tags=["机器人管理"])
async def robot_update_tasks(tasks: Dict[str, RobotTask], ip: str = Body("1")) -> ResponseReturn:
    """## 更新所有机器人实时任务信息
    - 参数：
        - tasks:Dict[str,RobotTask] 任务信息字典
        - ip: str 机器人ip (可不填)
    - 示例：        
        - {"tasks":Dict[str, RobotTask], "ip":str 机器人ip}
    - 返回：
        - {"tasks":Dict[str, RobotTask]}
    """
    LastError = LastErrorBase()
    if GRobotManage.update_tasks(tasks):
        return ResponseReturn(status=True, code=0, message="Update robot task list success.",
                              data={"tasks": GRobotManage.tasks})
    return ResponseReturn(status=False, code=-1, message=LastError.message, data=LastError)


@app.post("/user/robot/tasks/add", summary="添加机器人的一个任务信息", tags=["机器人管理"])
async def robot_add_tasks(task: RobotTask = RobotTask(), ip: str = Body("1")) -> ResponseReturn:
    """## 添加机器人的一个任务信息
    - 参数：
        - RobotTask 任务信息字典
            - taskName: str 任务名称(必须) 
        - ip: str 机器人ip (可不填)
    - 示例：        
        - {"task": RobotTask , "ip":str 机器人ip}
    - 返回：
        - {"tasks":Dict[str, RobotTask]}
    """
    LastError = LastErrorBase()
    if GRobotManage.add_task(task):
        return ResponseReturn(status=True, code=0, message="Add robot task success.",
                              data={"tasks": GRobotManage.tasks})
    return ResponseReturn(status=False, code=-1, message=LastError.message, data=LastError)


@app.post("/user/robot/tasks/delete", summary="删除机器人的一个任务信息", tags=["机器人管理"])
async def robot_delete_tasks(task: RobotTask, ip: str = Body("1")) -> ResponseReturn:
    """# 删除机器人的一个任务信息
    - 参数：
        - RobotTask 任务信息字典
            - taskName: str 任务名称(必须) 
        - ip: str 机器人ip (可不填)

    - 示例：        
        - {"task": RobotTask, "ip":str 机器人ip} 
    - 返回：
        - {"tasks":Dict[str, RobotTask]}
    """
    LastError = LastErrorBase()
    if GRobotManage.del_task(task.taskName):
        return ResponseReturn(status=True, code=0, message="Delete robot task list success.",
                              data={"tasks": GRobotManage.tasks})
    return ResponseReturn(status=False, code=-1, message=LastError.message, data=LastError)


"""END
机器人管理模块 请求路径与方法
"""

"""# 传感器管理模块
"""


class SensorBase(BaseModel):
    """传感器基础信息
    - 参数：
        - ip: str 传感器 监听ip地址
        - port: int 传感器 监听端口
        - name: str 传感器名称
        - description: str 传感器描述
    """
    ip: str = "0.0.0.0"
    port: int = 31024
    name: str = "传感器"
    description: str = ""


class SensorRobotData(SensorBase):
    """# 该项目消防机器人传感器数据
    两个氢气，一个烟雾传感器
    - 参数：
        - SensorBase
        - hydrogen1: float 氢气传感器1
        - hydrogen2: float 氢气传感器2
        - smoke: float 烟雾传感器
        - fire: int 是否灭火开关 0:关 1:开（询问时更新）
    """
    hydrogen1: float = 0.0
    hydrogen2: float = 0.0
    smoke: float = 0.0
    fire: int = 0


GSensorRobotData = SensorRobotData().dict()


class SensorManage:
    # 传感器信息管理类
    def __init__(self):
        self.sensor: dict = SensorRobotData(**GSensorRobotData).dict()

    def get_data(self) -> bool:
        # 获取传感器数据
        self.sensor: dict = SensorRobotData(**GSensorRobotData).dict()
        return True

    def set_sensor(self, sensor: dict) -> bool:
        # 设置传感器数据
        GSensorRobotData.update(sensor)
        if self.get_data():
            return True
        return False

    def set_fire(self, fire: int) -> bool:
        # 设置消防机器人灭火开关
        self.sensor.fire = fire
        return


GSensorManage = SensorManage()
"""END
# 传感器管理模块
"""

"""# 传感器管理模块 请求路径与方法
"""


@app.get("/user/sensor/data", summary="获取传感器数据", tags=["传感器管理"])
async def sensor_get_data(sensor: dict = Body(None, embed=True)) -> ResponseReturn:
    """## 获取传感器数据
    - 参数：
        - dict 传感器数据(目前可不用填写)
            - ip: str 传感器 监听ip地址(必须)
            - port: int 传感器 监听端口
            - 其他参数可选
        - 示例：
            - {"sensor":{"ip":"192.168.1.10","port":31024}}
    - 返回：
        - {"sensor":SensorRobotData}
    """
    LastError = LastErrorBase()
    if GSensorManage.get_data():
        return ResponseReturn(status=True, code=0, message="Get sensor data success.",
                              data={"sensor": GSensorManage.sensor})
    return ResponseReturn(status=False, code=-1, message=LastError.message, data=LastError)


@app.post("/user/sensor/data", summary="设置传感器数据", tags=["传感器管理"])
async def sensor_set_data(sensor: dict = Body(SensorBase(), embed=True)) -> ResponseReturn:
    """## 设置传感器数据
    - 参数：
        - SensorBase 传感器数据（可设置默认值，非必填，不填写则设置为默认值）
            - ip: str 传感器 监听ip地址
            - port: int 传感器 监听端口
            - name: str 传感器名称
            - description: str 传感器描述
        - 示例：
            - {"sensor":{"ip":"192.168.1.10","port":31024,"name":"传感器","description":"传感器描述"}}
    - 返回：
        - {"sensor":SensorRobotData}
    """
    LastError = LastErrorBase()
    if GSensorManage.set_sensor(SensorBase(**sensor).dict()):
        return ResponseReturn(status=True, code=0, message="Set sensor data success.",
                              data={"sensor": GSensorManage.sensor})
    return ResponseReturn(status=False, code=-1, message=LastError.message, data=LastError)


@app.post("/user/sensor/fire", summary="设置消防机器人灭火开关", tags=["传感器管理"])
async def sensor_set_fire(sensor: SensorRobotData = Body(SensorRobotData(), embed=True)) -> ResponseReturn:
    """## 设置消防机器人灭火开关
    - 参数：
        - SensorRobotData 传感器数据
            - ip: str 传感器 监听ip地址（可不填）
            - port: int 传感器 监听端口（可不填）
            - name: str 传感器名称（不填）
            - description: str 传感器描述（不填）
            - hydrogen1: float 氢气传感器1（不填）
            - hydrogen2: float 氢气传感器2（不填）
            - smoke: float 烟雾传感器（不填）
            - fire: int 是否灭火开关 0:关 1:开（询问时更新，必须-**其他参数无效**）
        - 示例：
            - {"sensor":{"ip":"192.168.1.10","port"=31024,"fire":0}}
            - {"sensor":{"fire":1}}
    - 返回：
        - {"sensor":SensorRobotData}
    """
    LastError = LastErrorBase()
    if GSensorManage.set_fire(sensor.fire):
        return ResponseReturn(status=True, code=0, message="Set sensor fire data success.",
                              data={"sensor": GSensorManage.sensor})
    return ResponseReturn(status=False, code=-1, message=LastError.message, data=LastError)


"""END
# 传感器管理模块 请求路径与方法
"""


class EventBase(BaseModel):
    """事件基础信息
    - 参数：
        - ID: str 事件ID(唯一)(时间戳)
        - name: str 事件名称
        - code: int 事件代码,可以设置着火事件报警代码为1，预警代码2
        - description: str 事件描述
    """
    ID: str = "2023, 7, 6, 18, 17, 2, 557892"
    name: str = ""
    code: int = 0
    description: str = ""


class EventsManage:
    # 事件信息管理类
    events: Dict[str, EventBase] = {}

    def get_events(self) -> bool:
        # 获取所有事件信息
        return True

    def set_events(self, events: Dict[str, EventBase]) -> bool:
        # 设置所有事件信息
        self.events = events
        return True

    def update_events(self, events: Dict[str, EventBase]) -> bool:
        # 更新所有事件信息
        self.events.update(events)
        return True

    def add_event(self, event: EventBase) -> bool:
        # 添加一个事件信息
        self.events[event.ID] = event
        return True

    def del_event(self, ID: str) -> bool:
        # 删除一个事件信息
        if ID in self.events.keys():
            self.events.pop(ID)
            return True
        return False

    def get_event(self, ID: str) -> bool:
        # 获取一个事件信息
        if ID in self.events.keys():
            return True
        return None


GEventsManage = EventsManage()
"""END
# 事件信息管理模块
"""

"""# 事件管理模块 请求路径与方法
"""


@app.get("/user/events", summary="获取所有事件信息", tags=["事件信息管理"])
async def events_get_events() -> ResponseReturn:
    """## 获取所有事件信息
    - 参数：
        - 无
    - 返回：
        - {"events":Dict[ID:str, EventBase]}
    """
    LastError = LastErrorBase()
    if GEventsManage.get_events():
        return ResponseReturn(status=True, code=0, message="Get events list success.",
                              data={"events": GEventsManage.events})
    return ResponseReturn(status=False, code=-1, message=LastError.message, data=LastError)


@app.get("/user/events/{ID}", summary="获取一个事件信息", tags=["事件信息管理"])
async def events_get_event(ID: str) -> ResponseReturn:
    """## 获取一个事件信息
    - 参数：
        - ID:str 事件ID，请求地址中获取，请求时填写
        - 示例：
            请求地址：/user/events/ID
    - 返回：
        - {"event":EventBase}
    """
    LastError = LastErrorBase()
    if GEventsManage.get_event(ID):
        return ResponseReturn(status=True, code=0, message="Get event success.",
                              data={"event": GEventsManage.events(ID)})
    return ResponseReturn(status=False, code=-1, message=LastError.message, data=LastError)


@app.post("/user/events", summary="设置所有事件信息", tags=["事件信息管理"])
async def events_set_events(events: Dict[str, EventBase] = Body(embed=True)) -> ResponseReturn:
    """## 设置所有事件信息
    - 参数：
        - events:Dict[str,EventBase] 事件信息字典
        - 示例：        
            - {"events":Dict[str, EventBase]}
    - 返回：
        - {"events":Dict[str, EventBase]}
    """
    LastError = LastErrorBase()
    if GEventsManage.set_events(events):
        return ResponseReturn(status=True, code=0, message="Set events list success.",
                              data={"events": GEventsManage.events})
    return ResponseReturn(status=False, code=-1, message=LastError.message, data=LastError)


@app.post("/user/events/update", summary="更新事件信息", tags=["事件信息管理"])
async def events_update_events(events: Dict[str, EventBase] = Body(embed=True)) -> ResponseReturn:
    """# 更新所有事件信息
    - 参数：
        - events:Dict[str,EventBase] 事件信息字典
        - 示例：        
            - {"events":Dict[str, EventBase]}
    - 返回：
        - {"events":Dict[str, EventBase]}
    """
    LastError = LastErrorBase()
    if GEventsManage.update_events(events):
        return ResponseReturn(status=True, code=0, message="Update event list success.",
                              data={"events": GEventsManage.events})
    return ResponseReturn(status=False, code=-1, message=LastError.message, data=LastError)


@app.post("/user/events/add", summary="添加一个事件信息", tags=["事件信息管理"])
async def events_add_event(event: EventBase = Body(EventBase(), embed=True)) -> ResponseReturn:
    """# 添加一个事件信息
    - 参数：
        - EventBase 事件信息字典
            - ID: str 事件ID(唯一)(时间戳)
            - name: str 事件名称
            - code: int 事件代码 
            - description: str 事件描述 
        - 示例：        
            - {"event":{"ID":"2023, 7, 6, 18, 17, 2, 557892","name":"事件名称","code":0,"description":"事件描述"}}
    - 返回：
        - {"events":Dict[str, EventBase]}
    """
    LastError = LastErrorBase()
    if GEventsManage.add_event(event):
        return ResponseReturn(status=True, code=0, message="Add event list success.",
                              data={"events": GEventsManage.events})
    return ResponseReturn(status=False, code=-1, message=LastError.message, data=LastError)


@app.post("/user/events/del", summary="删除一个事件信息", tags=["事件信息管理"])
async def events_del_event(event: EventBase = Body(EventBase(), embed=True)) -> ResponseReturn:
    """# 删除一个事件信息
    - 参数：
        - EventBase 事件信息字典
            - ID: str 事件ID(唯一)(时间戳)(必须)
        - 示例：        
            - {"event":{"ID":"2023, 7, 6, 18, 17, 2, 557892"}}
    - 返回：
        - {"events":Dict[str, EventBase]}
    """
    LastError = LastErrorBase()
    if GEventsManage.del_event(event.ID):
        return ResponseReturn(status=True, code=0, message="Delete event list success.",
                              data={"events": GEventsManage.events})
    return ResponseReturn(status=False, code=-1, message=LastError.message, data=LastError)


"""END
# 事件管理模块 请求路径与方法
"""

"""# 其他 请求路径与方法
"""


@app.get("/", summary="文档", tags=["其他"])
async def root():
    """
    文档说明:readme.md,API参数文档请访问 /docs
    - 无参数
    - 返回：
        - 文档页面
    """
    # return RedirectResponse(url="/docs",status_code=status.HTTP_302_FOUND)
    with open("api.html", encoding='utf-8') as f:
        return HTMLResponse(content=f.read(), status_code=200)


class LogSettingBase(BaseModel):
    """## 日志设置信息
    - 参数：
        - level: str 日志级别
            - DEBUG
            - INFO
            - WARNING
            - ERROR
            - CRITICAL
        - logpath: str 日志路径
        - logname: str 日志名称
        - logmaxsize: int 日志最大大小
        - logmaxcount: int 日志最大数量
        - logmaxtime: int 日志最大时间
        - remark: str 备注
    """
    level: str = "DEBUG"
    path: str = "./log"
    name: str = "log"
    maxsize: int = 1024 * 1024 * 10
    maxcount: int = 10
    maxtime: int = 24 * 60 * 60 * 7
    remark: str = ""


GLogSetting = ConfigAPP["log"]


@app.get("/other/log/config", summary="获取日志设置信息", tags=["其他"])
async def other_log_config() -> ResponseReturn:
    """# 获取日志设置信息
    - 参数：
        - 无参数
    - 返回：    
        - {"config":LogSettingBase}
    """
    return ResponseReturn(status=True, code=0, message="Success", data={"config": GLogSetting})


@app.post("/other/log/config/update", summary="更新日志设置信息", tags=["其他"])
async def other_log_update_config(config=Body(embed=True)) -> ResponseReturn:
    """## 更新日志设置信息
    - 参数：
        - config:LogSettingBase 日志设置信息
        - 示例：
            - {"config":{"level":"DEBUG","path":"./log","name":"log","maxsize":1024*1024*10,"maxcount":10,"maxtime":24*60*60*7,"remark":""}}
    - 返回：
        - {"config":LogSettingBase}
    """
    LastError = LastErrorBase()
    if config:
        GLogSetting.update(config)
        # ConfigAPP["log"] = GLogSetting
        with open(ConfigAPP_path, mode='w', encoding='utf-8') as f:
            json.dump(ConfigAPP, f, ensure_ascii=False, indent=4)
        return ResponseReturn(status=True, code=0, message="Update log config success.", data={"config": GLogSetting})
    LastError.ERROR_TYPE = "LOG_CONFIG_ERROR"
    LastError.code = 400
    LastError.message = "Log config error."
    return ResponseReturn(status=False, code=-1, message=LastError.message, data=LastError)


@app.post("other/command", summary="执行用户命令", tags=["其他"])
async def other_command(command: CommandBase) -> ResponseReturn:
    """## **执行用户命令,返回执行结果 DEBUG 的测试模式，仅限测试使用**
    - 参数：
        - command:CommandBase - 暂时没有命令
            - command: str 命令名称(必须)
                - start: 开始
                - stop: 停止
                - pause: 暂停
                - resume: 继续
                - cancel: 取消
                - reboot: 重启
                - shutdown: 关机
            - params: Dict[str, Any] 命令参数
        - 示例：    
            - {"command":"start","params":{}}
    - 返回：    
        - {"status":True,"code":0,"message":"Success","data":{}}
    """
    LastError = LastErrorBase()
    if command.command == "start":
        return ResponseReturn(status=True, code=0, message="Start success.", data={})
    elif command.command == "stop":
        return ResponseReturn(status=True, code=0, message="Stop success.", data={})
    LastError.ERROR_TYPE = "COMMAND_NOT_FOUND"
    LastError.code = 400
    LastError.message = "Command not found."
    return ResponseReturn(status=False, code=-1, message=LastError.message, data=LastError)


@app.get("/other/lasterror", summary="获取最后一次错误信息", tags=["其他"])
async def other_error() -> ResponseReturn:
    """# 获取最后一次错误信息
    - 参数：
        - 无参数
    - 返回：    
        - {"lasterror":LastError}
    """
    return ResponseReturn(status=True, code=0, message="Success", data={"lasterror": GLastError})


from modules.method_meter import MeterHttpClient

# 获取当前文件所在的目录
current_dir = os.path.dirname(__file__)

meter_config_path = os.path.join(current_dir, 'config', 'config_meter.json')

meter_client = MeterHttpClient(meter_config_path)


@app.get("/other/meter", summary="获取表计识别算法的结果", tags=["其他"])
async def other_meter(point_id: str, image_url: str):
    """## 请求表计识别数据
    - 参数:
        - point_id: str = "1", 表计炮号
        - image_url: str = "/image filename", 图片地址
        - 返回:
            - {"status":True,"code":0,"message":"Success","data":{"image_url":"http file path","result":[123]}}
    - 示例：
        - 请求：
            api/other/meter?point_id=1&image_url=D:/imgMeter/imgMeter.jpg
        - 返回：
            - {"status":True,"code":0,"message":"Success","data":{"image_url":"http file path","result":[123]}}
    """
    print("point_id:", point_id)
    print("image_url:", image_url)
    if point_id in meter_client.config.keys():
        # meter_return = meter_client.get_meter_result_from_point(point_id,image_url)
        meter_return = meter_client.get_meter_result_from_point("p1", "meter/2023-07-07_13_59_014.jpg")

        print(meter_return)
        # return ResponseModel(**meter_return)
        return str(meter_return["data"])

    else:
        # return ResponseModel(status=False, code="/other/meter", message="point_id not found", data={})
        return "55"


@app.get("/other/test", summary="test", tags=["其他"])
async def other_meter():
    return "hello"


"""END
# 其他 请求路径与方法
"""

"""# 发布测试的一些问题
"""
# 以下为权限验证开关
FlagCheckPermission = False


# @app.middleware("http")
async def check_authentication(request: Request, call_next):
    def check_permission(method, api, auth):
        # The following paths are always allowed:
        if api == '/login' or api == '/user/login' or api == '/docs' or api == '/' or api == '/openapi.json' or api == '/error':
            return True
        # Parse auth header and check scheme, username and password
        if method == 'POST' or method == 'GET':
            username = GUserManage.get_current_username(auth)
            if username == 'admin':
                return True
            else:
                if method == 'GET':
                    return True
                else:
                    return False

    if FlagCheckPermission:
        auth = request.headers.get('token')
        if not check_permission(request.method, request.url.path, auth):
            return ItemResponseResult(status=False, code=2, message="该用户没有权限，或者token过期", data={})
    return await call_next(request)


# 以下为允许客户端跨域设置
from fastapi.middleware.cors import CORSMiddleware

origins = ["http://localhost", "*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allow_headers=["*"],  # ["Authorization", "Content-Type", "token"]
)

# 允许HTTPS的证书
# from starlette.responses import HTMLResponse
# import ssl
# context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
# context.load_cert_chain('cert.pem', 'key.pem')


"""END
# 发布测试的一些问题
"""
# app.openapi(exclude_schemas=True)
# app.openapi_tags = []
# app.models_to_show = [LastErrorBase,ResponseReturn,RobotStatus,VisionConfig,EventBase,RobotTask]
# app.openapi_schema= {}
# if __name__ == "__main__":
#     import uvicorn
#     # uvicorn 将重新加载您的代码，因为您是从代码内部调用的。也许解决方法是将 uvicorn 调用放在单独的文件中，或者正如我所说，只需使用命令行
#     uvicorn.run("run:app", reload=True, port=8000, host="0.0.0.0",log_level="debug",limit_max_requests=100,limit_concurrency=100)
#     # uvicorn.run("run:app", reload=True, port=8000, host="0.0.0.0")
