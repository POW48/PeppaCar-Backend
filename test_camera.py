import io
from time import sleep
import picamera
import cv2
import numpy as np

with picamera.PiCamera() as camera:
    camera.resolution = (320, 240)
    stream = io.BytesIO()
    for foo in camera.capture_continuous(stream, format='jpeg', use_video_port=True):
        data = np.frombuffer(stream.getvalue(), dtype=np.uint8)
        image = cv2.imdecode(data, cv2.CV_LOAD_IMAGE_UNCHANGED)
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

        circles1 = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 600, param1=100, param2=30, minRadius=10,
                                    maxRadius=200)
        circles = circles1[0, :, :]
        circles = np.uint16(np.around(circles))
        print(circles)

        stream.truncate()
        stream.seek(0)
