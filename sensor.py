from RPi import GPIO


LEFT_TRACK_DETECTOR = 29
MIDDLE_TRACK_DETECTOR = 31
RIGHT_TRACK_DETECTOR = 33
LEFT_INFRARED_SENSOR = 35
RIGHT_INFRARED_SENSOR = 37
ALL_PINS = [
    LEFT_TRACK_DETECTOR,
    MIDDLE_TRACK_DETECTOR,
    RIGHT_TRACK_DETECTOR,
    LEFT_INFRARED_SENSOR,
    RIGHT_INFRARED_SENSOR
]

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
for pin in ALL_PINS:
    GPIO.setup(pin, GPIO.IN)


def infrared_sensors(self):
    return GPIO.input(LEFT_INFRARED_SENSOR), GPIO.input(RIGHT_INFRARED_SENSOR)


def track_detectors():
    return GPIO.input(LEFT_TRACK_DETECTOR), GPIO.input(MIDDLE_TRACK_DETECTOR), GPIO.input(RIGHT_TRACK_DETECTOR)


def ultrasonic_detector():
    raise Exception('not implemented')


__all__ = ['infrared_sensors', 'track_detectors']
