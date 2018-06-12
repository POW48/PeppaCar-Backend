import RPi.GPIO as GPIO
import time

__all__ = ['Vehicle']

ENA = 11
IN1 = 13
IN2 = 15
IN3 = 19
IN4 = 21
ENB = 23
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
        self.left_wheels.move_backward()
        self.right_wheels.move_backward()

    def move_backward(self):
        self.left_wheels.move_forward()
        self.right_wheels.move_forward()

    def set_speed(self, speed: int):
        speed = max(0, min(10, speed))
        self.ENA_pwm.ChangeDutyCycle(speed * 5 + 50)
        self.ENB_pwm.ChangeDutyCycle(speed * 5 + 50)

    def turn_left(self):
        self.left_wheels.move_forward()
        self.right_wheels.move_backward()

    def turn_right(self):
        self.left_wheels.move_backward()
        self.right_wheels.move_forward()

    def stop(self):
        self.left_wheels.stop()
        self.right_wheels.stop()


if __name__ == '__main__':
    car = Vehicle()
    for i in range(10):
        print('- At speed %d:' % (i + 1))
        car.set_speed(i + 1)
        print('Move forward')
        car.move_forward()
        time.sleep(1)
        print('Move backward')
        car.move_backward()
        time.sleep(1)
    car.stop()
