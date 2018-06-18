import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.options
import os
import json
import controller
import sensor
import test_find_track as find_track
from camera import CarCamera
import queue
from tornado.web import RequestHandler
from tornado.options import define, options
from tornado.websocket import WebSocketHandler, WebSocketClosedError

define("port", default=8000, type=int)

car = controller.Vehicle()
camera = None
find_track.init(car)


class IndexHandler(RequestHandler):
    def get(self):
        self.render("index.html")


car_mode = 'user'
ws_reply = {}
ws_tasks = queue.Queue()


class ChatSocketHandler(WebSocketHandler):

    # 建立连接时调用，建立连接后将该websocket实例存入ChatSocketHandler.examples
    def open(self):
        print("WebSocket opened")

    # 收到web端消息时调用，接收到消息，使用实例发送消息
    def on_message(self, message):
        global car_mode
        print("WebSocket on_message ")
        print(message)
        message = json.loads(message)
        if message['mode'] == 'track':
            if car_mode == 'ball':
                print('Stop find ball')
                if camera is not None:
                    camera.origin()
            print('Start find track')
            car_mode = 'track'
            find_track.start_find_track()
        elif message['mode'] == 'ball':
            if car_mode == 'track':
                print('Stop find track')
                find_track.stop_find_track()
            print('Start find ball')
            car_mode = 'ball'
            if camera is not None:
                camera.mark()
        elif message['mode'] == 'user':
            if car_mode == 'track':
                print('Stop find track')
                find_track.stop_find_track()
            elif car_mode == 'ball':
                print('Stop find ball')
                if camera is not None:
                    camera.origin()
            car_mode = 'user'
            if message['speed'] == 0:
                car.stop()
            else:
                car.set_speed(message['speed'])
                if message['direction'] == 0:
                    car.move_forward()
                elif message['direction'] == 180:
                    car.move_backward()
                elif message['direction'] == 270:
                    car.turn_left()
                elif message['direction'] == 90:
                    car.turn_right()
        # Reply with status of sensors
        infrared = sensor.infrared_sensors()
        tracks = sensor.track_detectors()
        self.write_message(json.dumps({
            'type': 'sensor',
            'data': {
                'Left Infrared Sensor': infrared[0],
                'Middle Infrared Sensor': infrared[1],
                'Right Infrared Sensor': infrared[2],
                'Left Track Detector': tracks[0],
                'Middle Track Detector': tracks[1],
                'Right Track Detector': tracks[2],
                **ws_reply
            }
        }))

    # 断开连接时调用，断开连接后删除ChatSocketHandler.examples中的该实例
    def on_close(self):
        car.stop()
        print("WebSocket on_closed")

    # 403就加这个
    def check_origin(self, origin):
        return True

    # 用于发送消息到web端
    # def write_message(self, message, binary=False):
    #     if self.ws_connection is None:
    #         raise WebSocketClosedError()
    #     if isinstance(message, dict):
    #         message = tornado.escape.json_encode(message)
    #     self.ws_connection.write_message(message, binary=binary)

    # 主动关闭连接
    def close(self, code=None, reason=None):
        # if self.ws_connection:
        #     self.ws_connection.close(code, reason)
        #     self.ws_connection = None
        pass


def refresh_message():
    global ws_reply
    try:
        res = ws_tasks.get(False)
        ws_reply = res
    except queue.Empty:
        return


if __name__ == '__main__':
    tornado.options.parse_command_line()
    app = tornado.web.Application([
        (r"/", IndexHandler),
        (r"/chat", ChatSocketHandler),
    ],
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        debug=True
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    camera = CarCamera(ws_tasks)
    camera.start()
    print('start')
    loop = tornado.ioloop.IOLoop.current()
    loop.add_callback(refresh_message)
    loop.start()
