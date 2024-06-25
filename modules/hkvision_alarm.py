import re

import xml.etree.ElementTree as ET

start_marker = b'--boundary'
end_marker = b'--boundary--'

def get_alarm_data_bytes_list(body):

    find_index = 0
    AlarmData = []

    while(True):
        start_index = body.find(start_marker,find_index)
        if start_index == -1:
            break
        start_index += len(start_marker)
        end_index = body.find(end_marker, start_index)
        if end_index == -1:
            break
        find_index = end_index + len(end_marker)
        # print(find_index)
        content = body[start_index:end_index].strip()
        # print("content")
        AlarmData.append(content)
    
    return AlarmData

def parse_header_field(header, field_name):
    pattern = rb'%s: ([^\r\n]+)'  %field_name
    match = re.search(pattern, header)
    return match.group(1) if match else None


def parse_header_field_by_name(header_field, name):
    # 使用正则表达式提取 name 的值
    match = re.search(rb'%s="([^"]+)"' %name, header_field)
    return match.group(1) if match else None

def get_alarm_data_bytes_header(header):
    return {
        b"Content-Disposition": parse_header_field(header, rb'Content-Disposition'),
        b"Content-Type":parse_header_field(header, rb'Content-Type'),
        b"Content-Length":parse_header_field(header, rb'Content-Length')
        }

def get_alarm_data_bytes_body_xml(xml_data):
    pattern = rb'<EventNotificationAlert>([\s\S]*?)</EventNotificationAlert>'
    match = re.search(pattern, xml_data)
    if not match:
        print("报警内容为空，没有报警信息提示xml格式数据")
        return None
    # 解析报警内容
    
    print("解析报警内容")
    xml_data_bytes = match.group(0).strip()
    print(len(xml_data_bytes))
    root = ET.fromstring(xml_data_bytes)
    # print("报警内容：")
    # print(root)
    
    # 提取需要的数据
    alarm = {}
    alarm['channelName'] = root.find('channelName').text
    alarm['ipAddress'] = root.find('ipAddress').text
    alarm['portNo'] = root.find('portNo').text
    alarm['channelID'] = root.find('channelID').text
    alarm['dateTime'] = root.find('dateTime').text
    alarm['eventType'] = root.find('eventType').text
    alarm['eventState'] = root.find('eventState').text
    alarm['eventDescription'] = root.find('eventDescription').text
    DetectionRegionList = root.find('DetectionRegionList')
    detection_region = []
    detail = "  "
    for region_entry in DetectionRegionList.findall('DetectionRegionEntry'):
        region = {}
        region['regionID'] = region_entry.find('regionID').text
        detail += "规则"+ region['regionID']+":"
        region['fireMaxTemperature'] = region_entry.find('FireDetection').find('fireMaxTemperature').text
        detail += "最高温度："+region['fireMaxTemperature']

        detection_region.append(region)

    alarm['DetectionRegionList'] = detection_region

    # 打印提取的数据
    # jsonData.get("type");
    # alarmEntity.setType("test");
    # alarmEntity.setIp("ip");
    # alarmEntity.setDetail("detail");
    # alarmEntity.setFPan("p");
    # alarmEntity.setFTilt("t");
    # alarmEntity.setFZoom("z");
    # alarmEntity.setDwPicUrl("video path");
    # alarmEntity.setDwThermalPicUrl("thermal path");
    post_data = {}
    post_data['type'] = "火点报警上传"
    post_data['ip'] = alarm['ipAddress']
    post_data['detail'] = alarm['channelName'] + detail


    print("火点报警上传")
    print(post_alarm_to_server(post_data))

    
    # print(alarm)
    return alarm

def get_fireDetection_data(body):
    pass

