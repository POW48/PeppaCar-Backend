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
last_rising_time = None
last_falling_time = None
last_distance = None


def on_echo_rising():
    global last_rising_time
    last_rising_time = time.time()


def on_echo_falling():
    global last_rising_time, last_falling_time, last_distance
    last_falling_time = time.time()
    last_distance = (last_falling_time - last_rising_time) * 340 / 2


GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(ULTRASONIC_TRIGGER, GPIO.OUT)
for pin in ALL_INPUT_PINS:
    GPIO.setup(pin, GPIO.IN)
GPIO.add_event_detect(ULTRASONIC_ECHO, GPIO.RISING, callback=on_echo_rising)
GPIO.add_event_detect(ULTRASONIC_ECHO, GPIO.FALLING, callback=on_echo_falling)


trigger = GPIO.PWM(ULTRASONIC_TRIGGER, 100)


trigger.start(50)


def infrared_sensors():
    return GPIO.input(LEFT_INFRARED_SENSOR), GPIO.input(RIGHT_INFRARED_SENSOR)


def track_detectors():
    return GPIO.input(LEFT_TRACK_DETECTOR), GPIO.input(MIDDLE_TRACK_DETECTOR), GPIO.input(RIGHT_TRACK_DETECTOR)


def ultrasonic_detector():
    return last_distance


__all__ = ['infrared_sensors', 'track_detectors', 'ultrasonic_detector']
