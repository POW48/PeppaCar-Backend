from picamera.array import PiRGBArray
import picamera
import cv2
import math
import numpy as np


def apply_mask(matrix, mask, fill_value):
    masked = np.ma.array(matrix, mask=mask, fill_value=fill_value)
    return masked.filled()


def apply_threshold(matrix, low_value, high_value):
    low_mask = matrix < low_value
    matrix = apply_mask(matrix, low_mask, low_value)

    high_mask = matrix > high_value
    matrix = apply_mask(matrix, high_mask, high_value)

    return matrix


def simplest_cb(img, percent):
    assert img.shape[2] == 3
    assert percent > 0 and percent < 100

    half_percent = percent / 200.0

    channels = cv2.split(img)

    out_channels = []
    for channel in channels:
        assert len(channel.shape) == 2
        # find the low and high precentile values (based on the input percentile)
        height, width = channel.shape
        vec_size = width * height
        flat = channel.reshape(vec_size)

        assert len(flat.shape) == 1

        flat = np.sort(flat)

        n_cols = flat.shape[0]

        low_val = flat[math.floor(n_cols * half_percent)]
        high_val = flat[math.ceil(n_cols * (1.0 - half_percent))]

        # saturate below the low percentile and above the high percentile
        thresholded = apply_threshold(channel, low_val, high_val)
        # scale the channel
        normalized = cv2.normalize(thresholded, thresholded.copy(), 0, 255, cv2.NORM_MINMAX)
        out_channels.append(normalized)

    return cv2.merge(out_channels)


def find_circle(frame):
    # frame = cv2.cvtColor(frame, cv2.COLOR_YUV2BGR)
    ret, frame = cv2.threshold(frame, 230, 255, cv2.THRESH_TOZERO_INV)
    frame = simplest_cb(frame, 1)
    frameHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_red = np.array([0, 128, 128])
    upper_red = np.array([2, 255, 255])
    lower_red_another = np.array([163, 128, 90])
    upper_red_another = np.array([180, 255, 255])
    mask1 = cv2.inRange(frameHSV, lower_red, upper_red)
    mask2 = cv2.inRange(frameHSV, lower_red_another, upper_red_another)
    mask = cv2.bitwise_or(mask1, mask2)
    res = cv2.bitwise_and(frame, frame, mask=mask)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
    mask = cv2.erode(mask, kernel)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
    mask = cv2.dilate(mask, kernel)

    image, contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if len(contours) != 0:
        max_contour = max(contours, key=cv2.contourArea)
        bound = cv2.boundingRect(max_contour)
        center = (int(bound[0] + bound[2] / 2), int(bound[1] + bound[3] / 2))
        cv2.circle(frame, center, int(max(bound[2], bound[3]) / 2), (255, 255, 255), 2)
    # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV)
    return frame


if __name__ == '__main__':
    with picamera.PiCamera() as camera:
        camera.resolution = (320, 240)
        camera.framerate = 60
        rawCapture = PiRGBArray(camera, size=(320, 240))

        count = 0
        for frame in camera.capture_continuous(rawCapture, format='yuv', use_video_port=True):
            find_circle(frame.array)

            rawCapture.truncate(0)
            count += 1
            # if count > 10:
            #     break
