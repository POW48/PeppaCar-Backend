import picamera
from threading import Thread
from subprocess import Popen, PIPE
from struct import Struct
from test_camera import find_circle
import asyncio
import numpy
import json
import io
import os
from tornado import websocket, web, ioloop


class CarCamera(Thread):
    class VideoSocketHandler(websocket.WebSocketHandler):
        clients = []
        JSMPEG_MAGIC = b'jsmp'
        JSMPEG_HEADER = Struct('>4sHH')
        VFLIP = False
        HFLIP = False

        def check_origin(self, origin):
            return True

        def open(self):
            if self not in self.clients:
                self.clients.append(self)

            self.write_message(self.JSMPEG_HEADER.pack(self.JSMPEG_MAGIC, 640, 480), binary=True)

        def on_message(self, message):
            pass

        def on_close(self):
            if self in self.clients:
                self.clients.remove(self)

        @classmethod
        def broadcast(cls, data):
            for c in cls.clients:
                c.write_message(data, binary=True)

    def __init__(self, clients, ws_port=8081):
        super(CarCamera, self).__init__()
        self.width = 640
        self.height = 480
        self.frame_rate = 24

        self.stop = False
        self.capture = None
        self.converter = None
        self.broadcaster = None
        self.io_loop = None
        self.server_clients = clients

        self.camera = picamera.PiCamera()
        self.camera.resolution = (self.width, self.height)
        self.camera.framerate = self.frame_rate
        self.camera.vflip = False
        self.camera.hflip = False
        self.ws_port = ws_port
        self.ws_server = web.Application([
            (r'/', self.VideoSocketHandler),
        ])

    def run(self):
        self.io_loop = ioloop.IOLoop()
        self.ws_server.listen(self.ws_port)

        self.converter = VideoConverter(self.camera, self)
        self.capture = CaptureThread(self.camera, self.converter)
        self.broadcaster = BroadcastThread(self.converter, self.VideoSocketHandler, self.io_loop)

        print("Broadcast thread started.")
        self.io_loop.make_current()
        try:
            self.capture.start()
            self.broadcaster.start()

            self.io_loop.start()
        finally:
            print("Broadcast thread stopped.")
            self.converter.flush()

    def mark(self):
        if self.converter is not None:
            self.converter.mark()

    def origin(self):
        if self.converter is not None:
            self.converter.origin()

    def close(self):
        self.stop = True

        self.capture.close()
        self.converter.flush()
        self.join()


class BroadcastThread(Thread):
    def __init__(self, converter, socket_handler, io_loop):
        super(BroadcastThread, self).__init__()
        self.stop = False
        self.converter = converter
        self.socket_handler = socket_handler
        self.io_loop = io_loop

    def run(self):
        while not self.stop:
            buf = self.converter.read(32768)
            if buf:
                self.io_loop.add_callback(self.socket_handler.broadcast, buf)
            elif self.converter.poll() is not None:
                break

    def close(self):
        self.stop = True
        self.join()


class CaptureThread(Thread):
    def __init__(self, camera, converter):
        super(CaptureThread, self).__init__()
        self.camera = camera
        self.converter = converter
        self.stop = False
        self.markable = False

    def run(self):
        self.camera.start_recording(self.converter, 'yuv')

        while not self.stop:
            self.camera.wait_recording(1)

        self.camera.stop_recording()

    def close(self):
        self.stop = True
        self.join()


class VideoConverter:
    def __init__(self, camera, camcls):
        print('Spawning background conversion process')
        self.camera = camcls
        self.converter = Popen([
            'ffmpeg',
            '-f', 'rawvideo',
            '-pix_fmt', 'yuv420p',
            '-s', '%dx%d' % camera.resolution,
            '-r', str(float(camera.framerate)),
            '-i', '-',
            '-f', 'mpeg1video',
            '-b', '800k',
            '-r', str(float(camera.framerate)),
            '-'],
            stdin=PIPE, stdout=PIPE, stderr=io.open(os.devnull, 'wb'),
            shell=False, close_fds=True)
        self.markable = False

    def post_mark_image(self, b):
        y_frame = numpy.frombuffer(b, dtype=numpy.uint8, count=self.camera.width * self.camera.height).reshape(
            (self.camera.height, self.camera.width))
        u_frame = numpy.frombuffer(b, dtype=numpy.uint8,
                                   count=(self.camera.width // 2) * (self.camera.height // 2),
                                   offset=self.camera.width * self.camera.height).reshape(
            (self.camera.height // 2, self.camera.width // 2)).repeat(2, axis=0).repeat(2, axis=1)
        v_frame = numpy.frombuffer(b, dtype=numpy.uint8,
                                   count=(self.camera.width // 2) * (self.camera.height // 2),
                                   offset=(self.camera.width * self.camera.height) + (self.camera.width // 2) * (
                                       self.camera.height // 2)).reshape(
            (self.camera.height // 2, self.camera.width // 2)).repeat(2, axis=0).repeat(2, axis=1)
        yuv_file = numpy.dstack((y_frame, u_frame, v_frame))[:self.camera.height, :self.camera.width, :]
        yuv_file, bound = find_circle(yuv_file, 'yuv')
        self.camera.server_clients.put(json.dumps({'type': 'sensor', 'data': {'bound': bound}}))
        print(bound)

    def write(self, b):
        if self.markable:
            Thread(target=self.post_mark_image, args=[b]).run()
            self.converter.stdin.write(b)
        else:
            self.converter.stdin.write(b)

    def read(self, n):
        return self.converter.stdout.read1(n)

    def mark(self):
        self.markable = True

    def origin(self):
        self.markable = False

    def poll(self):
        return self.converter.poll()

    def flush(self):
        if not self.converter.stdin.closed:
            self.converter.stdin.close()
            self.converter.wait()
            pass
