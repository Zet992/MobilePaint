# 1600 x 900
from random import random
import asyncio
import json
import socket

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.graphics import *
from kivy.logger import Logger


class Paint(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.update_canvas)
        self.bind(size=self.update_canvas)

    def update_canvas(self, *args, pos=(5, 5), color=(1, 1, 1, 1), size=30):
        with self.canvas:
            Color(*color)
            Ellipse(size=(size, size), pos=pos)


class PaintApp(App):
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)

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
        await asyncio.gather(self.receive_data())

    async def receive_data(self):
        try:
            while True:
                data = await self.reader.read(1024)
                if not data:
                    return
                points = data.split(b';')[:-1]
                for point in points:
                    r, g, b, a, ra, x, y = map(float, point.split(b','))
                    color = (float(r), float(g), float(b), float(a))
                    self.root.update_canvas(pos=(x, y), color=color, size=int(ra))
        except ConnectionError:
            Logger.warning('Phone is unavailable')
        except Exception as e:
            Logger.warning('Receiving data failed: ' + str(e) + 'received data ' + data)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(PaintApp().app_func())
    loop.close()
