# -*- coding: Utf-8 -*

import socket
import select
from constant import IMG
from my_pygame.window import Window
from my_pygame.classes import Button, RectangleShape, Image, Text, Entry
from my_pygame.colors import BLACK, GREEN, GREEN_DARK, GREEN_LIGHT, YELLOW
from setup_navy import NavySetup
from loading import Loading
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
        self.bg = Image(IMG["menu_bg"], self.window_rect.size)
        self.logo = Image(IMG["logo"])
        self.socket = None
        self.ip = socket.gethostbyname(socket.gethostname())
        self.port = 12800
        self.frame_size = int(0.5 * self.window_rect.w), int(0.5 * self.window_rect.h)
        self.frame = RectangleShape(self.frame_size, GREEN_DARK, outline=5)
        self.text_title = Text("Waiting for Player 2", ("calibri", 100), BLACK)
        self.ip_address = Text(f"IP address: {self.ip}", ("calibri", 80), BLACK)
        self.port_of_connection = Text(f"Port: {self.port}", ("calibri", 80), BLACK)
        self.ai_button = Button(self, "Against AI", command=self.play_against_ai, **params_for_all_buttons)
        self.cancel_button = Button(self, "Return to menu", command=self.stop, **params_for_all_buttons)
        self.with_ai = False
        self.place_objects()
        self.after(0, self.check_incoming_connection)

    def place_objects(self):
        self.bg.move(center=self.window_rect.center)
        self.logo.move(centerx=self.window_rect.centerx, y=10)
        self.frame.move(center=self.window_rect.center)
        self.text_title.move(centerx=self.frame.centerx, top=self.frame.top + 50)
        self.ip_address.move(centerx=self.window_rect.centerx, bottom=self.frame.rect.centery - 10)
        self.port_of_connection.move(centerx=self.ip_address.centerx, top=self.ip_address.bottom + 20)
        self.ai_button.move(centerx=self.frame.centerx - (self.frame.w / 4), bottom=self.frame.bottom - 50)
        self.cancel_button.move(centerx=self.frame.centerx + (self.frame.w / 4), bottom=self.frame.bottom - 50)

    def on_quit(self):
        self.close_socket()
        self.with_ai = False

    def close_socket(self):
        if self.socket is not None:
            self.socket.close()
        self.socket = None

    def set_up_connection(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(("", self.port))
        self.socket.listen(1)

    def check_incoming_connection(self):
        if self.socket is None:
            self.set_up_connection()
        try:
            connections = select.select([self.socket], [], [], 0.05)[0]
        except (socket.error, ValueError, TypeError):
            pass
        else:
            if len(connections) > 0 or self.with_ai:
                if len(connections) > 0:
                    socket_player_2 = connections[0].accept()[0]
                    timer = True
                else:
                    self.close_socket()
                    socket_player_2 = None
                    timer = False
                first_page = self
                while True:
                    loading_page = Loading(side_opening="top", side_ending="bottom")
                    loading_page.show(first_page)
                    setup = NavySetup(timer)
                    loading_page.hide(setup)
                    setup.mainloop()
                    if setup.start_game:
                        first_page = setup
                        loading_text = "Loading..." if socket_player_2 is None else "Waiting for player 2"
                        loading_page = Loading(text=loading_text, side_opening="right", side_ending="left")
                        loading_page.show(setup)
                        gameplay = Gameplay(setup, socket_player_2, True)
                        loading_page.hide(gameplay)
                        gameplay.mainloop()
                        if gameplay.finish is None or not gameplay.finish.restart:
                            break
                        first_page = gameplay.finish
                    else:
                        break
                if socket_player_2 is not None:
                    socket_player_2.close()
                self.stop()
        finally:
            self.after(10, self.check_incoming_connection)

    def play_against_ai(self):
        self.with_ai = True

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
        self.bg = Image(IMG["menu_bg"], self.window_rect.size)
        self.logo = Image(IMG["logo"])
        self.frame_size = int(0.5 * self.window_rect.w), int(0.5 * self.window_rect.h)

        self.frame = RectangleShape(self.frame_size, GREEN_DARK, outline=5)
        self.text_title = Text("Connect to Player 1", ("calibri", 100), BLACK)
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
        self.text_title.move(centerx=self.frame.rect.centerx, top=self.frame.top + 50)
        self.ip.move(centerx=self.window_rect.centerx, bottom=self.frame.centery - 10)
        self.text_ip.move(centery=self.ip.centery, right=self.ip.left - 10)
        self.port.move(left=self.ip.left, top=self.ip.bottom + 20)
        self.text_port.move(centery=self.port.centery, right=self.port.left - 10)
        self.connect_button.move(centerx=self.frame.w / 4 + self.frame.x, bottom=self.frame.bottom - 50)
        self.cancel_button.move(centerx=self.frame.w * 3 / 4 + self.frame.x, bottom=self.frame.bottom - 50)

    def connection(self):
        try:
            socket_player_1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_player_1.settimeout(3)
            socket_player_1.connect((self.ip.get(), int(self.port.get())))
        except socket.error:
            play = False
        else:
            play = True
            setup = NavySetup(True)
            setup.mainloop()
        finally:
            socket_player_1.close()
        if play:
            self.stop()