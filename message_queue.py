import collections
import threading
import time

import sensor


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

_last_sensor_status = dict()
_sensors = [['infra', sensor.infrared_sensors],
            ['track', sensor.track_detectors]]


def on(event_name, task_name_or_func):
    if event_name in _events:
        _events[event_name].append(task_name_or_func)
    else:
        _events[event_name] = [task_name_or_func]


def trigger(name, *args, **kwargs):
    if name in _events:
        for handler in _events[name]:
            if callable(handler):
                handler(*args, **kwargs)
            elif type(handler) == str:
                execute(handler)
            else:
                print('Warning: event "{}" is not a callable object or task name')


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


def loop_body():
    global _end_loop
    global _is_running
    global _queue
    global _thread
    _is_running = True
    while not _end_loop:
        # check status of sensors
        for sensor_name, sensor_getter in _sensors:
            new_status = sensor_getter()
            if _last_sensor_status.get(sensor_name) != new_status:
                trigger(sensor_name, new_status)
                _last_sensor_status[sensor_name] = new_status
        # execute all routines
        for item in _queue:
            item.remaining_cycle -= 1
            if item.remaining_cycle == 0:
                execute(item.task_name)
                if item.once:
                    item.to_be_remove = True
                item.remaining_cycle = item.interval
        _queue = collections.deque(
            filter(lambda x: not x.to_be_remove, _queue))
        time.sleep(_MESSAGE_QUEUE_TICK)
    _end_loop = False
    _is_running = False
    _thread = threading.Thread(target=loop_body)


_thread = threading.Thread(target=loop_body)


def stop():
    global _end_loop
    _end_loop = True


def start():
    if _thread.is_alive():
        print('Warning: message queue is already running.')
    else:
        _thread.start()

def join():
    if _thread.is_alive():
        _thread.join()
