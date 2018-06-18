import car
import scheduler



def simple_steer_track():
    def track_detector_callback(status):
        scheduler.cancel('avoid_ob')
        left, middle, right = status
        if left == 1 and middle == 0:
            rotate_left()
        if right == 1 and middle == 0:
            rotate_right()
        if middle == 1:
            go()
    on_track_detector_change(track_detector_callback)
    go()



if __name__ == '__main__':
    simple_steer_track()


