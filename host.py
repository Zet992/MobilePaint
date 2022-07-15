# 1600 x 900
from random import random
import socket
import asyncio
import json
import logging

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.graphics import *


class Paint(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.update_canvas)
        self.bind(size=self.update_canvas)

        addr = ('', 8080)
        print(socket.gethostname())
        print(socket.gethostbyname(socket.gethostname()))
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind(addr)
        self.s.listen(1)
        self.conn, addr = self.s.accept()
        print('Connected by', addr)
        self.event = Clock.schedule_interval(self.receive_data, 1 / 24)

    def update_canvas(self, *args, pos=(5, 5), color=(1, 1, 1, 1), size=30):
        with self.canvas:
            Color(*color)
            Ellipse(size=(size, size), pos=pos)

    def on_touch_down(self, touch):
        self.update_canvas(pos=[touch.x - self.brush_size[0] // 2,
                                touch.y - self.brush_size[1] // 2])
        touch.grab(self)

    def on_touch_move(self, touch):
        self.update_canvas(pos=[touch.x - self.brush_size[0] // 2,
                                touch.y - self.brush_size[1] // 2])
        if touch.grab_current is self:
            return None

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            return None

    def receive_data(self, dt):
        try:
            data = self.conn.recv(1024)
            if not data:
                return
            points = data.split(b';')[:-1]
            for point in points:
                r, g, b, a, ra, x, y = map(float, point.split(b','))
                color = (float(r), float(g), float(b), float(a))
                self.update_canvas(pos=(x, y), color=color, size=int(ra))
        except ConnectionError:
            print('phone is unavailable')
            self.event.cancel()
            self.s.listen(1)
            self.conn, addr = self.s.accept()
            print('Connected by', addr)
            self.event = Clock.schedule_interval(self.receive_data, 1 / 30)

class PaintApp(App):
    def build(self):
        return Paint()


if __name__ == '__main__':
    PaintApp().run()
