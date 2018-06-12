import message_queue as mq
from controller import Vehicle


car = Vehicle()


def stop_queue():
    mq.stop()


# queue actions
mq.task('stop_queue', stop_queue)

# actions of car
mq.task('go', car.move_forward)
mq.task('back', car.move_backward)
mq.task('stop', car.stop)
mq.task('turn-left', car.turn_left)
mq.task('turn-right', car.turn_right)

# keep going until track detects
mq.execute('go')
mq.on('track', 'stop')

# stop car after 3 seconds
mq.timeout('stop_queue', 300)

# start the process
mq.start()
