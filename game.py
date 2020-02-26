# -*- coding: Utf-8 -*

import socket
# import constant
from my_pygame.window import Window
from my_pygame.classes import Text
from my_pygame.colors import WHITE

class Gameplay(Window):

    def __init__(self, player_socket: socket.socket, turn: bool):
        Window.__init__(self)
        self.socket = player_socket
        self.turn = turn
        self.text = Text("You are connnected. Quit in 3 secs", ("calibri", 120), WHITE)
        self.text.move(center=self.window_rect.center)
        self.after(3 * 1000, self.stop)