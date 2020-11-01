# -*- coding: Utf-8 -*

import socket
import select
import pygame
from typing import Type, Union
from my_pygame import Window, RectangleShape, Image, Button, ButtonListVertical, Scale, Text, CountDown, Entry
from my_pygame import GREEN, GREEN_DARK, GREEN_LIGHT, YELLOW
from my_pygame import BLACK, GREEN, GREEN_DARK, GREEN_LIGHT, YELLOW, TRANSPARENT
from constants import RESOURCES
from navy_setup import NavySetup

class PlayerServer(Window):
    def __init__(self, master):
        Window.__init__(self, master=master, bg_music=master.bg_music)
        params_for_all_buttons = {
            "font": ("calibri", 30),
            "bg": GREEN,
            "hover_bg": GREEN_LIGHT,
            "active_bg": GREEN_DARK,
            "outline": 3,
            "highlight_color": YELLOW
        }
        self.ip = socket.gethostbyname(socket.gethostname())
        self.port = 12800
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(("", self.port))
        self.socket.listen(1)
        self.frame = RectangleShape(0.5 * self.width, 0.5 * self.height, GREEN_DARK, outline=5)
        self.text_title = Text("Waiting for Player 2", ("calibri", 50))
        self.text_ip_address = Text(f"IP address: {self.ip}", ("calibri", 40))
        self.text_port_of_connection = Text(f"Port: {self.port}", ("calibri", 40))
        self.button_cancel = Button(self, "Return to menu", callback=self.stop, **params_for_all_buttons)
        self.lets_play_countdown = CountDown(self, 3, "Player 2 connected.\nGame start in {seconds} seconds", font=("calibri", 35), color=YELLOW, justify="center")

    def on_start_loop(self):
        self.check_incoming_connections()

    def on_quit(self):
        self.socket.close()

    def place_objects(self):
        self.frame.move(center=self.center)
        self.text_title.move(centerx=self.frame.centerx, top=self.frame.top + 50)
        self.lets_play_countdown.move(center=self.text_title.center)
        self.text_ip_address.move(centerx=self.centerx, bottom=self.frame.centery - 10)
        self.text_port_of_connection.move(centerx=self.text_ip_address.centerx, top=self.text_ip_address.bottom + 20)
        self.button_cancel.move(centerx=self.frame.centerx, bottom=self.frame.bottom - 10)

    def check_incoming_connections(self):
        socket_player = None
        try:
            connections = select.select([self.socket], [], [], 0.05)[0]
            if connections:
                socket_player = connections[0].accept()[0]
                self.text_title.hide()
                self.button_cancel.state = Button.DISABLED
                self.lets_play_countdown.start(at_end=lambda: self.play(socket_player))
        except (socket.error, ValueError, TypeError, OSError):
            pass
        else:
            if not isinstance(socket_player, socket.socket):
                self.after(10, self.check_incoming_connections)

    def play(self, socket_player: socket.socket):
        NavySetup(socket_player, 1).mainloop()
        self.stop()

