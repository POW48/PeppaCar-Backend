import threading
import time
import collections


class Routine:
    def __init__(self, name, task_name, interval, once=False):
        self.name = name
        self.task_name = task_name
        self.interval = interval
        self.remaining_cycle = self.interval
        self.once = once
        self.successors = []
        self.to_be_remove = False


_MESSAGE_QUEUE_FREQUENCY = 100
_MESSAGE_QUEUE_TICK = 1 / _MESSAGE_QUEUE_FREQUENCY
_queue = collections.deque()
_tasks = dict()
_routines = dict()
_events = dict()
_end_loop = False
_is_running = False


def task(name, func):
    if name in _tasks:
        print('Warning: try to override a existing task "{}"'.format(name))
    else:
        _tasks[name] = func


def execute(name, *args, **kwargs):
    if name in _tasks:
        func = _tasks.get(name)
        func(*args, **kwargs)
    else:
        print('Warning: try to execute a unknown task "{}"'.format(name))


def routine(name, task_name, interval):
    _queue.append(Routine(name, task_name, interval))


def timeout(task_name, interval):
    _queue.append(Routine(task_name, task_name, interval, once=True))


def stop():
    global _end_loop
    _end_loop = True


def on(event_name, task):
    _events[event_name].append(task)


def register(event_name):
    _events[event_name] = []


def trigger(event_name, *args, **kwargs):
    task_list = _events.get(event_name)
    for task in task_list:
        if callable(task):
            event(*args, **kwargs)
        else:
            execute(task, *args, **kwargs)


def loop_body():
    global _end_loop
    global _is_running
    global _queue
    _is_running = True
    while not _end_loop:
        # check status of sensors

        # execute all routines
        for item in _queue:
            item.remaining_cycle -= 1
            if item.remaining_cycle == 0:
                execute(item.task_name)
                if item.once:
                    item.to_be_remove = True
                item.remaining_cycle = item.interval
        _queue = collections.deque(filter(lambda x: not x.to_be_remove, _queue))
        time.sleep(_MESSAGE_QUEUE_TICK)
    _end_loop = False
    _is_running = False


_thread = threading.Thread(target=loop_body)


def start():
    if _thread.is_alive():
        print('Warning: message queue is already running.')
    else:
        _thread.start()
        _thread.join()