import datetime
# image/jpeg
# application/xml; charset="UTF-8"
def get_alarm_data_by_bytes(body):
    AlarmData = {}
    AlarmData['timestamp'] = datetime.datetime.now().timestamp() *1000
    alarm_data_bytes_list = get_alarm_data_bytes_list(body)
    print("AlarmData:")
    AlarmData['alarm_list'] = []
    for content_data_bytes in alarm_data_bytes_list:
        alarm_data_list = []
        index_find_start_marker =0 - len(start_marker)
        index_find_end_marker = 0
        while(index_find_start_marker != -1):
            alarm_data = {}
            index_find_start_marker += len(start_marker)
            header_index_end = content_data_bytes.find(b'\r\n\r\n',index_find_start_marker)
            print(" header_index_end结束标记",header_index_end)
            if(header_index_end ==-1):
                break
            bytes_header = content_data_bytes[index_find_start_marker:header_index_end]
            print("content_data bytes_header 报文数据:",bytes_header)
            alarm_header = get_alarm_data_bytes_header(bytes_header)
            print(alarm_header[b"Content-Disposition"])
            alarm_type = parse_header_field_by_name(alarm_header[b"Content-Disposition"], b"name")
            print("报警类型：",alarm_type)
            alarm_data['header'] = alarm_header
            alarm_data['name'] = alarm_type

            if(alarm_type == b"fireDetection"):
                print("烟火检测")
                if (b'application/xml' in alarm_header[b"Content-Type"]):
                    print("烟火检测数据解析")
                    # index_find_end_marker = content_data_bytes.find(b'\r\n\r\n',header_index_end+4)
                    index_find_end_marker = int(alarm_header[b"Content-Length"])+header_index_end+4
                    alarm_data_xml = content_data_bytes[header_index_end+4:index_find_end_marker]
                    print(header_index_end+4)
                    print(index_find_end_marker)
                    print(alarm_header[b"Content-Length"])
                    print(len(alarm_data_xml.strip()))
                    alarm_data['data'] = get_alarm_data_bytes_body_xml(alarm_data_xml)

                elif(b'image/jpeg' in alarm_header[b"Content-Type"]):
                    print("烟火检测image/jpeg数据解析")
                    alarm_end_index = int(alarm_header[b"Content-Length"])
                    index_find_end_marker = header_index_end+4+alarm_end_index
                    alarm_data_jpg = content_data_bytes[header_index_end+4:index_find_end_marker]
                    print(header_index_end+4)
                    print(alarm_end_index)
                    print(index_find_end_marker)
                    print(alarm_header[b"Content-Length"])
                    print(len(alarm_data_jpg.strip()))
                    # print(alarm_data_jpg)
                    alarm_data['data'] = alarm_data_jpg
                else:
                    print("烟火检测未知的数据解析")
                    alarm_data['data'] = None
                    index_find_end_marker = header_index_end+4
            elif(alarm_type == b"thermometry"):
                print("温度报警")
                index_find_end_marker = header_index_end+4
            else:
                print("其他报警类型")
                print(alarm_type)
                index_find_end_marker = header_index_end+4
            # print("报警类型")
            alarm_data_list.append(alarm_data)
            # 如果还有开始标志标志
            index_find_start_marker = content_data_bytes.find(start_marker,index_find_end_marker)
            
        # while(index_find_start_marker != -1):
        AlarmData['alarm_list'].append(alarm_data_list)
    print("parse alarm end")
    return AlarmData

import requests
url_alarm = "http://10.148.7.8:8091/other/vision/a"
def post_alarm_to_server(alarm_data):
    try:
        response = requests.post(url_alarm,json=alarm_data,timeout = 10)
    except Exception as e:
        print(e)
        return False
    if response.status_code != 200:
        print("post_alarm_to_server error:",response.status_code)
        print(response.text)
        return False
    return True
    
