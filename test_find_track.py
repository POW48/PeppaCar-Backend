import message_queue as mq
from controller import Vehicle

import time

righttime = 0
lefttime = 0
find_track_flag = 0
car = None
avoid_ob_flag = 0
on_this_avoid_ob = 0
adjust_flag = 0



def stop_queue():
    mq.stop()


def on_track(status):
    left, middle, right = status
    global find_track_flag
    global adjust_flag
    if avoid_ob_flag==0:
        if find_track_flag == 1:

            if left == 1:
                mq.execute('turn-left')

            if middle == 1:
                mq.execute('go')
                find_track_flag = 0

        else:
            if left == 1 and middle==0:
                mq.execute('turn-left')
            if right == 1 and middle==0:
                mq.execute('turn-right')
            if middle==1:
                mq.execute('go')
    elif adjust_flag ==1:
        print('adujust')
        if left == 1 and middle==0:
            mq.execute('turn-left')
        if right == 1 and middle==0:
            mq.execute('turn-right')
        if middle==1:
            mq.execute('stop')
            adjust_flag ==0

a=[0]*100
timeout = 80
a[0] = 0
for i in range(1,50):
    a[i] = a[i-1]+timeout


def avoid_ob(status):
    left, middle, right = status
    global avoid_ob_flag
    global on_this_avoid_ob
    global adjust_flag

    if middle==0 and on_this_avoid_ob ==0:

        # if adjust_flag ==1:
        #     mq.execute('turn-left')

        avoid_ob_flag = 1
        on_this_avoid_ob = 1

        mq.execute('stop')

        mq.timeout('back',20)

        mq.timeout('turn-left',50)

        mq.timeout('go',80)

        mq.timeout('turn-right',200 )

        mq.timeout('go',300)

        mq.timeout('turn-right', 400)

        mq.timeout('go',500 )

        mq.timeout('turn-left',600 )

        mq.timeout('stop',680)


        mq.timeout('change_on_this_avoid_flag', 680)

        mq.timeout('go',700)

def change_on_this_avoid_flag ():
    global avoid_ob_flag
    global on_this_avoid_ob
    avoid_ob_flag = 0
    on_this_avoid_ob = 0
find_track_flag = 1


def init(given_car):
    global car
    car = given_car
    # queue actions
    mq.task('stop_queue', stop_queue)
    # actions of car
    mq.task('change_on_this_avoid_flag',change_on_this_avoid_flag)

    mq.task('go', car.move_forward)
    mq.task('back', car.move_backward)
    mq.task('stop', car.stop)
    mq.task('turn-left', car.turn_left)
    mq.task('turn-right', car.turn_right)
    # keep going until track detects
    mq.on('track', on_track)
    mq.on('infra',avoid_ob)

def start_find_track():
    if not mq._is_running:
        mq.start()

def stop_find_track():
    global car
    if mq._is_running:
        mq.stop()

if __name__ == '__main__':
    init(Vehicle())
    mq.timeout('stop_queue', 1500)
    start_find_track()
