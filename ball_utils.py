from picamera.array import PiRGBArray
import test_camera
import car
import picamera
import time

threshold = 10
direction = True
rush = False
time_eclipse = 0.2


def load():
    global direction, rush, time_eclipse
    direction = True
    rush = False
    time_eclipse = 0.2


def unload():
    car.brake()


def center_ball(bound, resolution, go=False):
    global direction, time_eclipse
    center_x = bound[0] + bound[2] / 2
    if resolution[0] / 2 - threshold <= center_x <= resolution[0] / 2 + threshold:
        car.brake()
        if go:
            go_ball(bound)
        else:
            time_eclipse = 0
        return
    elif 0 < center_x < resolution[0] / 2 - threshold:
        if not direction:
            time_eclipse = max(time_eclipse / 2, 0.05)
            direction = True
    elif center_x > resolution[0] / 2 + threshold:
        if direction:
            time_eclipse = max(time_eclipse / 2, 0.05)
            direction = False
    if not rush:
        if time_eclipse == 0:
            time_eclipse = 0.2
        if direction:
            car.rotate_right()
            time.sleep(time_eclipse)
            car.brake()
        else:
            car.rotate_left()
            time.sleep(time_eclipse)
            car.brake()
        # wait for camera stable
        time.sleep(0.15)


def go_ball(bound):
    global rush
    radius = max(bound[2], bound[3]) / 2
    center_y = bound[1] + bound[3] / 2
    bottom = center_y - radius
    car.set_left_wheels_speed(10)
    car.set_right_wheels_speed(10)
    if not car.registered_infrared_sensor_change(infrare_handler):
        car.on_infrared_sensor_change(infrare_handler)
    if bottom <= 0:
        rush = True
        rush_ball()
    else:
        rush = True
        car.go()


def infrare_handler(tup):
    global time_eclipse, rush
    left, middle, right = tup
    if middle == 0:
        time_eclipse = 0
        rush = False
        car.brake()
        car.remove_infrared_sensor_change(infrare_handler)


def rush_ball():
    global time_eclipse, rush
    car.go()
    time.sleep(0.8)
    time_eclipse = 0
    rush = False
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
        if time_eclipse == 0:
            break
        rawCapture.truncate()
        rawCapture.seek(0)
