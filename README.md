# 小車（jū）佩奇后端

## 事件队列

在自动化任务（例如循线避障和推球入门中）中，消息队列负责控制整个过程。消息队列每隔 10 毫秒会查询传感器状态，并根据传感器状态触发相应事件。

你可以通过 `task` 函数，注册一个新的任务。

```python
import message_queue as mq


def stop_car():
    car.stop()


def move_forward_car():
    car.move_forward()


mq.task('stop', stop_car)
mq.task('run', move_forward_car)
```

然后用 `execute` 执行这个任务。

```python
mq.execute('run')
```

你可以设定每隔几个间隔，就执行某个任务。

```python
mq.routine('run_every_100ms', 'run', 10)
```

如果你觉得这个任务不需要定时执行了，使用 `cancel` 函数取消定时任务。

```python
mq.cancel('run_every_100ms')
```

如果你希望在一定时间后执行某个任务，你需要 `timeout` 函数。例如在 100 个时间间隔后停止小车运行。

```python
mq.timeout('stop', 100)
```

### 事件

除了任务，我们还有事件的概念。你可以设定在某个事件发生后执行特定的任务。

```python
def on_sensor_change(status):
    left, middle, right = status.track_detectors
    if left == 1:
        mq.execute('turn-left')
    elif right == 1:
        mq.execute('turn-right')
    elif middle == 1:
        mq.execute(')


mq.on('sensor-change', )
```

### 开始与启动

调用 `start` 函数以启动，调用 `stop` 函数以停止。

```python
mq.start()
mq.stop()
```