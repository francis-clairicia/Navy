#! /bin/python3
# -*- coding: Utf-8 -*

import sys
import pygame
import constant
from player import PlayerServer, PlayerClient
from my_pygame.window import Window
from my_pygame.colors import BLACK, GREEN, GREEN_DARK, GREEN_LIGHT, YELLOW
from my_pygame.classes import Image, Button

class Navy(Window):
    def __init__(self):
        Window.__init__(self) # flags=pygame.FULLSCREEN
        params_for_all_buttons = {
            "font": ("calibiri", 200),
            "bg": GREEN,
            "over_bg": GREEN_DARK,
            "active_bg": GREEN_LIGHT,
            "over_fg": YELLOW,
            "outline": 5,
            "outline_color": BLACK
        }
        self.bg = Image(constant.IMG["menu_bg"], self.window_rect.size)
        self.logo = Image(constant.IMG["logo"])
        self.player_1 = PlayerServer()
        self.player_2 = PlayerClient()
        self.player_1_button = Button(self, "Play as P1", command=self.player_1.mainloop, **params_for_all_buttons)
        self.player_2_button = Button(self, "Play as P2", command=self.player_2.mainloop, **params_for_all_buttons)
        self.quit_button = Button(self, "Quit", command=self.stop, **params_for_all_buttons)
        self.place_objects()

    def place_objects(self):
        self.bg.move(center=self.window_rect.center)
        self.logo.move(centerx=self.window_rect.centerx, y=10)
        rect = self.player_2_button.move(center=self.window_rect.center)
        self.player_1_button.move(centerx=self.window_rect.centerx, bottom=rect.top - 50)
        self.quit_button.move(centerx=self.window_rect.centerx, top=rect.bottom + 50)
        self.quit_button.set_size(self.player_1_button.size)


def main():
    status = pygame.init()
    if status[1] > 0:
        sys.exit(84)
    navy_game = Navy()
    navy_game.mainloop()
    pygame.quit()
    sys.exit(0)

if __name__ == "__main__":
    main()