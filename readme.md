
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
```