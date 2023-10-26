if __name__ == "__main__":
    import uvicorn

    # uvicorn 将重新加载您的代码，因为您是从代码内部调用的。也许解决方法是将 uvicorn 调用放在单独的文件中，或者正如我所说，只需使用命令行
    #     uvicorn.run("run:app", reload=True, port=8000, host="0.0.0.0",log_level="debug",limit_max_requests=100,limit_concurrency=100)
    uvicorn.run("run:app", reload=True, port=8000, host="0.0.0.0")
