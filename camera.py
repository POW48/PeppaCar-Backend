import picamera
from threading import Thread
from subprocess import Popen, PIPE
from struct import Struct
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

    def __init__(self, ws_port=8081):
        super(CarCamera, self).__init__()
        self.width = 640
        self.height = 480
        self.frame_rate = 24

        self.stop = False

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

        self.converter = VideoConverter(self.camera)
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

    def run(self):
        self.camera.start_recording(self.converter, 'yuv')

        while not self.stop:
            self.camera.wait_recording(1)

        self.camera.stop_recording()

    def close(self):
        self.stop = True
        self.join()


class VideoConverter:
    def __init__(self, camera):
        print('Spawning background conversion process')
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

    def write(self, b):
        self.converter.stdin.write(b)

    def read(self, n):
        return self.converter.stdout.read1(n)

    def poll(self):
        return self.converter.poll()

    def flush(self):
        if not self.converter.stdin.closed:
            self.converter.stdin.close()
            self.converter.wait()