import cv2
import math
import numpy as np

max_value = 255
max_value_H = 360 // 2
low_H = 0
low_S = 200
low_V = 60
high_H = 2
high_S = 255
high_V = 255
window_capture_name = 'Video Capture'
window_detection_name = 'Object Detection'
low_H_name = 'Low H'
low_S_name = 'Low S'
low_V_name = 'Low V'
high_H_name = 'High H'
high_S_name = 'High S'
high_V_name = 'High V'


def on_low_H_thresh_trackbar(val):
    global low_H
    global high_H
    low_H = val
    low_H = min(high_H - 1, low_H)
    cv2.setTrackbarPos(low_H_name, window_detection_name, low_H)


def on_high_H_thresh_trackbar(val):
    global low_H
    global high_H
    high_H = val
    high_H = max(high_H, low_H + 1)
    cv2.setTrackbarPos(high_H_name, window_detection_name, high_H)


def on_low_S_thresh_trackbar(val):
    global low_S
    global high_S
    low_S = val
    low_S = min(high_S - 1, low_S)
    cv2.setTrackbarPos(low_S_name, window_detection_name, low_S)


def on_high_S_thresh_trackbar(val):
    global low_S
    global high_S
    high_S = val
    high_S = max(high_S, low_S + 1)
    cv2.setTrackbarPos(high_S_name, window_detection_name, high_S)


def on_low_V_thresh_trackbar(val):
    global low_V
    global high_V
    low_V = val
    low_V = min(high_V - 1, low_V)
    cv2.setTrackbarPos(low_V_name, window_detection_name, low_V)


def on_high_V_thresh_trackbar(val):
    global low_V
    global high_V
    high_V = val
    high_V = max(high_V, low_V + 1)
    cv2.setTrackbarPos(high_V_name, window_detection_name, high_V)


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


camera = cv2.VideoCapture(0)

# cv2.namedWindow(window_detection_name)
# cv2.createTrackbar(low_H_name, window_detection_name, low_H, max_value_H, on_low_H_thresh_trackbar)
# cv2.createTrackbar(high_H_name, window_detection_name, high_H, max_value_H, on_high_H_thresh_trackbar)
# cv2.createTrackbar(low_S_name, window_detection_name, low_S, max_value, on_low_S_thresh_trackbar)
# cv2.createTrackbar(high_S_name, window_detection_name, high_S, max_value, on_high_S_thresh_trackbar)
# cv2.createTrackbar(low_V_name, window_detection_name, low_V, max_value, on_low_V_thresh_trackbar)
# cv2.createTrackbar(high_V_name, window_detection_name, high_V, max_value, on_high_V_thresh_trackbar)

while True:
    (grabbed, frame) = camera.read()
    if grabbed:
        # ret, frame = cv2.threshold(frame, 230, 255, cv2.THRESH_TOZERO_INV)
        # frame = simplest_cb(frame, 1)
        # frameHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # lower_red = np.array([0, 128, 128])
        # upper_red = np.array([2, 255, 255])
        # lower_red_another = np.array([163, 128, 90])
        # upper_red_another = np.array([180, 255, 255])
        # mask1 = cv2.inRange(frameHSV, lower_red, upper_red)
        # mask2 = cv2.inRange(frameHSV, lower_red_another, upper_red_another)
        # mask = cv2.bitwise_or(mask1, mask2)
        # res = cv2.bitwise_and(frame, frame, mask=mask)
        #
        # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
        # mask = cv2.erode(mask, kernel)
        # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
        # mask = cv2.dilate(mask, kernel)
        #
        # image, contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        # if len(contours) != 0:
        #     max_contour = max(contours, key=cv2.contourArea)
        #     bound = cv2.boundingRect(max_contour)
        #     center = (int(bound[0] + bound[2] / 2), int(bound[1] + bound[3] / 2))
        #     cv2.circle(frame, center, int(max(bound[2], bound[3]) / 2), (255, 255, 255), 2)

        frameHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # lower_red = np.array([0, 128, 128])
        # upper_red = np.array([2, 255, 255])
        lower_red = np.array((low_H, low_S, low_V))
        upper_red = np.array((high_H, high_S, high_V))
        # lower_red_another = np.array([163, 128, 90])
        # upper_red_another = np.array([180, 255, 255])
        mask = cv2.inRange(frameHSV, lower_red, upper_red)
        # mask2 = cv2.inRange(frameHSV, lower_red_another, upper_red_another)
        # mask = cv2.bitwise_or(mask1, mask2)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        mask = cv2.erode(mask, kernel)
        # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        mask = cv2.dilate(mask, kernel)

        image, contours, hierarchy = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        if len(contours) != 0:
            top_contour = sorted(contours, key=cv2.contourArea, reverse=True)[:3]
            top_contour = filter(lambda x: cv2.contourArea(x) > 50, top_contour)
            top_contour = map(lambda x: cv2.boundingRect(x), top_contour)
            top_contour = filter(lambda x: x[3] <= x[2] * 1.5, top_contour)
            top_contour = list(top_contour)
            if len(top_contour) != 0:
                bound = top_contour[0]
            else:
                bound = [0, 0, 0, 0]
        else:
            bound = [0, 0, 0, 0]

        cv2.imshow('FrameHSV', mask)
        cv2.imshow('frame', frame)

    cv2.waitKey(1)

cv2.destroyAllWindows()
