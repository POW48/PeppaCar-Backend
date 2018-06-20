import datetime
import math
import time

import car
import cv2
import picamera
import picamera.array
from test_camera import find_circle


def center_ball(camera, threshold=10, max_rotating_time=3.0):
    """
    Adjust the position of car.
    Make the ball is at the center of image captured by camera.
    """
    direction = True # True means right
    rotate_interval = 0.05
    total_rotating_time = 0.0
    result = None
    resolution = camera.resolution

    rawCapture = picamera.array.PiRGBArray(camera, size=camera.resolution)
    for frame in camera.capture_continuous(rawCapture, format='bgr', use_video_port=True):
        # fetch an image from camera, then find the circle in it

        _, bound = find_circle(frame.array, required=False)
        # decides what to do
        center_x = bound[0] + bound[2] / 2
        if resolution[0] / 2 - threshold <= center_x <= resolution[0] / 2 + threshold:
            result = center_x
            car.brake()
            break
        elif 0 < center_x < resolution[0] / 2 - threshold:
            if not direction:
                rotate_interval = max(rotate_interval / 2, 0.005)
                direction = True
        elif center_x > resolution[0] / 2 + threshold:
            if direction:
                rotate_interval = max(rotate_interval / 2, 0.005)
                direction = False
        # do rotate car in place
        if direction:
            car.rotate_right_in_place()
            time.sleep(rotate_interval)
            total_rotating_time += rotate_interval
            car.brake()
        else:
            car.rotate_left_in_place()
            time.sleep(rotate_interval)
            total_rotating_time += rotate_interval
            car.brake()
        # wait for camera stable
        time.sleep(0.005)
        rawCapture.truncate()
        rawCapture.seek(0)

        if total_rotating_time >= max_rotating_time:
            break

    # returns the final x center of the ball
    return result


def x_center_of_rect(rect):
    """
    Compute the x center of a given rectangle
    """
    return rect[0] + rect[2] / 2


def save_image(kind, image):
    """
    Save image, using current time as file name. For debug use.
    """
    cv2.imwrite(kind + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '.jpg', image)


def find_goal(camera):
    # capture image and convert it to HSV
    frame = picamera.array.PiRGBArray(camera)
    camera.capture(frame, 'bgr')
    # we need to flip vertically because the camera is up-side-down
    image = cv2.flip(frame.array, 0)
    save_image('original', image) # for debug use
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # compute the size of horizon line strip
    # the number 0.407 is the horizontal line of image captured by car
    # if the position of camera changed, this number will also be changed
    y_begin = math.floor(hsv_image.shape[0] * 0.407) - 10
    y_end = y_begin + 20
    horizon_strip = hsv_image[y_begin:y_end, :, :]
    # filter black regions
    nearly_black_mask = cv2.inRange(horizon_strip, (0, 0, 0), (180, 70, 100))

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    nearly_black_mask = cv2.dilate(nearly_black_mask, kernel)
    nearly_black_mask = cv2.erode(nearly_black_mask, kernel)
    # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    # find contours in black regions
    _, contours, hierarchy = cv2.findContours(
        nearly_black_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    mask_copy = cv2.cvtColor(nearly_black_mask, cv2.COLOR_GRAY2RGB)
    cv2.drawContours(mask_copy, contours, -1, (0, 255, 0), 3)
    save_image('mask', nearly_black_mask) # for debug use
    # sort rectangles by x coordinates
    all_rects = sorted(filter(
        lambda rect: rect[2] * rect[3] >= 100, map(cv2.boundingRect, contours)), key=cv2.contourArea, reverse=True)
    if len(all_rects) >= 1:
        x, y, w, h = all_rects[0]
        return (x, y, 1, h), (x + w, y, 1, h)


def brake_if_touch_something(status):
    if status[0] == 0 or status[1] == 0 or status[2] == 0:
        car.brake()
        car.remove_infrared_sensor_change(brake_if_touch_something)


def push_ball():
    car.on_infrared_sensor_change(brake_if_touch_something)
    car.go()


def move_around_ball_clockwise():
    car.rotate_left_90()
    car.on_infrared_sensor_change(brake_if_touch_something)
    car.go()
    time.sleep(0.2)
    car.brake()


def move_around_ball_counterclockwise():
    car.rotate_right_90()
    car.on_infrared_sensor_change(brake_if_touch_something)
    car.go()
    time.sleep(0.2)
    car.brake()


def kick_ball():
    camera = picamera.PiCamera()
    camera.resolution = (320, 240)
    while True:
        # center the ball, exit if not found
        print('Center the ball')
        ball_center = center_ball(camera)
        if ball_center is None:
            print('Cannot find the ball, exit.')
            break
        # find the goal, move to next position if not found or inappropriate
        print('Find the goal')
        goal = find_goal(camera)
        if goal is None:
            print('Goal not found, move around ball clockwise')
            move_around_ball_clockwise()
        else:
            print('Goal found, left pole at {} and right pole at {}'.format(*goal))
            (left_pole, right_pole) = goal
            if left_pole < ball_center < right_pole:
                print('Ball is in front of goal, try push the ball')
                push_ball()
            elif ball_center <= left_pole:
                print('Ball is at the left of goal, move')
                move_around_ball_clockwise()
            elif ball_center >= right_pole:
                print('Ball is at the right of goal, move')
                move_around_ball_counterclockwise()
            else:
                raise RuntimeError(
                    'Hmmm, this situation will never be reached')


if __name__ == '__main__':
    try:
        kick_ball()
    except KeyboardInterrupt:
        car.brake()
        car.stop_polling()
