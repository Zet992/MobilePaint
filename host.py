from random import random
import asyncio
import json
import socket

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.graphics import *
from kivy.logger import Logger

from kivy.core.window import Window


class Paint(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.update_canvas)
        self.bind(size=self.update_canvas)
        self.prev_pos = None
        self.k = 1

    def update_canvas(self, *args, pos=(5, 5), color=(1, 1, 1, 1), size=30,
                      line=False):
        if self.prev_pos is None and pos == (5, 5):
            return
        with self.canvas:
            Color(*color)
            size = size * self.k
            pos = (pos[0] * self.k, pos[1] * self.k)
            Ellipse(size=(size, size), pos=pos)
            line_point = (pos[0] + size // 2, pos[1] + size // 2)
            if line and self.prev_pos:
                Line(points=(*self.prev_pos, *line_point), width=size)
            self.prev_pos = line_point


class PaintApp(App):
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        Window.size = (576, 720)

    def build(self):
        return Paint()

    def app_func(self):
        self.other_task1 = asyncio.ensure_future(self.start_server())

        async def run_wrapper():
            await self.async_run(async_lib='asyncio')
            self.other_task1.cancel()

        return asyncio.gather(run_wrapper(), self.other_task1)

    async def start_server(self):
        addr = (socket.getfqdn(), 8080)
        self.server = await asyncio.start_server(self.open_connection, *addr)
        addrs = ', '.join(str(sock.getsockname()) for sock in self.server.sockets)
        print(f"Serving on {addrs}")
        try:
            async with self.server:
                await self.server.serve_forever()
        except asyncio.CancelledError as e:
            Logger.info("Server was canceled")
        finally:
            Logger.info("Server is disabled")

    async def open_connection(self, reader, writer):
        Logger.info('User connected')
        self.writer, self.reader = writer, reader
        try:
            data = await self.reader.read(1024)
            ph_width, ph_height, ph_dp = map(float, data.split(b','))
            self.root.k = Window.height / ph_height
            Logger.info(f'Size of window: {Window.size}')
            Logger.info(f'Size of phone: ({ph_width}, {ph_height})')
            Logger.info(f'Coefficient is {self.root.k}')
        except ConnectionError:
            Logger.warning('Phone is unavailable')
        except Exception as e:
            msg = 'Receiving data failed: ' + str(e) + 'receiving data ' + phone_res
            Logger.warning(msg)
        await asyncio.gather(self.receive_data())

    async def receive_data(self):
        try:
            while True:
                data = await self.reader.read(1024)
                if not data:
                    return
                commands = data.split(b';')[:-1]
                for command in commands:
                    if command == b'clear':
                        self.root.canvas.clear()
                        Logger.debug('Canvas is cleared')
                    else:
                        values = command.split(b',')
                        r, g, b, a, ra, x, y = map(float, values[:-1])
                        line = bool(int(values[-1]))
                        color = (r, g, b, a)
                        self.root.update_canvas(pos=(x, y), color=color,
                                                size=int(ra), line=line)
        except ConnectionError:
            Logger.warning('Phone is unavailable')
        except Exception as e:
            msg = 'Receiving data failed: ' + str(e) + ' received data ' + str(data)
            Logger.warning(msg)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(PaintApp().app_func())
    loop.close()
