# coding=utf-8
import threading
import time

from RPi import GPIO

#          3V3  (1) (2)  5V
#        GPIO2  (3) (4)  5V
#        GPIO3  (5) (6)  GND
#        GPIO4  (7) (8)  GPIO14
#          GND  (9) (10) GPIO15
# IFR_L GPIO17 (11) (12) GPIO18
# IFR_M GPIO27 (13) (14) GND
# IFR_R GPIO22 (15) (16) GPIO23
#          3V3 (17) (18) GPIO24
# TRK_L GPIO10 (19) (20) GND
# TRK_M  GPIO9 (21) (22) GPIO25
# TRK_R GPIO11 (23) (24) GPIO8
#          GND (25) (26) GPIO7
#        GPIO0 (27) (28) GPIO1
#        GPIO5 (29) (30) GND
#        GPIO6 (31) (32) GPIO12
# IN2   GPIO13 (33) (34) GND
# IN1   GPIO19 (35) (36) GPIO16 IN3
# ENA   GPIO26 (37) (38) GPIO20 IN4
#          GND (39) (40) GPIO21 ENB

# GPIO pin number of track detectors
PIN_LEFT_TRACK = 19
PIN_MIDDLE_TRACK = 21
PIN_RIGHT_TRACK = 23
# GPIO pin number of infrared sensors
PIN_LEFT_INFRARED = 11
PIN_MIDDLE_INFRARED = 13
PIN_RIGHT_INFRARED = 15
# GPIO pin number of wheels
PIN_LEFT_WHEELS_ENABLER = 40
PIN_RIGHT_WHEELS_ENABLER = 37
PIN_WHEELS_IN1 = 35
PIN_WHEELS_IN2 = 33
PIN_WHEELS_IN3 = 36
PIN_WHEELS_IN4 = 38
# All input pins
INPUT_PINS = [
    PIN_LEFT_TRACK,
    PIN_MIDDLE_TRACK,
    PIN_RIGHT_TRACK,
    PIN_LEFT_INFRARED,
    PIN_MIDDLE_INFRARED,
    PIN_RIGHT_INFRARED,
]
# All output pins
OUTPUT_PINS = [
    PIN_LEFT_WHEELS_ENABLER,
    PIN_RIGHT_WHEELS_ENABLER,
    PIN_WHEELS_IN1,
    PIN_WHEELS_IN2,
    PIN_WHEELS_IN3,
    PIN_WHEELS_IN4
]

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
for pin in INPUT_PINS:
    try:
        GPIO.setup(pin, GPIO.IN)
    except:
        print('Error when setup {} as input pin'.format(pin))
for pin in OUTPUT_PINS:
    try:
        GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
    except:
        print('Error when setup {} as output pin'.format(pin))

# PWM of motor enablers
LEFT_WHEELS_PWM = GPIO.PWM(PIN_LEFT_WHEELS_ENABLER, 500)
RIGHT_WHEELS_PWM = GPIO.PWM(PIN_RIGHT_WHEELS_ENABLER, 500)

# Current speed of left and right wheels
left_wheels_speed = 10
right_wheels_speed = 10

# Set a initial duty cycle for motor PWMs
LEFT_WHEELS_PWM.start(left_wheels_speed * 10)
RIGHT_WHEELS_PWM.start(right_wheels_speed * 10)


def _go_left():
    GPIO.output(PIN_WHEELS_IN3, GPIO.LOW)
    GPIO.output(PIN_WHEELS_IN4, GPIO.HIGH)


def _go_right():
    GPIO.output(PIN_WHEELS_IN1, GPIO.HIGH)
    GPIO.output(PIN_WHEELS_IN2, GPIO.LOW)


def _back_left():
    GPIO.output(PIN_WHEELS_IN3, GPIO.HIGH)
    GPIO.output(PIN_WHEELS_IN4, GPIO.LOW)