if __name__ == '__main__':
    body = b'--boundary\r\n\r\nContent-Disposition: form-data; name="fireDetection"\r\nContent-Type: application/xml; charset="UTF-8"\r\nContent-Length: 5297\r\n\r\n<EventNotificationAlert>\r\n<ipAddress>10.1.99.8</ipAddress>\r\n<portNo>8000</portNo>\r\n<protocol>HTTP</protocol>\r\n<macAddress>a4:4c:62:22:d7:3c</macAddress>\r\n<dynChannelID>2</dynChannelID>\r\n<channelID>2</channelID>\r\n<dateTime>2023-12-27T18:07:58+08:00</dateTime>\r\n<activePostCount>1</activePostCount>\r\n<eventType>fireDetection</eventType>\r\n<eventState>active</eventState>\r\n<eventDescription>fireDetection alarm</eventDescription>\r\n<DetectionRegionList>\r\n<DetectionRegionEntry>\r\n<regionID>1</regionID>\r\n<RegionCoordinatesList>\r\n<RegionCoordinates>\r\n<positionX>683</positionX>\r\n<positionY>10</positionY>\r\n</RegionCoordinates>\r\n<RegionCoordinates>\r\n<positionX>714</positionX>\r\n<positionY>10</positionY>\r\n</RegionCoordinates>\r\n<RegionCoordinates>\r\n<positionX>714</positionX>\r\n<positionY>46</positionY>\r\n</RegionCoordinates>\r\n<RegionCoordinates>\r\n<positionX>683</positionX>\r\n<positionY>41</positionY>\r\n</RegionCoordinates>\r\n</RegionCoordinatesList>\r\n<FireDetection>\r\n<FireRegion>\r\n<x>683</x>\r\n<y>10</y>\r\n<width>31</width>\r\n<height>36</height>\r\n</FireRegion>\r\n<HighestPoint>\r\n<x>703</x>\r\n<y>15</y>\r\n</HighestPoint>\r\n<temperatureUnit>celsius</temperatureUnit>\r\n<fireMaxTemperature>68</fireMaxTemperature>\r\n<targetDistance>-1</targetDistance>\r\n<AbsoluteHigh>\r\n<elevation>0</elevation>\r\n<azimuth>0</azimuth>\r\n<absoluteZoom>0</absoluteZoom>\r\n</AbsoluteHigh>\r\n</FireDetection>\r\n</DetectionRegionEntry>\r\n<DetectionRegionEntry>\r\n<regionID>2</regionID>\r\n<RegionCoordinatesList>\r\n<RegionCoordinates>\r\n<positionX>785</positionX>\r\n<positionY>20</positionY>\r\n</RegionCoordinates>\r\n<RegionCoordinates>\r\n<positionX>812</positionX>\r\n<positionY>20</positionY>\r\n</RegionCoordinates>\r\n<RegionCoordinates>\r\n<positionX>812</positionX>\r\n<positionY>66</positionY>\r\n</RegionCoordinates>\r\n<RegionCoordinates>\r\n<positionX>785</positionX>\r\n<positionY>47</positionY>\r\n</RegionCoordinates>\r\n</RegionCoordinatesList>\r\n<FireDetection>\r\n<FireRegion>\r\n<x>785</x>\r\n<y>20</y>\r\n<width>27</width>\r\n<height>46</height>\r\n</FireRegion>\r\n<HighestPoint>\r\n<x>792</x>\r\n<y>31</y>\r\n</HighestPoint>\r\n<temperatureUnit>celsius</temperatureUnit>\r\n<fireMaxTemperature>65</fireMaxTemperature>\r\n<targetDistance>-1</targetDistance>\r\n<AbsoluteHigh>\r\n<elevation>0</elevation>\r\n<azimuth>0</azimuth>\r\n<absoluteZoom>0</absoluteZoom>\r\n</AbsoluteHigh>\r\n</FireDetection>\r\n</DetectionRegionEntry>\r\n<DetectionRegionEntry>\r\n<regionID>3</regionID>\r\n<RegionCoordinatesList>\r\n<RegionCoordinates>\r\n<positionX>414</positionX>\r\n<positionY>328</positionY>\r\n</RegionCoordinates>\r\n<RegionCoordinates>\r\n<positionX>437</positionX>\r\n<positionY>328</positionY>\r\n</RegionCoordinates>\r\n<RegionCoordinates>\r\n<positionX>437</positionX>\r\n<positionY>354</positionY>\r\n</RegionCoordinates>\r\n<RegionCoordinates>\r\n<positionX>414</positionX>\r\n<positionY>351</positionY>\r\n</RegionCoordinates>\r\n</RegionCoordinatesList>\r\n<FireDetection>\r\n<FireRegion>\r\n<x>414</x>\r\n<y>328</y>\r\n<width>23</width>\r\n<height>26</height>\r\n</FireRegion>\r\n<HighestPoint>\r\n<x>429</x>\r\n<y>343</y>\r\n</HighestPoint>\r\n<temperatureUnit>celsius</temperatureUnit>\r\n<fireMaxTemperature>69</fireMaxTemperature>\r\n<targetDistance>-1</targetDistance>\r\n<AbsoluteHigh>\r\n<elevation>0</elevation>\r\n<azimuth>0</azimuth>\r\n<absoluteZoom>0</absoluteZoom>\r\n</AbsoluteHigh>\r\n</FireDetection>\r\n</DetectionRegionEntry>\r\n<DetectionRegionEntry>\r\n<regionID>4</regionID>\r\n<RegionCoordinatesList>\r\n<RegionCoordinates>\r\n<positionX>0</positionX>\r\n<positionY>375</positionY>\r\n</RegionCoordinates>\r\n<RegionCoordinates>\r\n<positionX>3</positionX>\r\n<positionY>375</positionY>\r\n</RegionCoordinates>\r\n<RegionCoordinates>\r\n<positionX>3</positionX>\r\n<positionY>390</positionY>\r\n</RegionCoordinates>\r\n<RegionCoordinates>\r\n<positionX>0</positionX>\r\n<positionY>378</positionY>\r\n</RegionCoordinates>\r\n</RegionCoordinatesList>\r\n<FireDetection>\r\n<FireRegion>\r\n<x>0</x>\r\n<y>375</y>\r\n<width>3</width>\r\n<height>15</height>\r\n</FireRegion>\r\n<HighestPoint>\r\n<x>0</x>\r\n<y>380</y>\r\n</HighestPoint>\r\n<temperatureUnit>celsius</temperatureUnit>\r\n<fireMaxTemperature>101</fireMaxTemperature>\r\n<targetDistance>-1</targetDistance>\r\n<AbsoluteHigh>\r\n<elevation>0</elevation>\r\n<azimuth>0</azimuth>\r\n<absoluteZoom>0</absoluteZoom>\r\n</AbsoluteHigh>\r\n</FireDetection>\r\n</DetectionRegionEntry>\r\n<DetectionRegionEntry>\r\n<regionID>5</regionID>\r\n<RegionCoordinatesList>\r\n<RegionCoordinates>\r\n<positionX>27</positionX>\r\n<positionY>468</positionY>\r\n</RegionCoordinates>\r\n<RegionCoordinates>\r\n<positionX>38</positionX>\r\n<positionY>468</positionY>\r\n</RegionCoordinates>\r\n<RegionCoordinates>\r\n<positionX>38</positionX>\r\n<positionY>483</positionY>\r\n</RegionCoordinates>\r\n<RegionCoordinates>\r\n<positionX>27</positionX>\r\n<positionY>479</positionY>\r\n</RegionCoordinates>\r\n</RegionCoordinatesList>\r\n<FireDetection>\r\n<FireRegion>\r\n<x>27</x>\r\n<y>468</y>\r\n<width>11</width>\r\n<height>15</height>\r\n</FireRegion>\r\n<HighestPoint>\r\n<x>27</x>\r\n<y>473</y>\r\n</HighestPoint>\r\n<temperatureUnit>celsius</temperatureUnit>\r\n<fireMaxTemperature>63</fireMaxTemperature>\r\n<targetDistance>-1</targetDistance>\r\n<AbsoluteHigh>\r\n<elevation>0</elevation>\r\n<azimuth>0</azimuth>\r\n<absoluteZoom>0</absoluteZoom>\r\n</AbsoluteHigh>\r\n</FireDetection>\r\n</DetectionRegionEntry>\r\n</DetectionRegionList>\r\n<channelName>#4\xe6\xb1\xbd\xe6\x9c\xba\xe8\xa5\xbf\xe5\x8d\x97\xe8\xa7\x92\xe6\x9e\xaa\xe6\x9c\xba</channelName>\r\n<detectionPicturesNumber>2</detectionPicturesNumber>\r\n</EventNotificationAlert>\r\n\r\n--boundary\r\nContent-Disposition: form-data; name="fireDetection"; filename="fireDetection.jpg";\r\nContent-Type: image/jpeg\r\nContent-Length: 4\r\n\r\n\\xfd\xaa4\xff\x00\xb1\r\n\r\n\r\n\r\n--boundary\r\nContent-Disposition: form-data; name="fireDetection"; filename="fireDetection.jpg";\r\nContent-Type: image/jpeg\r\nContent-Length: 5\r\n\r\n\\xfd\xaa4\xff\x00\xb1\r\n\r\n--boundary--\r\n\r\n'
    print(get_alarm_data_by_bytes(body))

