import time

from RPi import GPIO

LEFT_TRACK_DETECTOR = 19
MIDDLE_TRACK_DETECTOR = 21
RIGHT_TRACK_DETECTOR = 23
LEFT_INFRARED_SENSOR = 29
MIDDLE_INFRARED_SENSOR = 32
RIGHT_INFRARED_SENSOR = 31
ALL_INPUT_PINS = [
    LEFT_TRACK_DETECTOR,
    MIDDLE_TRACK_DETECTOR,
    RIGHT_TRACK_DETECTOR,
    LEFT_INFRARED_SENSOR,
    MIDDLE_INFRARED_SENSOR,
    RIGHT_INFRARED_SENSOR,
]


GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
for pin in ALL_INPUT_PINS:
    GPIO.setup(pin, GPIO.IN)


def infrared_sensors():
    return GPIO.input(LEFT_INFRARED_SENSOR), GPIO.input(MIDDLE_INFRARED_SENSOR), GPIO.input(RIGHT_INFRARED_SENSOR)


def track_detectors():
    return GPIO.input(LEFT_TRACK_DETECTOR), GPIO.input(MIDDLE_TRACK_DETECTOR), GPIO.input(RIGHT_TRACK_DETECTOR)


def ultrasonic_detector():
    raise RuntimeError('Ultrasonic sensor detector is not implemented.')


__all__ = ['infrared_sensors', 'track_detectors', 'ultrasonic_detector']
