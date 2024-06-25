body = b'--boundary\r\nContent-Disposition: form-data; name="diskerror"\r\nContent-Type: application/xml; charset="UTF-8"\r\nContent-Length: 567\r\n\r\n<EventNotificationAlert>\r\n<ipAddress>10.148.193.234</ipAddress>\r\n<portNo>8000</portNo>\r\n<protocol>HTTP</protocol>\r\n<macAddress>a4:4c:62:22:4a:9a</macAddress>\r\n<dynChannelID>1</dynChannelID>\r\n<channelID>1</channelID>\r\n<dateTime>2023-12-26T20:00:54+08:00</dateTime>\r\n<activePostCount>1</activePostCount>\r\n<eventType>diskerror</eventType>\r\n<eventState>active</eventState>\r\n<eventDescription>diskerror alarm</eventDescription>\r\n<channelName>Camera 01</channelName>\r\n<HDDList>\r\n<HDD>\r\n<id>1</id>\r\n<diskNumber>1</diskNumber>\r\n</HDD>\r\n</HDDList>\r\n</EventNotificationAlert>\r\n\r\n--boundary--\r\n'
start_marker = b'--boundary'
end_marker = b'--boundary--'
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
    print(find_index)
    content = body[start_index:end_index].strip()
    print(content)
    AlarmData.append(content)

print(AlarmData)