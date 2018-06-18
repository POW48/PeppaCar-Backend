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
speed = 10


def center_ball(bound, go=False):
    global direction, speed
    center_x = bound[0] + bound[2] / 2
    if camera.resolution[0] / 2 - threshold <= center_x <= camera.resolution[0] / 2 + threshold:
        speed = 0
        car.brake()
        if go:
            go_ball(bound)
    elif 0 < center_x < camera.resolution[0] / 2 - threshold:
        if not direction:
            speed = max(speed // 2, 4)
            car.left_wheels_speed = speed
            car.right_wheels_speed = speed
            car.add_left_wheels_speed(0)
            car.add_right_wheels_speed(0)
            car.rotate_right()
            direction = True
    elif center_x > camera.resolution[0] / 2 + threshold:
        if direction:
            speed = max(speed // 2, 4)
            car.left_wheels_speed = speed
            car.right_wheels_speed = speed
            car.add_left_wheels_speed(0)
            car.add_right_wheels_speed(0)
            car.rotate_left()
            direction = False


def go_ball(bound):
    radius = max(bound[2], bound[3]) / 2
    center_y = bound[1] + bound[3] / 2
    bottom = center_y - radius
    print(bottom)
    if bottom <= 0:
        rush_ball()
    else:
        car.go()
        if infrare_handler not in car._infrared_sensor_change_callbacks:
            car.on_infrared_sensor_change(infrare_handler)


def infrare_handler(tup):
    left, middle, right = tup
    if middle == 0:
        car.brake()
        car.remove_infrared_sensor_change(infrare_handler)


def rush_ball():
    car.go()
    time.sleep(0.1)
    car.brake()


def go_door():
    pass


if __name__ == '__main__':
    car.rotate_right()
    for frame in camera.capture_continuous(rawCapture, format='bgr', use_video_port=True):
        _, bound = test_camera.find_circle(frame.array)
        center_ball(bound, True)
        if speed == 0:
            break
        rawCapture.truncate()
        rawCapture.seek(0)
