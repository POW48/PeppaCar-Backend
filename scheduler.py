import heapq
import threading
import time

_tasks_to_remove = set()
_pending_tasks = []
_tick_counter = 0
_should_stop = False


def _executer_thread_main():
    global _pending_tasks, _tick_counter, _should_stop, _executer_thread
    while not _should_stop:
        while len(_pending_tasks) > 0 and _pending_tasks[0][0] == _tick_counter:
            _, name, tasks, index = heapq.heappop(_pending_tasks)
            tasks[index][1]()
            index += 1
            if index < len(tasks) and name not in _tasks_to_remove:
                heapq.heappush(_pending_tasks, (_tick_counter + tasks[index][0], name, tasks, index))
        if len(_tasks_to_remove) > 0:
            _tasks_to_remove.clear()
        _tick_counter += 1
        time.sleep(0.005)
    # reset
    _pending_tasks = []
    _tick_counter = 0
    _should_stop = False
    _executer_thread = threading.Thread(target=_executer_thread_main)


_executer_thread = threading.Thread(target=_executer_thread_main)


def schedule(name, *args):
    heapq.heappush(_pending_tasks, (_tick_counter + args[0][0], name, args, 0))


def cancel(name):
    _tasks_to_remove.add(name)


def start():
    _executer_thread.start()


def stop():
    global _should_stop
    _should_stop = True


def join():
    _executer_thread.join()


if __name__ == '__main__':
    def print_1():
        print(1)


    def print_2():
        print(2)


    def print_3():
        print(3)


    def cancel_myself():
        cancel('test')


    schedule('test', (100, print_1), (100, print_2), (100, cancel_myself), (100, print_3))
    start()
