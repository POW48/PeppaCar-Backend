import car
import scheduler

track_flag =1

#1 nomorl find track
#2 return track
#3 nothing

def track_detector_callback(status):

    left, middle, right = status
    if track_flag==1:

        if left == 1 and middle == 0:
            car.rotate_left()
        if right == 1 and middle == 0:
            car.rotate_right()
        if middle == 1:
            car.go()

    elif track_flag==3:
        pass
    else:
        if middle==1:
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

    if middle==0:
        change_flag_nothing()

        scheduler.schedule('avoid_ob',(0,car.back),
          (10,car.rotate_left),
          (70,change_flag_return),
          (1,car.go),
          (70,car.rotate_right),
          (70,car.go))



if __name__ == '__main__':
    car.on_track_detector_change(track_detector_callback)
    car.on_infrared_sensor_change(simple_avoid_ob)
    car.go()
    scheduler.start()
    scheduler.schedule('stop',(2000,car.brake))



