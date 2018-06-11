import message_queue as mq


def say_hello():
    print('Hello!')

def stop_queue():
    mq.stop()

mq.task('say_hello', say_hello)
mq.task('stop', stop_queue)

mq.routine('say_hello', 'say_hello', 10)
mq.timeout('stop', 100)

mq.start()
