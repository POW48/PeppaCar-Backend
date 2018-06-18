from picamera.array import PiRGBArray
import picamera
import cv2
import math
import numpy as np

_running = False
_prev_frame = None
_prev_bound = None


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


def find_circle(frame, mode='bgr', required=True):
    global _running, _prev_frame, _prev_bound
    if _running:
        if _prev_frame is None:
            return frame, [0, 0, 0, 0]
        return _prev_frame, _prev_bound
    _running = True
    if mode == 'yuv':
        frame = cv2.cvtColor(frame, cv2.COLOR_YUV2BGR)

    # too slow to use white balance, deprecated
    # frame = cv2.bitwise_and(frame, frame, mask=cv2.inRange(frame, (0, 0, 0), (230, 230, 230)))
    # frame = simplest_cb(frame, 1)

    frameHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_red = [0, 128, 128]
    upper_red = [2, 255, 255]
    lower_red_another = [163, 128, 90]
    upper_red_another = [180, 255, 255]
    mask1 = cv2.inRange(frameHSV, lower_red, upper_red)
    mask2 = cv2.inRange(frameHSV, lower_red_another, upper_red_another)
    mask = cv2.bitwise_or(mask1, mask2)

    # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    # mask = cv2.erode(mask, kernel)
    # # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    # mask = cv2.dilate(mask, kernel)

    image, contours, hierarchy = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    if len(contours) != 0:
        top_contour = map(lambda x: {'ca': cv2.contourArea(x), 'origin': x}, contours)
        top_contour = filter(lambda x: x['ca'] > 100, top_contour)
        top_contour = sorted(top_contour, key=lambda x: x['ca'], reverse=True)[:3]
        top_contour = map(lambda x: cv2.boundingRect(x['origin']), top_contour)
        top_contour = filter(lambda x: x[3] <= x[2] * 1.5, top_contour)
        try:
            bound = top_contour.__next__()
            if required:
                center = (int(bound[0] + bound[2] / 2), int(bound[1] + bound[3] / 2))
                cv2.circle(frame, center, int(max(bound[2], bound[3]) / 2), (255, 255, 255), 2)
        except StopIteration:
            bound = [0, 0, 0, 0]
    else:
        bound = [0, 0, 0, 0]
    if mode == 'yuv' and required:
        mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        frame = cv2.addWeighted(mask, 0.5, frame, 0.5, 0)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV_I420)
    if required:
        _prev_frame = frame
    _prev_bound = bound
    _running = False
    return frame, bound


if __name__ == '__main__':
    with picamera.PiCamera() as camera:
        camera.resolution = (320, 240)
        camera.framerate = 60
        rawCapture = PiRGBArray(camera, size=(320, 240))

        count = 0
        for frame in camera.capture_continuous(rawCapture, format='bgr', use_video_port=True):
            find_circle(frame.array)

            rawCapture.truncate()
            rawCapture.seek(0)
            count += 1
            # if count > 10:
            #     break
