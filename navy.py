#! /bin/python3
# -*- coding: Utf-8 -*

from constant import IMG
from player import PlayerServer, PlayerClient
from my_pygame.window import Window
from my_pygame.colors import BLACK, GREEN, GREEN_DARK, GREEN_LIGHT, YELLOW
from my_pygame.classes import Image, Button
from loading import Loading

class NavyGame(Window):
    def __init__(self):
        Window.__init__(self) # flags=pygame.FULLSCREEN
        loading_page = Loading(opening=False, side_ending="right")
        loading_page.show(self)
        self.set_icon(IMG["icon"])
        self.set_title("Navy")
        params_for_all_buttons = {
            "font": ("calibiri", 200),
            "bg": GREEN,
            "over_bg": GREEN_DARK,
            "active_bg": GREEN_LIGHT,
            "over_fg": YELLOW,
            "outline": 5,
            "outline_color": BLACK
        }
        self.bg = Image(IMG["menu_bg"], self.window_rect.size)
        self.logo = Image(IMG["logo"])
        self.player_1 = PlayerServer()
        self.player_2 = PlayerClient()
        self.player_1_button = Button(self, "Play as P1", command=self.player_1.mainloop, **params_for_all_buttons)
        self.player_2_button = Button(self, "Play as P2", command=self.player_2.mainloop, **params_for_all_buttons)
        self.quit_button = Button(self, "Quit", command=self.stop, **params_for_all_buttons)
        self.quit_button.set_size(self.player_1_button.size)
        self.place_objects()
        loading_page.hide(self)

    def place_objects(self):
        self.bg.move(center=self.window_rect.center)
        self.logo.move(centerx=self.window_rect.centerx, y=10)
        self.player_2_button.move(center=self.window_rect.center)
        self.player_1_button.move(centerx=self.window_rect.centerx, bottom=self.player_2_button.top - 50)
        self.quit_button.move(centerx=self.window_rect.centerx, top=self.player_2_button.bottom + 50)

def main():
    navy_game = NavyGame()
    navy_game.mainloop()

if __name__ == "__main__":
    main()