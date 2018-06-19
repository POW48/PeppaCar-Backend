import time

import picamera
import picamera.array

import car
from test_camera import find_circle


def center_ball(camera, threshold=10, max_rotating_time=3.0):
    direction = True
    rotate_interval = 0.05
    total_rotating_time = 0.0
    result = None
    resolution = camera.resolution

    while total_rotating_time < max_rotating_time:
        # fetch an image from camera, then find the circle in it
        start = time.time()
        frame = picamera.array.PiRGBArray(camera, size=camera.resolution)
        camera.capture(frame, format='bgr')
        end = time.time()
        print('Capture: {} seconds'.format(end - start))
        start = time.time()
        _, bound = find_circle(frame.array)
        end = time.time()
        print('Recognize: {} seconds'.format(end - start))
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


def find_goal(camera):
    # capture image and convert it to HSV
    frame = picamera.array.PiRGBArray(camera)
    camera.capture(frame, 'bgr')
    hsv_image = cv2.cvtColor(frame.array, cv2.BGR2HSV)
    # compute the size of horizon line strip
    y_begin = math.floor(image.shape[0] * 0.407) - 10
    y_end = y_begin + 20
    horizon_strip = image[y_begin:y_end, :, :]
    nearly_black_mask = cv2.inRange(horizon_strip, (0, 0, 0), (180, 255, 50))
    # find rectangles
    _, contours, hierarchy = cv2.findContours(
        nearly_black_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # sort rectangles by x coordinates
    all_rects = sorted(filter(
        lambda rect: rect[2] * rect[3] >= 100, map(cv2.boundingRect, contours)), key=lambda r: r[0])
    if len(all_rects) > 1:
        return x_center_of_rect(all_rects[0]), x_center_of_rect(all_rects[-1])


def push_ball():
    def brake_if_touch_ball(status):
        if status[1] == 0:
            car.brake()
        car.remove_infrared_sensor_change(brake_if_touch_ball)

    car.on_infrared_sensor_change(brake_if_touch_ball)
    car.go()


def move_around_ball_clockwise():
    car.rotate_left_in_place()
    time.sleep(0.1)
    car.go()
    time.sleep(0.1)
    car.brake()


def move_around_ball_counterclockwise():
    car.rotate_right_in_place()
    time.sleep(0.1)
    car.go()
    time.sleep(0.1)
    car.brake()


def kick_ball():
    camera = picamera.PiCamera(resolution=resolution)
    while True:
        # center the ball, exit if not found
        ball_center = center_ball(camera)
        if ball_center is None:
            print('Cannot find the ball.')
            break
        # find the goal, move to next position if not found or inappropriate
        goal = find_goal(camera)
        if goal is None:
            move_around_ball_clockwise()
        else:
            (left_pole, right_pole) = goal
            if left_pole < ball_center < right_pole:
                push_ball()
            elif ball_center <= left_pole:
                move_around_ball_clockwise()
            elif ball_center >= right_pole:
                move_around_ball_counterclockwise()
            else:
                raise RuntimeError(
                    'Hmmm, this situation will never be reached')


if __name__ == '__main__':
    try:
        kick_ball()
    except:
        car.brake()
        car.stop_polling()
