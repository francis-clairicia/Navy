# -*- coding: Utf-8 -*

import socket
import select
import constant
from my_pygame.window import Window
from my_pygame.classes import Button, RectangleShape, Image, Text, Entry
from my_pygame.colors import BLACK, GREEN, GREEN_DARK, GREEN_LIGHT, YELLOW
from game import Gameplay

class PlayerServer(Window):
    def __init__(self):
        Window.__init__(self)
        params_for_all_buttons = {
            "font": ("calibiri", 50),
            "bg": GREEN,
            "over_bg": GREEN_DARK,
            "active_bg": GREEN_LIGHT,
            "over_fg": YELLOW,
            "outline": 5,
            "outline_color": BLACK
        }
        self.bg = Image(constant.IMG["menu_bg"], self.window_rect.size)
        self.logo = Image(constant.IMG["logo"])

        self.socket = None
        self.ip = socket.gethostbyname(socket.gethostname())
        self.port = 12800
        self.frame_size = int(0.5 * self.window_rect.w), int(0.5 * self.window_rect.h)

        self.frame = RectangleShape(self.frame_size, GREEN_DARK, outline=5)
        self.ip_address = Text(f"IP address: {self.ip}", ("calibri", 80), BLACK)
        self.port_of_connection = Text(f"Port: {self.port}", ("calibri", 80), BLACK)
        self.cancel_button = Button(self, "Return to menu", command=self.stop, **params_for_all_buttons)
        self.place_objects()
        self.after(500, self.check_incoming_connection)

    def place_objects(self):
        self.bg.move(center=self.window_rect.center)
        self.logo.move(centerx=self.window_rect.centerx, y=10)
        self.frame.move(center=self.window_rect.center)
        self.ip_address.move(centerx=self.window_rect.centerx, bottom=self.frame.rect.centery - 10)
        self.port_of_connection.move(centerx=self.ip_address.rect.centerx, top=self.ip_address.rect.bottom + 20)
        self.cancel_button.move(centerx=self.frame.rect.centerx, bottom=self.frame.rect.bottom - 50)

    def on_quit(self):
        if self.socket is not None:
            self.socket.close()
        self.socket = None

    def set_up_connection(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(("0.0.0.0", self.port))
        self.socket.listen(1)

    def check_incoming_connection(self):
        if self.socket is None:
            self.set_up_connection()
        try:
            connections = select.select([self.socket], [], [], 0.05)[0]
        except (socket.error, ValueError):
            pass
        else:
            if len(connections) > 0:
                socket_player_2 = connections[0].accept()[0]
                gameplay = Gameplay(socket_player_2, True)
                gameplay.mainloop()
                socket_player_2.close()
                self.stop()
        finally:
            self.after(500, self.check_incoming_connection)

class PlayerClient(Window):
    def __init__(self):
        Window.__init__(self)
        params_for_all_buttons = {
            "font": ("calibiri", 50),
            "bg": GREEN,
            "over_bg": GREEN_DARK,
            "active_bg": GREEN_LIGHT,
            "over_fg": YELLOW,
            "outline": 5,
            "outline_color": BLACK
        }
        self.bg = Image(constant.IMG["menu_bg"], self.window_rect.size)
        self.logo = Image(constant.IMG["logo"])
        self.frame_size = int(0.5 * self.window_rect.w), int(0.5 * self.window_rect.h)

        self.frame = RectangleShape(self.frame_size, GREEN_DARK, outline=5)
        self.ip = Entry(self, font=("calibri", 80), width=13, bg=GREEN, fg=BLACK, highlight_color=YELLOW, outline=5)
        self.text_ip = Text("IP adress", ("calibri", 80), YELLOW)
        self.port = Entry(self, font=("calibri", 80), width=13, bg=GREEN, fg=BLACK, highlight_color=YELLOW, outline=5)
        self.text_port = Text("Port", ("calibri", 80), YELLOW)
        self.connect_button = Button(self, "Connection", command=self.connection, **params_for_all_buttons)
        self.cancel_button = Button(self, "Return to menu", command=self.stop, **params_for_all_buttons)
        self.place_objects()

    def place_objects(self):
        self.bg.move(center=self.window_rect.center)
        self.logo.move(centerx=self.window_rect.centerx, y=10)
        self.frame.move(center=self.window_rect.center)
        self.ip.move(centerx=self.window_rect.centerx, bottom=self.frame.rect.centery - 10)
        self.text_ip.move(centery=self.ip.rect.centery, right=self.ip.rect.left - 10)
        self.port.move(left=self.ip.rect.left, top=self.ip.rect.bottom + 20)
        self.text_port.move(centery=self.port.rect.centery, right=self.port.rect.left - 10)
        self.connect_button.move(centerx=self.frame.rect.w / 4 + self.frame.rect.x, bottom=self.frame.rect.bottom - 50)
        self.cancel_button.move(centerx=self.frame.rect.w * 3 / 4 + self.frame.rect.x, bottom=self.frame.rect.bottom - 50)

    def connection(self):
        try:
            socket_player_1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_player_1.settimeout(0.5)
            socket_player_1.connect((self.ip.get(), int(self.port.get())))
        except socket.error:
            return
        else:
            gameplay = Gameplay(socket_player_1, False)
            gameplay.mainloop()
        finally:
            socket_player_1.close()
        self.stop()