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
        self.after(10, self.stop)
