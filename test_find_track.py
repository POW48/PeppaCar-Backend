import message_queue as mq
from controller import Vehicle

import time

righttime = 0
lefttime = 0
find_track_flag = 0
car = Vehicle()


def stop_queue():
    mq.stop()


def on_track(status):
    left, middle, right = status
    global find_track_flag

    if find_track_flag == 1:

        if left == 1:
            mq.execute('turn-left')
            lefttime = time.time()
        if middle == 1:
            mq.stop()
            find_track_flag = 0


# queue actions
mq.task('stop_queue', stop_queue)


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

# stop car after 3 seconds
mq.timeout('stop_queue', 300)

# start the process
mq.start()
