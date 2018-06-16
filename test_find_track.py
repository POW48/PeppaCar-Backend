import message_queue as mq
from controller import Vehicle

import time

righttime = 0
lefttime = 0
find_track_flag = 0
car = Vehicle()
avoid_ob_flag = 0
on_this_avoid_ob = 0
adjust_flag = 1
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
    else if adjust_flag ==1:
            if left == 1 and middle==0:
                mq.execute('turn-left')
            if right == 1 and middle==0:
                mq.execute('turn-right')
            if middle==1:
                mq.execute('stop')
                adjust_flag ==0


def avoid_ob(status):
    left, middle, right = status
    global avoid_ob_flag
    global on_this_avoid_ob
    global adjust_flag

    if middle==0 and on_this_avoid_ob ==0:
        if adjust_flag ==1:
            mq.execute('turn-left')
        avoid_ob_flag = 1
        on_this_avoid_ob = 1

        mq.execute('turn-left',100)

        mq.timeout('go',200)

        mq.timeout('turn-right', 300)

        mq.timeout('go', 400)

        mq.timeout('turn-right', 500)

        mq.timeout('go', 600)

        mq.timeout('turn-left', 700)

        mq.timeout('stop',800)

        mq.timeout('change_avoid_flag', 800)
        mq.timeout('change_on_this_avoid_flag', 800)

def change_flag ():
    global avoid_ob_flag
    avoid_ob_flag = 0

def change_on_this_avoid_flag ():
    global on_this_avoid_ob
    on_this_avoid_ob = 0

# queue actions
mq.task('stop_queue', stop_queue)
mq.task('change_avoid_flag',change_flag)
mq.task('change_on_this_avoid_flag',change_on_this_avoid_flag)
# actions of car
mq.task('go', car.move_forward)
mq.task('back', car.move_backward)
mq.task('stop', car.stop)
mq.task('turn-left', car.turn_left)
mq.task('turn-right', car.turn_right)

# keep going until track detects


find_track_flag = 1
mq.execute('turn-right')
mq.on('track', on_track)
mq.on('infra',avoid_ob)

print('fajejfajf')
# stop car after 3 seconds
mq.timeout('stop_queue', 1500)

# start the process
mq.start()
