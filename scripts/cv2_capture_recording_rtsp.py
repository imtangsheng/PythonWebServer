# python
import cv2
import datetime
import os
import time
import logging
import threading

class VideoHandler:
    threads = []
    running = True
    def __init__(self, log_file='video.log', log_level=logging.INFO):
        self.log_file = log_file
        logging.basicConfig(level=log_level,
                            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%m-%d %H:%M',
                            filename=self.log_file,
                            filemode='a')

    def capture_is_opened(self, url: str, channel: str = 1) -> bool:
        capture = cv2.VideoCapture(url + channel)
        ret = capture.isOpened()
        capture.release()
        return ret

    def save_image(self, url: str, channel: str = 1, image_path: str = 'video', image_type='jpg') -> bool:

        capture = cv2.VideoCapture(url + channel)
        ret, frame = capture.read()
        if ret:
            filepath = self.get_filepath(image_path, image_type)
            cv2.imwrite(filepath, frame)
            logging.info('Saved image to %s', filepath)
        else:
            logging.error('Error reading video stream from %s', url + channel)
        capture.release()

    def play_video(self, url: str, channel: str = 1, window_name='frame'):

        capture = cv2.VideoCapture(url + channel)

        while True:
            ret, frame = capture.read()

            if ret:
                cv2.imshow(window_name, frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                break

        capture.release()
        cv2.destroyAllWindows()

    def record_video(self, url, channel, video_path, video_type='avi',
                     max_size=1*1024*1024*1024, wait_reconnect=10):

        filepath = self.get_filepath(video_path,  video_type)
        cap = cv2.VideoCapture(url + channel)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)

        vout = cv2.VideoWriter(filepath, cv2.VideoWriter_fourcc(
            *'XVID'), fps, (width, height))
        self.running = True
        while self.running:
            ret, frame = cap.read()

            if ret:
                vout.write(frame)

                size = os.path.getsize(filepath)
                if size >= max_size:
                    logging.info('Reached max file size, rotating files...')
                    self.rotate_file(filepath, video_path, video_type)
                    filepath = self.get_filepath(video_path, video_type)
                    vout = cv2.VideoWriter(filepath, cv2.VideoWriter_fourcc(
                        *'XVID'), fps, (width, height))

            else:
                logging.warning(
                    'Error reading video stream, reconnecting in %d secs...', wait_reconnect)
                time.sleep(wait_reconnect)
                cap = cv2.VideoCapture(url + channel)
                continue

        cap.release()
        vout.release()
        logging.info('Stopped recording')
    
    def record_video_thread(self, url, channel, video_path, video_type='avi',
                     max_size=1*1024*1024*1024, wait_reconnect=10):
        thread = threading.Thread(target=self.record_video, args=(url, channel, video_path, video_type, max_size, wait_reconnect))
        thread.start()
        self.threads.append(thread)

    def get_filepath(self, path: str, file_type: str) -> str:
        now = datetime.datetime.now()
        filename = now.strftime('%Y%m%d_%H%M%S.'+file_type)
        path = os.path.join(path, now.strftime('%Y%m'),now.strftime('%Y%m%d'))
        filepath = os.path.join(path, filename)
        if not os.path.exists(path):
            os.makedirs(path)
        return filepath

    def rotate_file(filepath, video_path, video_type):
        now = datetime.datetime.now()
        new_name = now.strftime('%Y%m%d_%H%M%S.'+video_type)
        os.rename(filepath, os.path.join(video_path, new_name))

    def close(self):
        logging.shutdown()
        self.running = False
    def __del__(self):
        self.close()


if __name__ == '__main__':
    # RTSP视频流URL
    # // 说明：
    # // username：用户名，例如admin
    # // password：密码，例如12345
    # // ip：设备的ip地址，例如192.0.0.64
    # // port：端口号默认554，若为默认可以不写
    # // codec：有h264、MPEG-4、mpeg4这几种
    # // channel：通道号，起始为ch1,ch2
    # // subtype：码流类型，主码流为main，子码流为sub

    # 2012年之前的设备
    # rtsp://[username]:[passwd]@[ip]:[port]/[codec]/ch[channel]/[subtype]/av_stream
    # 新设备
    # rtsp://[username]:[passwd]@[ip]:[port]/Streaming/Channels/[channel](?parm1=value1&parm2=value2)
    # channel: 通道号，从1开始,101表示通道1的主码流，102表示通道1的子码流，以此类推
    ip = "192.168.1.36"
    port = "554"
    username = "admin"
    password = "dacang80"
    codec = "h264"
    channel = "1"
    subtype = "main"

    url = "rtsp://%s:%s@%s:%s/Streaming/Channels/" % (
        username, password, ip, port)
    url_old = "rtsp://%s:%s@%s:%s/%s/ch%s/%s/av_stream" % (
        username, password, ip, port, codec, channel, subtype)

    video_handler = VideoHandler()
    # video_handler.record_video(url, channel='102', video_path='video',video_type='avi', max_size=1*1024*1024*1024, wait_reconnect=10)
    # video_handler.record_video(url, channel='202', video_path='infrared',video_type='avi', max_size=1*1024*1024*1024, wait_reconnect=10)
    video_handler.record_video_thread(url, channel='102', video_path='video',video_type='avi', max_size=1*1024*1024*1024, wait_reconnect=10)
    video_handler.record_video_thread(url, channel='202', video_path='infrared',video_type='avi', max_size=1*1024*1024*1024, wait_reconnect=10)

    while True:
        time.sleep(1)
        key = input('Press q to quit:')
        if key == 'q':
            break
    # while True:
        key2 = cv2.waitKey(1) & 0xFF
        if key2 == ord('q'):
            break
        time.sleep(1)
        print('Press q to quit:')
    print('Closing...')
    video_handler.close()
    print('Done')