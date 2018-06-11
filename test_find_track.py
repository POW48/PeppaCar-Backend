import threading
import time

import controller
import sensor

infrared_sensors = sensor.infrared_sensors()
track_detectors = sensor.track_detectors()
end_polling = False

POLLING_FREQUENCY = 100
POLLING_INTERVAL = 1 / POLLING_FREQUENCY


def polling_sensor():
    global infrared_sensors
    global track_detectors
    global end_polling
    print('Start polling')
    while not end_polling:
        last_track_detectors = track_detectors
        infrared_sensors = sensor.infrared_sensors()
        track_detectors = sensor.track_detectors()
        if track_detectors != last_track_detectors:
            print('{} -> {}'.format(last_track_detectors, track_detectors))
        time.sleep(POLLING_FREQUENCY)
    print('End polling')


if __name__ == '__main__':
    thread = threading.Thread(target=polling_sensor)
    thread.start()
    car = controller.Vehicle()
    car.move_forward()
    time.sleep(1)
    car.move_backward()
    time.sleep(1)
    end_polling = True