class PlayerClient(Window):
    def __init__(self, master):
        Window.__init__(self, master=master, bg_music=master.bg_music)
        params_for_all_buttons = {
            "font": ("calibri", 30),
            "bg": GREEN,
            "hover_bg": GREEN_LIGHT,
            "active_bg": GREEN_DARK,
            "highlight_color": YELLOW,
            "outline": 3
        }
        self.frame = RectangleShape(0.5 * self.width, 0.5 * self.height, GREEN_DARK, outline=5)
        self.text_title = Text("Connect to Player 1", ("calibri", 50))
        self.ip = Entry(self, width=15, font=("calibri", 40), bg=GREEN, highlight_color=YELLOW, outline=2)
        self.text_ip_address = Text("IP address", ("calibri", 40), YELLOW)
        self.port = Entry(self, width=15, font=("calibri", 40), bg=GREEN, highlight_color=YELLOW, outline=2)
        self.text_port_of_connection = Text("Port", ("calibri", 40), YELLOW)
        self.text_connection = Text(font=("calibri", 25), color=YELLOW)
        self.text_connection.hide()
        self.button_connect = Button(self, "Connection", callback=self.connection, **params_for_all_buttons)
        self.button_cancel = Button(self, "Return to menu", callback=self.stop, **params_for_all_buttons)
        self.lets_play_countdown = CountDown(self, 3, "Connected.\nGame start in {seconds} seconds", font=("calibri", 35), color=YELLOW, justify="center")

    def on_quit(self):
        self.disable_text_input()

    def place_objects(self):
        self.frame.move(center=self.center)
        self.text_title.move(centerx=self.frame.centerx, top=self.frame.top + 50)
        self.lets_play_countdown.move(center=self.text_title.center)
        self.ip.move(centerx=self.frame.centerx + self.frame.w // 10, bottom=self.frame.centery - 10)
        self.text_ip_address.move(centery=self.ip.centery, right=self.ip.left - 10)
        self.port.move(left=self.ip.left, top=self.ip.bottom + 20)
        self.text_port_of_connection.move(centery=self.port.centery, right=self.port.left - 10)
        self.text_connection.move(centerx=self.frame.centerx, top=self.port.bottom + 5)
        self.button_connect.move(centerx=self.frame.centerx - (self.frame.width // 4), bottom=self.frame.bottom - 10)
        self.button_cancel.move(centerx=self.frame.centerx + (self.frame.width // 4), bottom=self.frame.bottom - 10)

    def connection(self):
        self.text_connection.show()
        self.text_connection.message = "Connection..."
        self.draw_and_refresh()
        try:
            socket_player = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_player.settimeout(3)
            socket_player.connect((self.ip.get(), int(self.port.get())))
        except (socket.error, OverflowError, ValueError):
            self.text_connection.message = "Connection failed. Try again."
        else:
            socket_player.settimeout(None)
            self.text_connection.hide()
            self.text_title.hide()
            self.button_connect.state = self.button_cancel.state = Button.DISABLED
            self.button_connect.focus_leave()
            self.lets_play_countdown.start(at_end=lambda: self.play(socket_player))

    def play(self, socket_player: socket.socket):
        NavySetup(socket_player, 2).mainloop()
        self.stop()

class Options(Window):
    def __init__(self, master):
        Window.__init__(self, master=master, bg_music=master.bg_music)
        self.frame = RectangleShape(0.5 * self.width, 0.5 * self.height, GREEN_DARK, outline=5)
        self.text_title = Text("Options", ("calibri", 50))
        params_for_all_scales = {
            "width": 0.45 * self.frame.w,
            "height": 30,
            "color": TRANSPARENT,
            "scale_color": GREEN,
            "from_": 0,
            "to": 100,
            "highlight_color": YELLOW,
            "outline": 3
        }
        params_for_all_buttons = {
            "font": ("calibri", 30),
            "bg": GREEN,
            "hover_bg": GREEN_LIGHT,
            "active_bg": GREEN_DARK,
            "highlight_color": params_for_all_scales["highlight_color"],
            "outline": params_for_all_scales["outline"]
        }
        self.scale_music = Scale(
            self, **params_for_all_scales,
            default=Window.music_volume() * 100,
            callback=lambda value, percent: Window.set_music_volume(percent)
        )
        self.scale_music.show_label("Music: ", Scale.S_LEFT, font=params_for_all_buttons["font"])
        self.scale_music.show_value(Scale.S_RIGHT, font=params_for_all_buttons["font"])
        self.scale_sound = Scale(
            self, **params_for_all_scales,
            default=Window.sound_volume() * 100,
            callback=lambda value, percent: Window.set_sound_volume(percent)
        )
        self.scale_sound.show_label("SFX: ", Scale.S_LEFT, font=params_for_all_buttons["font"])
        self.scale_sound.show_value(Scale.S_RIGHT, font=params_for_all_buttons["font"])
        self.button_cancel = Button(self, "Return to menu", callback=self.stop, **params_for_all_buttons)
        self.bind_key(pygame.K_ESCAPE, lambda event: self.stop())

    def place_objects(self):
        self.frame.center = self.center
        self.text_title.move(centerx=self.frame.centerx, top=self.frame.top + 50)
        self.scale_music.move(centerx=self.frame.centerx, bottom=self.frame.centery - 20)
        self.scale_sound.move(centerx=self.frame.centerx, top=self.frame.centery + 20)
        self.button_cancel.move(centerx=self.frame.centerx, bottom=self.frame.bottom - 10)

class NavyWindow(Window):
    def __init__(self):
        Window.__init__(self, size=(1280, 720), flags=pygame.DOUBLEBUF, bg_music=RESOURCES.MUSIC["menu"])
        self.set_icon(RESOURCES.IMG["icon"])
        self.set_title("Navy")
        self.set_fps(60)
        self.disable_key_joy_focus_for_all_window()

        self.bg = Image(RESOURCES.IMG["menu_bg"], self.size)
        self.logo = Image(RESOURCES.IMG["logo"])

        params_for_all_buttons = {
            "font": (None, 100),
            "bg": GREEN,
            "hover_bg": GREEN_LIGHT,
            "active_bg": GREEN_DARK,
            "outline": 3,
            "highlight_color": YELLOW,
        }
        self.menu_buttons = ButtonListVertical(offset=30)
        self.menu_buttons.add(
            Button(self, "Play against AI", **params_for_all_buttons, callback=self.single_player),
            Button(self, "Play as P1", **params_for_all_buttons, callback=lambda: self.multiplayer_menu(PlayerServer)),
            Button(self, "Play as P2", **params_for_all_buttons, callback=lambda: self.multiplayer_menu(PlayerClient)),
            Button(self, "Quit", **params_for_all_buttons, callback=self.stop)
        )
        self.button_settings = Button(self, img=Image(RESOURCES.IMG["settings"], size=50), compound="center", callback=self.open_settings, **params_for_all_buttons)

    def place_objects(self):
        self.bg.center = self.center
        self.logo.centerx = self.centerx
        self.menu_buttons.move(centerx=self.centerx, bottom=self.bottom - 20)
        self.button_settings.move(left=10, bottom=self.bottom - 10)

    def open_settings(self):
        self.hide_all(without=[self.bg, self.logo])
        Options(self).mainloop()
        self.show_all()

    def single_player(self):
        setup = NavySetup(None, 1)
        setup.mainloop()

    def multiplayer_menu(self, player_class: Type[Union[PlayerServer, PlayerClient]]) -> None:
        self.hide_all(without=[self.bg, self.logo])
        try:
            player = player_class(self)
        except OSError:
            pass
        else:
            player.mainloop()
        self.show_all()

if __name__ == "__main__":
    NavyWindow().mainloop()