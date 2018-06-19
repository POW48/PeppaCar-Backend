import car
import scheduler

track_flag = 1
loaded = False


# 1 nomorl find track
# 2 return track
# 3 nothing

def track_detector_callback(status):
    left, middle, right = status
    if track_flag == 1:

        if left == 1 and middle == 0:
            car.rotate_left()
        if right == 1 and middle == 0:
            car.rotate_right()
        if middle == 1:
            car.go()

    elif track_flag == 3:
        pass
    else:
        if middle == 1:
            scheduler.cancel('avoid_ob')
            change_flag_normal()
            car.rotate_left()


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

def simple_avoid_ob_from_ultrasonic(status):
    print(status)
    if status<10:
        change_flag_nothing()
        car.back()
        scheduler.schedule('avoid_ob', (40, car.rotate_left),
                           (50, change_flag_return),
                           (1, car.go),
                           (125, car.rotate_right),
                           (60, car.go))


def load():
    global loaded
    # car.set_global_speed(5)
    if not loaded:
        car.on_track_detector_change(track_detector_callback)
        # car.on_infrared_sensor_change(simple_avoid_ob)
        car.on_ultrasonic_in_range(simple_avoid_ob_from_ultrasonic,0,10)
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
