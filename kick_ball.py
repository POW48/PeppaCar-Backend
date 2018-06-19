import time

import picamera
import picamera.array

import car
from test_camera import find_circle


def center_ball(resolution=(640, 480), threshold=10, max_rotating_time=3.0):
    direction = True
    rotate_interval = 0.05
    total_rotating_time = 0.0
    result = None

    camera = picamera.PiCamera(resolution=resolution)
    frame = picamera.array.PiRGBArray(camera)

    while total_rotating_time < max_rotating_time:
        # fetch an image from camera, then find the circle in it
        camera.capture(frame, format='bgr')
        _, bound = find_circle(frame.array)
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

    return result

def push_ball():
    def brake_if_touch_ball(status):
        if status[1] == 0:
            car.brake()
        car.remove_infrared_sensor_change(brake_if_touch_ball)

    car.on_infrared_sensor_change(brake_if_touch_ball)
    car.go()


def kick_ball():
    while True:
        # center the ball, exit if not found
        ball_center = center_ball()
        if ball_center is None:
            print('Cannot find the ball.')
            break
        # find the goal, move to next position if not found
        goal = find_goal()
        if goal is None:
            car.rotate_left_in_place()
            time.sleep(0.1)
            car.go()
            time.sleep(0.1)
            car.brake()
        else:
            (left_pole, right_pole) = goal
            if left_pole < ball_center < right_pole:
                push_ball()
            elif ball_center <= left_pole:
                car.rotate_left_in_place()
                time.sleep(0.1)
                car.go()
                time.sleep(0.1)
                car.brake()
            elif ball_center >= right_pole:
                car.rotate_right_in_place()
                time.sleep(0.1)
                car.go()
                time.sleep(0.1)
                car.brake()


if __name__ == '__main__':
    try:
        center_ball()
    except:
        car.brake()
        car.stop_polling()
