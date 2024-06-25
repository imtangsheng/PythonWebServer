
# Python后端框架

比较流行和常用的有:

- 1. Django:这是Python最流行的Web框架。它采用MVT架构,提供ORM、模板引擎、管理界面等功能。非常适合开发复杂的数据库驱动网站。
- 2. Flask:这是一个轻量级Web框架。它没有默认使用的数据库或模板,这使它非常灵活且易于扩展。适合开发简单的API和Web服务。 
- 3. FastAPI:这是一个基于Starlette的Web框架,处理HTTP请求的速度非常快。它采用类似Flask的API,提供灵活性,并支持异步请求处理。用于开发REST API非常合适。
除此之外,还有Falcon、CherryPy、Bottle等优秀框架。可以根据您的项目需求,选择对应的框架:
- 复杂网站:Django
- 微服务与API:Flask、FastAPI 

# [FastAPI教程](https://fastapi.tiangolo.com/tutorial/)

安装

    pip install fastapi[all]

或者

    pip install fastapi
    pip install "uvicorn[standard]"

运行文件：main.py 

    uvicorn main:app --reload
# 项目目录结构
```
proj/
├── main.py       # 入口
├── app          
│   ├── __init__.py
│   ├── models.py       # Pydantic模型
│   ├── routers       
│   │  ├── __init__.py 
│   │  ├── user.py     # URL为/users 的路由    
│   │  └── item.py     # URL 为 /items 的路由 
│   ├── services.py     # 业务服务
│   └── db.py           # 数据库操作   
├── templates       # 模板
├── libs            # 第三方库
│   ├── hikmicro    # 摄像头开发库
├── static          # 静态文件
├── tests           # 测试
└── configurations.py # 配置
requirements.txt

requirements.txt可以通过pip命令自动生成和安装。

生成requirements.txt文件：pip freeze > requirements.txt

安装requirements.txt依赖：pip install -r requirements.txt

将所有第三方库依赖放在requirements.txt文件中。运行 pip install -r requirements.txt安装所有依赖。

windows系统：直接在user目录中创建一个pip目录，如：C:\Users\xx\pip，新建文件pip.ini，内容如下：

[global]
 index-url = https://pypi.tuna.tsinghua.edu.cn/simple


```

大体上划分为:

- 主逻辑(main.py)
- models(模型)
- routers(路由)
- services(业务逻辑)
- templates/static(视图) 
- tests(测试)
- configurations(配置)
目录结构可以随项目复杂度而变化,但是遵循“单一抽象原则”和“单一责任原则”:
- 每个文件或目录只做一件事情
- 文件名能清楚反映内容

另外,可以使用`fastapi path`命令自动生成基本目录结构


# 代码

```
1. 定义请求和响应模型
使用Pydantic模型定义请求和响应的JSON schema:
python
# 请求模型
class ItemRequest(BaseModel):
    title: str
    description: Optional[str] = None

# 响应模型    
class ItemResponse(BaseModel):
    id: int
    title: str  
    ...
2. 定义服务类
使用类记录相关信息和提供方法:
python 
class ItemService:
    
    def __init__(self, items):
        self.items = items
        
    def get_all(self):
        return [ItemResponse(**item) for item in self.items]
        
    def get_by_id(self, id):
        ...
        
    def create(self, item: ItemRequest):
        ...
3. 定义路由函数
路由函数调用服务方法,并返回响应模型:
python
@app.get("/items/")
def read_items(item_service: ItemService = Depends()):
    return item_service.get_all()

@app.post("/items/") 
def create_item(item: ItemRequest, item_service: ItemService = Depends()):
    return item_service.create(item)
4. 使用依赖注入通 删官道的服务类
使用Depends(),让FastAPI自动注入依赖:
python
@app.get("/items/{id}")
def read_item(id: int, item_service: ItemService = Depends()): 
    ...
5. 返回正确的响应模型
服务方法应当始终返回响应模型,让FastAPI自动序列化为JSON:
python
def get_by_id(self, id):
    item = ... # 获取对应ID项
    return ItemResponse(**item)
这种方式可以更清晰地将路由、服务和模型分离,使代码保持高内聚、低耦合。同时根据请求和响应模型,生成自动的API文档和Schema验证。

```


## 安全第一步登录模块

```
pip install python-multipart
pip install python-jose[cryptography]
pip install passlib[bcrypt]

# to get a string like this run in git bash:
# openssl rand -hex 32

```
## API 的设计与实现

## 脚本类


/script/cv2capture.py

依赖 按照opencv

```
# 安装 opencv-contrib-python
# 使用国内源 -i https://mirrors.aliyun.com/pypi/simple/   
pip install opencv-contrib-python -i https://mirrors.aliyun.com/pypi/simple/   

```
实现录像，


##  部署到服务器，使用Git方法，共享文件夹
忽略全部文件夹
```
git config --global --add safe.directory "*"
```


## 程序打包教程

```   
pyinstaller.exe --onefile --version-file file_version_info.txt --icon=logo.ico main.py

pyinstaller.exe --onefile --version-file file_version_info.txt --icon=video.ico cv2capture.py

```
然后修改对应的文件