def _back_right():
    GPIO.output(PIN_WHEELS_IN1, GPIO.LOW)
    GPIO.output(PIN_WHEELS_IN2, GPIO.HIGH)


def _stop_left():
    GPIO.output(PIN_WHEELS_IN3, GPIO.LOW)
    GPIO.output(PIN_WHEELS_IN4, GPIO.LOW)


def _stop_right():
    GPIO.output(PIN_WHEELS_IN1, GPIO.LOW)
    GPIO.output(PIN_WHEELS_IN2, GPIO.LOW)


def add_left_wheels_speed(delta):
    global left_wheels_speed
    left_wheels_speed = max(0, min(10, left_wheels_speed + delta))
    LEFT_WHEELS_PWM.ChangeDutyCycle(left_wheels_speed * 10)


def add_right_wheels_speed(delta):
    global right_wheels_speed
    right_wheels_speed = max(0, min(10, right_wheels_speed + delta))
    RIGHT_WHEELS_PWM.ChangeDutyCycle(right_wheels_speed * 10)


def go():
    _go_left()
    _go_right()


def back():
    _back_left()
    _back_right()


def brake():
    _stop_left()
    _stop_right()


def rotate_left():
    _go_right()
    _back_left()


def rotate_right():
    _go_left()
    _back_right()


def get_infrared_sensor_status():
    return GPIO.input(PIN_LEFT_INFRARED), GPIO.input(PIN_MIDDLE_INFRARED), GPIO.input(PIN_RIGHT_INFRARED)


def get_track_detector_status():
    return GPIO.input(PIN_LEFT_TRACK), GPIO.input(PIN_MIDDLE_TRACK), GPIO.input(PIN_RIGHT_INFRARED)


def ultrasonic_sensor_status():
    raise NotImplementedError(
        '`ultrasonic_sensor_status` has not been implemented')


_last_infrared_sensor_status = get_infrared_sensor_status()
_last_track_detector_status = get_track_detector_status()
_infrared_sensor_change_callbacks = []
_track_detector_change_callbacks = []


def on_infrared_sensor_change(callback):
    _infrared_sensor_change_callbacks.append(callback)


def remove_infrared_sensor_change(callback):
    _infrared_sensor_change_callbacks.remove(callback)


def on_track_detector_change(callback):
    _track_detector_change_callbacks.append(callback)


def remove_track_detector_callback(callback):
    _track_detector_change_callbacks.remove(callback)


def _polling_thread_main():
    global _last_infrared_sensor_status, _last_track_detector_status
    while True:
        # infrared sensor
        infrared_sensor_status = get_infrared_sensor_status()
        # if changed
        if infrared_sensor_status != _last_infrared_sensor_status:
            # invoke callbacks
            for callback in _infrared_sensor_change_callbacks:
                try:
                    callback(infrared_sensor_status)
                except:
                    print('Error raised in change callback of infrared sensor')
            # update status
            _last_infrared_sensor_status = infrared_sensor_status
        # track detectors
        track_detector_status = get_track_detector_status()
        # if changed
        if track_detector_status != _last_track_detector_status:
            # invoke callbacks
            for callback in _track_detector_change_callbacks:
                try:
                    callback(track_detector_status)
                except:
                    print('Error raised in change callback of infrared sensor')
            # update status
            _last_track_detector_status = track_detector_status
        # sleep for a while
        time.sleep(0.01)


_sensor_polling_thread = threading.Thread(target=_polling_thread_main)
_sensor_polling_thread.start()


def simple_steer_track():
    def track_detector_callback(status):
        left, middle, right = status
        if left == 1 and middle == 0:
            rotate_right()
        if right == 1 and middle == 0:
            rotate_left()
        if middle == 1:
            go()

    on_track_detector_change(print)
    on_track_detector_change(track_detector_callback)
    go()


if __name__ == '__main__':
    from time import sleep
    try:
        simple_steer_track()
        _sensor_polling_thread.join()
    except KeyboardInterrupt:
        GPIO.cleanup()
