import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.options
import os
import json
import controller
from tornado.web import RequestHandler
from tornado.options import define, options
from tornado.websocket import WebSocketHandler, WebSocketClosedError

define("port", default=8000, type=int)

car = controller.Vehicle()


class IndexHandler(RequestHandler):
    def get(self):
        self.render("index.html")


class ChatSocketHandler(WebSocketHandler):

    # 建立连接时调用，建立连接后将该websocket实例存入ChatSocketHandler.examples
    def open(self):
        print("WebSocket opened")

    # 收到web端消息时调用，接收到消息，使用实例发送消息
    def on_message(self, message):
        print("WebSocket on_message ")
        print(message)
        controlmand = json.loads(message)
        if controlmand['speed'] == 0:
            car.stop()
        else:
            car.set_speed(controlmand['speed'])
            if controlmand['direction'] == 0:
                car.move_forward()
            elif controlmand['direction'] == 180:
                car.move_backward()
            elif controlmand['direction'] == 270:
                car.turn_left()
            elif controlmand['direction'] == 90:
                car.turn_right()

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
    print('start')
    tornado.ioloop.IOLoop.current().start()
