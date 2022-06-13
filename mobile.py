# 720 x 1280
import socket
import json
import logging
from random import random
import re

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.graphics import *

from kivy.uix.gridlayout import GridLayout
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.stencilview import StencilView

from kivy.core.window import Window


r = 10
color = [1, 1, 1, 1]


class Paint(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.bind(pos=self.update_canvas)
        self.bind(size=self.update_canvas)

        self.prev_pos = None

        with self.canvas.before:
            Color(1, 1, 1, mode='rgb')
            Line(points=(0, 145, Window.width, 145))

        # addr = ('127.0.0.1', 8080)
        # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # s.connect(addr)
        # s.sendall(bytes('information', encoding='utf-8'))

    def update_canvas(self, *args, pos=(5, 5)):
        with self.canvas:
            Color(*color)
            Ellipse(size=(r, r), pos=pos)
            if self.prev_pos and self.prev_pos != (5, 5):
                Line(points=(*self.prev_pos, *pos), width=r)
            self.prev_pos = pos

    def on_touch_down(self, touch):
        self.update_canvas(pos=[touch.x - r // 2,
                                touch.y - r // 2])
        touch.grab(self)

    def on_touch_move(self, touch):
        self.update_canvas(pos=[touch.x - r // 2,
                                touch.y - r // 2])
        if touch.grab_current is self:
            return None

    def on_touch_up(self, touch):
        self.prev_pos = None
        if touch.grab_current is self:
            touch.ungrab(self)
            return None


class PaintApp(App):
    def build(self):
        parent = Widget()

        self.painter = Paint()
        stencil_layout = BoxStencil(cols=1, width=Window.width, height=Window.height-145)
        stencil_layout.set_top(Window.height)
        stencil_layout.add_widget(self.painter)

        grid_layout = GridLayout(cols=5, row_default_height=100, width=300)
        grid_layout.set_top(125)
        text_layout = GridLayout(cols=5, width=300)
        text_layout.set_top(65)

        color_r = Slider(min=0, max=100, value=100, orientation='vertical',
                         value_track=True, value_track_color=[1, 0, 0, 1])
        color_r.bind(value_normalized=change_r)
        color_g = Slider(min=0, max=100, value=100, orientation='vertical',
                         value_track=True, value_track_color=[0, 1, 0, 1])
        color_g.bind(value_normalized=change_g)
        color_b = Slider(min=0, max=100, value=100, orientation='vertical',
                         value_track=True, value_track_color=[0, 0, 1, 1])
        color_b.bind(value_normalized=change_b)
        color_a = Slider(min=0, max=100, value=100, orientation='vertical',
                         value_track=True)
        color_a.bind(value_normalized=change_a)
        point_r = Slider(min=1, max=25, value=10, orientation='vertical',
                         value_track=True)
        point_r.bind(value=change_ra)

        clear_btn = Button(text="Clear")
        clear_btn.set_right(798)
        clear_btn.set_top(100)
        clear_btn.bind(on_release=self.clear_canvas)

        parent.add_widget(stencil_layout)
        grid_layout.add_widget(color_r)
        grid_layout.add_widget(color_g)
        grid_layout.add_widget(color_b)
        grid_layout.add_widget(color_a)
        grid_layout.add_widget(point_r)
        text_layout.add_widget(Label(text='R'))
        text_layout.add_widget(Label(text='G'))
        text_layout.add_widget(Label(text='B'))
        text_layout.add_widget(Label(text='A'))
        text_layout.add_widget(Label(text='Size'))
        parent.add_widget(grid_layout)
        parent.add_widget(text_layout)
        parent.add_widget(clear_btn)

        return parent

    def clear_canvas(self, obj):
        self.painter.canvas.clear()


class BoxStencil(GridLayout, StencilView):
    pass


def change_r(obj, value):
    color[0] = value


def change_g(obj, value):
    color[1] = value


def change_b(obj, value):
    color[2] = value


def change_a(obj, value):
    color[3] = value


def change_ra(obj, value):
    global r
    r = value


if __name__ == '__main__':
    PaintApp().run()
