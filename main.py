import os

# 打印当前工作目录
print("当前工作目录:", os.getcwd())

# 打印默认目录
print("默认目录expanduser:", os.path.expanduser("~"))

# 文件路径
file_path = __file__

# 打印文件的目录
print("文件的目录__file__:", os.path.dirname(file_path))

print("文件的目录__file__:", os.path.abspath(file_path))
print("文件的目录__file__:", os.path.dirname(os.path.abspath(file_path)))


# 打印更改后的工作目录
print("新的工作目录:", os.getcwd())

current_path = os.getcwd()
config_path = os.path.join(current_path, "config/config.json")
print("配置文件路径config_path:",config_path)

# 更改工作目录为文件的目录
os.chdir(current_path)

import run
import json
if __name__ == "__main__":
    with open(config_path, mode='r', encoding='utf-8') as f:
        config = json.load(f)
    import uvicorn
    print("Host:",config['host'])
    print("port:",config['port'])
    # uvicorn 将重新加载您的代码，因为您是从代码内部调用的。也许解决方法是将 uvicorn 调用放在单独的文件中，或者正如我所说，只需使用命令行
    #     uvicorn.run("run:app", reload=True, port=8000, host="0.0.0.0",log_level="debug",limit_max_requests=100,limit_concurrency=100)
    uvicorn.run(run.app, reload=False, port=config['port'], host=config['host'])
