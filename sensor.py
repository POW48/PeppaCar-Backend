import time

from RPi import GPIO

LEFT_TRACK_DETECTOR = 29
MIDDLE_TRACK_DETECTOR = 31
RIGHT_TRACK_DETECTOR = 33
LEFT_INFRARED_SENSOR = 35
RIGHT_INFRARED_SENSOR = 37
ULTRASONIC_TRIGGER = 38
ULTRASONIC_ECHO = 40
ALL_INPUT_PINS = [
    LEFT_TRACK_DETECTOR,
    MIDDLE_TRACK_DETECTOR,
    RIGHT_TRACK_DETECTOR,
    LEFT_INFRARED_SENSOR,
    RIGHT_INFRARED_SENSOR,
    ULTRASONIC_ECHO
]


GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(ULTRASONIC_TRIGGER, GPIO.OUT)
for pin in ALL_INPUT_PINS:
    GPIO.setup(pin, GPIO.IN)


def infrared_sensors():
    return GPIO.input(LEFT_INFRARED_SENSOR), GPIO.input(RIGHT_INFRARED_SENSOR)


def track_detectors():
    return GPIO.input(LEFT_TRACK_DETECTOR), GPIO.input(MIDDLE_TRACK_DETECTOR), GPIO.input(RIGHT_TRACK_DETECTOR)


def ultrasonic_detector():
    GPIO.output(ULTRASONIC_TRIGGER, GPIO.HIGH)
    time.sleep(0.000015)
    GPIO.output(ULTRASONIC_TRIGGER, GPIO.LOW)
    result = GPIO.wait_for_edge(ULTRASONIC_ECHO, GPIO.RISING, timeout=1000)
    if result is None:
        print('Waiting for rising edge failed.')
        return
    start = time.time()
    result = GPIO.wait_for_edge(ULTRASONIC_ECHO, GPIO.FALLING, timeout=1000)
    if result is None:
        print('Waiting for falling edge failed.')
        return
    end = time.time()
    return (end - start) * 340 / 2


__all__ = ['infrared_sensors', 'track_detectors', 'ultrasonic_detector']
