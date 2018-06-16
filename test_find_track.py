import message_queue as mq
from controller import Vehicle

import time

righttime = 0
lefttime = 0
find_track_flag = 0
car = Vehicle()
avoid_ob_flag = 0
on_this_avoid_ob = 0
def stop_queue():
    mq.stop()


def on_track(status):
    left, middle, right = status
    global find_track_flag
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

def avoid_ob(status):
    left, middle, right = status
    global avoid_ob_flag
    global on_this_avoid_ob
    if middle==0 and on_this_avoid_ob ==0:
        avoid_ob_flag = 1
        on_this_avoid_ob = 1
        mq.execute('turn-left')

        mq.timeout('go',100)

        mq.timeout('turn-right', 200)

        mq.timeout('go', 300)

        mq.timeout('turn-right', 400)

        mq.timeout('go', 500)

        mq.timeout('turn-left', 600)

        mq.timeout('stop',700)

        mq.timeout('change_avoid_flag', 700)
        mq.timeout('change_on_this_avoid_flag', 700)

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
mq.timeout('stop_queue', 3000)

# start the process
mq.start()
