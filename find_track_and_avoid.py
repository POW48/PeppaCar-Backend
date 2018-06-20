import car
import time
import scheduler

track_flag = 1
loaded = False
last_rotate = 0
# 1 left
# 2 right
# 0 is nothing

avoid_flag = 0


# 1 nomorl find track
# 2 return track
# 3 nothing


# plan A
def track_detector_callback(status):
    global avoid_flag
    # plan A
    left, middle, right = status
    global last_rotate
    if track_flag == 1:
        if left == 1:
            last_rotate = 1
            # car.set_global_speed(1)
            car.rotate_left()
        elif right == 1:
            last_rotate = 2
            # car.set_global_speed(1)
            car.rotate_right()
        elif middle == 1:
            if last_rotate == 1:
                scheduler.schedule('buchang', (0, car.rotate_right), (5, car.go))
            if last_rotate == 2:
                scheduler.schedule('buchang', (0, car.rotate_left), (5, car.go))

            last_rotate = 0
            car.set_global_speed(10)
            car.go()

    elif track_flag == 3:
        pass
    else:
        if middle == 1:
            scheduler.cancel('avoid_ob')
            avoid_flag = 0
            change_flag_normal()
            recover_wheel_to_normal()
            car.rotate_left()
            print('refind road')

# # plan B
# def track_detector_callback(status):
#     global avoid_flag
#     _, left, right = status
#     global last_rotate
#     if track_flag == 1:
#         if left == 1:
#             last_rotate = 1
#             car.set_global_speed(1)
#             car.rotate_left()
#             time.sleep(0.05)
#             car.go()
#         elif right == 1:
#             last_rotate = 2
#             car.set_global_speed(1)
#             car.rotate_right()
#             time.sleep(0.05)
#             car.go()
#     elif track_flag == 3:
#         pass
#     else:
#         if left == 1:
#             scheduler.cancel('avoid_ob')
#             avoid_flag = 0
#             change_flag_normal()
#             recover_wheel_to_normal()
#             car.rotate_left()
#             print('refind road')


def change_flag_normal():
    global track_flag
    track_flag = 1


def change_flag_nothing():
    global track_flag
    track_flag = 3


def change_flag_return():
    global track_flag
    track_flag = 2


def simple_avoid_ob(status):
    left, middle, right = status

    print(middle)

    if middle == 0:
        change_flag_nothing()
        car.back()

        scheduler.schedule('avoid_ob', (80, car.rotate_left),
                           (100, change_flag_return),
                           (1, car.go),
                           (250, car.rotate_right),
                           (160, car.go))


def set_wheel_to_rotate():
    car.set_left_wheels_speed(10)
    car.set_right_wheels_speed(4)


def recover_wheel_to_normal():
    car.set_left_wheels_speed(10)
    car.set_right_wheels_speed(10)


def simple_avoid_ob_from_ultrasonic(status):
    print(status)
    global avoid_flag
    if status <= 25 and avoid_flag == 0:
        scheduler.cancel('avoid_ob')
        avoid_flag = 1
        change_flag_nothing()
        car.back()
        print('start avoid')
        # scheduler.schedule('avoid_ob', (10, car.rotate_left),
        #                    (45, car.go),
        #                    (1, change_flag_return),
        #                    (120, car.rotate_right),
        #                    (55, car.go))
        scheduler.schedule('avoid_ob', (10, car.rotate_left_90),
                           (0, set_wheel_to_rotate),
                           (0, car.go),
                           (10, change_flag_return))


def load():
    global loaded, avoid_flag, track_flag, last_rotate
    # car.set_global_speed(5)
    avoid_flag = 0
    track_flag = 1
    last_rotate = 0
    if not loaded:
        car.on_track_detector_change(track_detector_callback)
        # car.on_infrared_sensor_change(simple_avoid_ob)
        car.on_ultrasonic_in_range(simple_avoid_ob_from_ultrasonic, 0, 25)
        scheduler.start()
    loaded = True


def unload():
    global loaded
    if loaded:
        car.remove_track_detector_callback(track_detector_callback)
        # car.remove_infrared_sensor_change(simple_avoid_ob)
        car.remove_ultrasonic_callback(simple_avoid_ob_from_ultrasonic)
        scheduler.stop()
    loaded = False


if __name__ == '__main__':
    load()
    car.go()
    scheduler.start()
    # scheduler.schedule('stop',(2000,car.brake))
