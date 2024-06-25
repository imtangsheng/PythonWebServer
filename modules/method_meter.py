# method_meter.py
# 表计识别算法

# 算法API接口

import os
import json
import requests
s = requests.Session()
s.timeout=10

ERROR_METER = {
    0:"正常",
    -1:"找不到识别目标",
    -2:"入参不准确或无法获得图像数据",
    -3:"算法处理异常",
    -4:"算法未启动"
    }

class MeterHttpClient:
    def __init__(self, config_path):
        # 读取json配置
        with open(config_path, mode='r', encoding='utf-8') as f:
            self.config = json.load(f)
    
    def get_meter_result_from_point(self, point_id:str,image_url:str)->dict:
        # 调用算法API接口
        result = {}
        if point_id not in self.config.keys():
#             result['status'] = False
            result['message'] = "point_id is not in config"
            point_id = "0"
#             return result

        url = self.config["api"] + self.config[point_id]["url"]
        data = {
            "image_url":image_url,
#             "image_url":self.config["api_image"] + image_url,#"api_image":"http://127.0.0.1:1122/image?name=",
            "other_infor":self.config[point_id]["other_infor"]
        }
        try:
            response = requests.post(url, json=data,timeout=10)
        except Exception as e:
            result['status'] = False
            result['message'] = e
            return result
        if response.status_code != 200:
            print("请求错误，请求返回：",response.status_code,response.text())
            result['status'] = False
            result['code'] = response.status_code
            result['message'] = "请求错误，请求返回：" + response.text()

        # {
        #     "err_desc": "meter has been detected",
        #     "errnbr": 0,
        #     "image_download_url": "http://192.168.1.133:2016/D:/_Cprogram_v14/Release/data/pointermeter/dst/2023_09_23/2023-09-23_16_30_340.jpg",
        #     "meter_rst": [
        #         {
        #             "region_id": 1,
        #             "result": 0.00477483
        #         }
        #     ]
        # }
        # {'err_desc': 'meter_recognize is disable !', 'errnbr': -4, 'image_download_url': ''}
        meter_return = response.json()
        print(meter_return)
        if meter_return['errnbr'] == 0:
            result['status'] = True
            result['code'] = 0
            #result['message'] = meter_return['err_desc']
            result['message'] = ERROR_METER.get(result['code'],"未知错误码："+str(result['code']))
            result['data'] = {}
            result['data']['image_url'] = meter_return['image_download_url']
            result['data']['normalRange'] = self.config[point_id]["normalRange"]
            result['data']["data"] = []
            for rts in meter_return['meter_rst']:
#                 print(rts)
                result['data']['data'].append(rts['result'])
            print("表计识别算法返回:")
            print(result)
            return result
        else:
            result['status'] = False
            result['code'] = meter_return['errnbr']

            #result['message'] = meter_return['err_desc']
            #请求 -5没有该参数，统一一个返回错误
            #result['message'] = "表计识别失败"
            result['message'] = ERROR_METER.get(result['code'],"未知错误码："+str(result['code']))
            return result


if __name__ == '__main__':
    # 获取当前文件所在的目录
    current_dir = os.path.dirname(__file__)

    # 拼接上级目录
    parent_dir = os.path.dirname(current_dir)
    config_path = os.path.join(parent_dir, 'config', 'config_meter.json')

    meter = MeterHttpClient(config_path)
    test = {}
    test = meter.get_meter_info('p1',test)
    print(test)

