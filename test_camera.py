import io
from time import sleep
import picamera
import cv2
import numpy as np

with picamera.PiCamera() as camera:
    camera.resolution = (320, 240)
    camera.framerate = 60
    rawCapture = picamera.array.PiRGBArray(camera, size=(320, 240))

    count = 0
    for frame in camera.capture_continuous(rawCapture, format='rgb', use_video_port=True):
        image = frame.array
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

        circles1 = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 600, param1=100, param2=30, minRadius=10,
                                    maxRadius=200)
        circles = circles1[0, :, :]
        circles = np.uint16(np.around(circles))
        for i in circles[:]:
            cv2.circle(image, (i[0], i[1]), i[2], (255, 0, 0), 5)
        print(circles)

        rawCapture.truncate(0)
        count += 1
        if count > 10:
            break
