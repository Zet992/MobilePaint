# 1600 x 900
from random import random
import socket
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

        self.brush_size = [50, 50]

        addr = ('', 8080)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(addr)
        s.listen(1)
        conn, addr = s.accept()
        print('Connected by', addr)
        while True:
            data = conn.recv(1024)
            if data:
                print(data)

    def update_canvas(self, *args, pos=(5, 5)):
        with self.canvas:
            Color(random(), random(), random(), random())
            Ellipse(size=self.brush_size, pos=pos)

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


class PaintApp(App):
    def build(self):
        return Paint()


if __name__ == '__main__':
    PaintApp().run()
