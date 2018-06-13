import message_queue as mq
from controller import Vehicle

import time

righttime = 0
lefttime = 0
find_track_flag = 0
car = None


def stop_queue():
    mq.stop()


def on_track(status):
    left, middle, right = status
    global find_track_flag

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

find_track_flag = 1

def init(given_car):
    global car
    car = given_car
    # queue actions
    mq.task('stop_queue', stop_queue)
    # actions of car
    mq.task('go', car.move_forward)
    mq.task('back', car.move_backward)
    mq.task('stop', car.stop)
    mq.task('turn-left', car.turn_left)
    mq.task('turn-right', car.turn_right)
    # keep going until track detects
    mq.on('track', on_track)


def start_find_track():
    if not mq._is_running:
        mq.start()

def stop_find_track():
    global car
    if mq._is_running:
        mq.stop()

if __name__ == '__main__':
    init(Vehicle())
    mq.timeout('stop_queue', 3000)
    start_find_track()
