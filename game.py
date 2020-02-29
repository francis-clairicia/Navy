# -*- coding: Utf-8 -*

import socket
import pygame
from constant import IMG
from my_pygame.window import Window
from my_pygame.classes import Drawable, Image, ImageButton
from setup_navy import NavySetup

class Box(Image):
    def __init__(self, valid: str, invalid: str, *args, **kwargs):
        Image.__init__(self, valid, *args, **kwargs)
        self.colors = {
            "green": self.image,
            "red": Image(invalid, *args, **kwargs).image
        }
        self.actual = "green"
        self.hit = False

    @property
    def hit(self):
        return self.actual == "green"

    @hit.setter
    def hit(self, value: bool):
        colors = {
            True: "red",
            False: "green"
        }
        self.set_color(colors[bool(value)])

    def set_color(self, color: str):
        self.image = self.colors[color]
        self.actual = color

class TurnArrow(Drawable):
    def __init__(self, master: Window, init_turn: bool, first_grid: Image, second_grid: Image):
        self.img_turn = {
            True: Image(IMG["green_triangle"]),
            False: Image(IMG["red_triangle"])
        }
        for turn, img in self.img_turn.items():
            img.set_width(second_grid.left - first_grid.right - 150)
            self.img_turn[turn] = img.image
        Drawable.__init__(self, surface=self.img_turn[init_turn], center=master.window_rect.center)
        self.turn = init_turn

    def is_my_turn(self):
        return self.turn

    def change_turn(self):
        self.turn = not self.turn
        self.image = self.img_turn[self.turn]

class Ship(Drawable):
    def __init__(self, ship_setup):
        Drawable.__init__(self, surface=ship_setup.image)
        self.move(topleft=ship_setup.topleft)
        self.cases = list()
        for box in ship_setup.cases_covered:
            self.cases.append([box.pos, False])

    def destroyed(self):
        return all(case[1] is True for case in self.cases)

    def hit(self, pos):
        for case in self.cases:
            if case[0] == pos:
                case[1] = True
                return True
        return False

class Navy:
    def __init__(self):
        self.map = [[0 for _ in range(10)] for _ in range(10)]
        self.ships = list()

    def load(self, ship_setup: list):
        for s in ship_setup:
            ship = Ship(s)
            for case in ship.cases:
                x, y = case[0]
                self.map[y][x] = 1
            self.ships.append(ship)

    def destroyed(self):
        return all(ship.destroyed() for ship in self.ships)

class AI:
    def __init__(self):
        navy_setup = NavySetup(None, False)
        navy_setup.random_positions()
        self.navy = Navy()
        self.navy.load(list(navy_setup.ships.values()))
        self.navy.ships.clear()

class Gameplay(Window):
    def __init__(self, navy_setup, player_socket: socket.socket, turn: bool):
        Window.__init__(self, bg_color=navy_setup.bg_color)
        self.socket = player_socket
        self.navy = Navy()
        arrow = Image(IMG["arrow_blue"], rotate=180, size=(70, 70))
        self.quit_button = ImageButton(self, arrow, command=self.stop)
        self.quit_button.move(x=20, y=20)
        self.grid = Image(IMG["grid"])
        self.enemy_grid = Image(IMG["grid"])
        ship_setup_list = list(navy_setup.ships.values())
        self.navy.load(ship_setup_list)
        self.grid.set_size(navy_setup.navy_grid.size)
        self.grid.move(topleft=navy_setup.navy_grid.topleft)
        self.enemy_grid.set_size(navy_setup.navy_grid.size)
        self.enemy_grid.move(right=self.window_rect.right - self.grid.left, centery=self.grid.centery)
        for ship in self.navy.ships:
            self.add(ship)
        self.enemy_boxes = dict()
        self.cursor_pos = (-1, -1)
        self.init_enemy_boxes()
        self.turn_checker = TurnArrow(self, turn, self.grid, self.enemy_grid)
        self.bind_mouse(self.choose_box)
        self.bind_event(pygame.MOUSEBUTTONDOWN, self.click_on_box)

    def init_enemy_boxes(self):
        c = round(self.enemy_grid.w / 10)
        n = self.enemy_grid
        for j in range(10):
            for i in range(10):
                box = Box(IMG["green_box"], IMG["red_box"], size=(c, c), x=n.x + (c * i), y=n.y + (c * j))
                box.hide()
                self.add(box)
                self.enemy_boxes[i, j] = box

    def choose_box(self, mouse_pos):
        if not self.turn_checker.is_my_turn():
            return
        on_box = False
        for coords, box in self.enemy_boxes.items():
            box.hide()
            if box.rect.collidepoint(mouse_pos):
                self.cursor_pos = coords
                box.show()
                on_box = True
        if not on_box:
            self.cursor_pos = (-1, -1)

    def click_on_box(self, event):
        if not self.turn_checker.is_my_turn() or not self.enemy_grid.rect.collidepoint(event.pos):
            return
        box = self.enemy_boxes.get(self.cursor_pos)
        if box is None:
            return
        box.hit = True