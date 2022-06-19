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
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.stencilview import StencilView
from kivy.uix.screenmanager import ScreenManager, Screen

from kivy.core.window import Window


r = 10
color = [1, 1, 1, 1]
conn_socket = None


class MenuScreen(Screen):
    pass


class SettingsScreen(Screen):
    pass


class Paint(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.bind(pos=self.update_canvas)
        self.bind(size=self.update_canvas)

        self.prev_pos = None

        with self.canvas.before:
            Color(1, 1, 1, mode='rgb')
            Line(points=(0, 145, Window.width, 145))

    def update_canvas(self, *args, pos=(5, 5)):
        with self.canvas:
            pos = (int(pos[0]), int(pos[1]))
            Color(*color)
            Ellipse(size=(r, r), pos=pos)
            line_point = (pos[0] + r // 2, pos[1] + r // 2)
            if self.prev_pos:
                Line(points=(*self.prev_pos, *line_point), width=r)
            if pos != (5, 5):
                self.prev_pos = line_point
        if conn_socket:
            try:
                data = ",".join(map(str, list(color) + [r] + list(pos))) + ';'
                conn_socket.sendall(bytes(data, encoding='utf-8'))
                print('data is sent')
            except ConnectionError:
                print('computer is unavailable')

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
        self.sm = ScreenManager()

        menu = MenuScreen(name='menu')
        self.painter = Paint()
        stencil_layout = BoxStencil(cols=1, width=Window.width,
                                    height=Window.height-145)
        stencil_layout.set_top(Window.height)
        stencil_layout.add_widget(self.painter)
        menu.add_widget(stencil_layout)

        menu_layout = GridLayout(rows=1, row_default_height=135,
                                 row_force_default=True)
        menu_layout.set_top(240 - Window.height)

        clear_btn = Button(text="Clear")
        clear_btn.bind(on_release=self.clear_canvas)
        menu_layout.add_widget(clear_btn)

        settings_btn = Button(text='Settings')
        settings_btn.bind(on_press=self.go_to_settings)
        menu_layout.add_widget(settings_btn)

        connection_btn = Button(text='Connection')
        connection_btn.bind(on_press=self.go_to_conn_screen)
        menu_layout.add_widget(connection_btn)

        menu.add_widget(menu_layout)
        self.sm.add_widget(menu)

        settings = SettingsScreen(name='settings')
        grid_layout = GridLayout(rows=1, row_default_height=500,
                                 row_force_default=True)
        grid_layout.set_top(55)
        text_layout = GridLayout(rows=1)
        text_layout.set_top(-150)

        color_r = Slider(min=0, max=100, value=100, orientation='vertical',
                         value_track=True, value_track_color=[1, 0, 0, 1])
        color_r.bind(value_normalized=self.change_r)
        color_g = Slider(min=0, max=100, value=100, orientation='vertical',
                         value_track=True, value_track_color=[0, 1, 0, 1])
        color_g.bind(value_normalized=self.change_g)
        color_b = Slider(min=0, max=100, value=100, orientation='vertical',
                         value_track=True, value_track_color=[0, 0, 1, 1])
        color_b.bind(value_normalized=self.change_b)
        color_a = Slider(min=0, max=100, value=100, orientation='vertical',
                         value_track=True)
        color_a.bind(value_normalized=self.change_a)
        point_r = Slider(min=1, max=25, value=10, orientation='vertical',
                         value_track=True)
        point_r.bind(value=self.change_ra)

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
        text_layout.add_widget(Label(text=''))

        menu_btn = Button(text='Back')
        menu_btn.bind(on_press=self.go_to_menu)
        grid_layout.add_widget(menu_btn)

        settings.add_widget(grid_layout)
        settings.add_widget(text_layout)
        self.sm.add_widget(settings)

        conn_screen = Screen(name='conn')
        conn_layout = BoxLayout(orientation='vertical')

        self.address_input = TextInput(multiline=False)
        conn_layout.add_widget(self.address_input)

        connect_btn = Button(text='Connect')
        connect_btn.bind(on_press=self.change_address)
        conn_layout.add_widget(connect_btn)

        menu_btn2 = Button(text='Back')
        menu_btn2.bind(on_press=self.go_to_menu)
        conn_layout.add_widget(menu_btn2)

        conn_screen.add_widget(conn_layout)
        self.sm.add_widget(conn_screen)

        self.draw_color_circle()

        return self.sm

    def clear_canvas(self, obj):
        self.painter.canvas.clear()

    def change_r(self, obj, value):
        self.draw_color_circle()
        color[0] = value

    def change_g(self, obj, value):
        self.draw_color_circle()
        color[1] = value

    def change_b(self, obj, value):
        self.draw_color_circle()
        color[2] = value

    def change_a(self, obj, value):
        self.draw_color_circle()
        color[3] = value

    def change_ra(self, obj, value):
        global r
        self.draw_color_circle()
        r = value

    def change_address(self, obj):
        global conn_socket
        conn_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn_socket.connect((self.address_input.text, 8080))
        print('connection is successful')

    def draw_color_circle(self):
        with self.sm.get_screen('settings').canvas:
            Color(*color)
            Ellipse(pos=(0, Window.height - 50), size=(50, 50))

    def go_to_settings(self, obj):
        self.sm.transition.direction = 'left'
        self.sm.current = 'settings'

    def go_to_menu(self, obj):
        self.sm.transition.direction = 'right'
        self.sm.current = 'menu'

    def go_to_conn_screen(self, obj):
        self.sm.transition.direction = 'left'
        self.sm.current = 'conn'


class BoxStencil(GridLayout, StencilView):
    pass


if __name__ == '__main__':
    PaintApp().run()
