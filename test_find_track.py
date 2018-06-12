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
mq.timeout('turn-right', 100)
mq.timeout('stop', 200)
mq.timeout('stop_queue', 300)

mq.start()
mq.join()
