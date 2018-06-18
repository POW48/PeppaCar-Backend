from picamera.array import PiRGBArray
import test_camera
import car
import picamera
import time

threshold = 10
direction = True
rush = False
speed = 10


def center_ball(bound, resolution, go=False):
    global direction, speed
    center_x = bound[0] + bound[2] / 2
    print('center', center_x)
    if resolution[0] / 2 - threshold <= center_x <= resolution[0] / 2 + threshold:
        car.brake()
        if go:
            go_ball(bound)
        else:
            speed = 0
    elif 0 < center_x < resolution[0] / 2 - threshold:
        if not direction:
            speed = max(speed // 2, 1)
            car.set_left_wheels_speed(speed)
            car.set_right_wheels_speed(speed)
            car.rotate_right()
            direction = True
    elif center_x > resolution[0] / 2 + threshold:
        if direction:
            speed = max(speed // 2, 1)
            car.set_left_wheels_speed(speed)
            car.set_right_wheels_speed(speed)
            car.rotate_left()
            direction = False
    elif not rush:
        if direction:
            car.rotate_right()
        else:
            car.rotate_left()


def go_ball(bound):
    global rush
    radius = max(bound[2], bound[3]) / 2
    center_y = bound[1] + bound[3] / 2
    bottom = center_y - radius
    print('bottom', bottom)
    car.set_left_wheels_speed(10)
    car.set_right_wheels_speed(10)
    if infrare_handler not in car._infrared_sensor_change_callbacks:
        car.on_infrared_sensor_change(infrare_handler)
    if bottom <= 0:
        rush = True
        rush_ball()
    else:
        rush = True
        car.go()


def infrare_handler(tup):
    global speed
    left, middle, right = tup
    print(tup)
    if middle == 0:
        speed = 0
        car.brake()
        car.remove_infrared_sensor_change(infrare_handler)


def rush_ball():
    global speed
    speed = 0
    car.go()
    time.sleep(1)
    car.brake()
    car.remove_infrared_sensor_change(infrare_handler)


def go_door():
    pass


if __name__ == '__main__':
    camera = picamera.PiCamera()
    camera.resolution = (320, 240)
    camera.framerate = 60
    rawCapture = PiRGBArray(camera, size=(320, 240))
    for frame in camera.capture_continuous(rawCapture, format='bgr', use_video_port=True):
        _, bound = test_camera.find_circle(frame.array)
        center_ball(bound, camera.resolution, True)
        if speed == 0:
            break
        rawCapture.truncate()
        rawCapture.seek(0)
