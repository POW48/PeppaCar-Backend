from controller import Vehicle

if __name__ == '__main__':
    car = Vehicle()
    print('Move forward')
    car.move_forward()
    time.sleep(1.5)
    print('Move backward')
    car.move_backward()
    time.sleep(1.5)
    print('Turn left in place')
    car.turn_left()
    time.sleep(1.5)
    print('Turn right in place')
    car.turn_right()
    time.sleep(1.5)
