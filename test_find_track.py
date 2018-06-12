import message_queue as mq
from controller import Vehicle


car = Vehicle()


def stop_queue():
    mq.stop()


mq.task('stop_queue', stop_queue)
mq.task('stop', car.stop)
mq.task('turn-left', car.turn_left)
mq.task('turn-right', car.turn_right)

mq.execute('turn-left')
mq.timeout('stop', 1000)
mq.timeout('stop_queue', 3000)

mq.start()
mq.join()
