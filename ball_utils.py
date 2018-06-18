from picamera.array import PiRGBArray
import test_camera
import car
import picamera
import time

camera = picamera.PiCamera()
camera.resolution = (320, 240)
camera.framerate = 60
threshold = 10
rawCapture = PiRGBArray(camera, size=(320, 240))
direction = True
rush = False
speed = 10


def center_ball(bound, go=False):
    global direction, speed
    center_x = bound[0] + bound[2] / 2
    print('center', center_x)
    if camera.resolution[0] / 2 - threshold <= center_x <= camera.resolution[0] / 2 + threshold:
        speed = 0
        car.brake()
        if go:
            go_ball(bound)
    elif 0 < center_x < camera.resolution[0] / 2 - threshold:
        if not direction:
            speed = max(speed // 2, 1)
            car.set_left_wheels_speed(speed)
            car.set_right_wheels_speed(speed)
            car.rotate_right()
            direction = True
    elif center_x > camera.resolution[0] / 2 + threshold:
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
    global speed, rush
    radius = max(bound[2], bound[3]) / 2
    center_y = bound[1] + bound[3] / 2
    bottom = center_y - radius
    print('bottom', bottom)
    speed = 10
    car.set_left_wheels_speed(speed)
    car.set_right_wheels_speed(speed)
    # if bottom <= 0:
    #     rush_ball()
    # else:
    rush = True
    car.go()
    if infrare_handler not in car._infrared_sensor_change_callbacks:
        car.on_infrared_sensor_change(infrare_handler)


def infrare_handler(tup):
    global speed
    left, middle, right = tup
    if middle == 0:
        speed = 0
        car.brake()
        car.remove_infrared_sensor_change(infrare_handler)


def rush_ball():
    global speed
    speed = 0
    car.go()
    time.sleep(0.5)
    car.brake()


def go_door():
    pass


if __name__ == '__main__':
    for frame in camera.capture_continuous(rawCapture, format='bgr', use_video_port=True):
        _, bound = test_camera.find_circle(frame.array)
        center_ball(bound, True)
        if speed == 0:
            break
        rawCapture.truncate()
        rawCapture.seek(0)
