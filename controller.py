import RPi.GPIO as GPIO

__all__ = ['Vehicle']

#        3V3  (1) (2)  5V
#      GPIO2  (3) (4)  5V
#      GPIO3  (5) (6)  GND
#      GPIO4  (7) (8)  GPIO14
#        GND  (9) (10) GPIO15
#     GPIO17 (11) (12) GPIO18
#     GPIO27 (13) (14) GND
#     GPIO22 (15) (16) GPIO23
#        3V3 (17) (18) GPIO24
#     GPIO10 (19) (20) GND
#      GPIO9 (21) (22) GPIO25
#     GPIO11 (23) (24) GPIO8
#        GND (25) (26) GPIO7
#      GPIO0 (27) (28) GPIO1
#      GPIO5 (29) (30) GND
#      GPIO6 (31) (32) GPIO12
# IN2 GPIO13 (33) (34) GND
# IN1 GPIO19 (35) (36) GPIO16 IN3
# ENA GPIO26 (37) (38) GPIO20 IN4
#        GND (39) (40) GPIO21 ENB


ENA = 37
IN1 = 35
IN2 = 33
IN3 = 36
IN4 = 38
ENB = 40
ALL_PINS = [ENA, IN1, IN2, IN3, IN4, ENB]


class Wheels:
    def __init__(self, enabler, input1, input2):
        self.enabler = enabler
        self.input1 = input1
        self.input2 = input2
        self.stop()
        self.enable()

    def enable(self):
        GPIO.output(self.enabler, GPIO.HIGH)

    def disable(self):
        GPIO.output(self.enabler, GPIO.LOW)

    def stop(self):
        GPIO.output(self.input1, GPIO.LOW)
        GPIO.output(self.input2, GPIO.LOW)

    def move_backward(self):
        GPIO.output(self.input1, GPIO.LOW)
        GPIO.output(self.input2, GPIO.HIGH)

    def move_forward(self):
        GPIO.output(self.input1, GPIO.HIGH)
        GPIO.output(self.input2, GPIO.LOW)


class Vehicle:
    def __init__(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        for pin in ALL_PINS:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)
        self.ENA_pwm = GPIO.PWM(ENA, 500)
        self.ENA_pwm.start(100)
        self.ENB_pwm = GPIO.PWM(ENB, 500)
        self.ENB_pwm.start(100)
        self.left_wheels = Wheels(ENA, IN1, IN2)
        self.right_wheels = Wheels(ENB, IN3, IN4)

    def move_forward(self):
        self.left_wheels.move_forward()
        self.right_wheels.move_backward()

    def move_backward(self):
        self.left_wheels.move_backward()
        self.right_wheels.move_forward()

    def set_speed(self, speed: int):
        speed = max(0, min(10, speed))
        self.ENA_pwm.ChangeDutyCycle(speed * 5 + 50)
        self.ENB_pwm.ChangeDutyCycle(speed * 5 + 50)

    def turn_left(self):
        self.left_wheels.move_backward()
        self.right_wheels.move_backward()

    def turn_right(self):
        self.left_wheels.move_forward()
        self.right_wheels.move_forward()

    def stop(self):
        self.left_wheels.stop()
        self.right_wheels.stop()
