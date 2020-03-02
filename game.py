# -*- coding: Utf-8 -*

import socket
import random
import pygame
from constant import IMG
from my_pygame.window import Window
from my_pygame.classes import Drawable, Image, ImageButton, Text, RectangleShape, Button
from my_pygame.colors import GREEN, GREEN_DARK, GREEN_LIGHT, BLACK
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
        return self.__hit

    @hit.setter
    def hit(self, value: bool):
        colors = {
            True: "red",
            False: "green"
        }
        self.set_color(colors[bool(value)])
        self.__hit = value

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

    def change_turn(self, turn: bool):
        self.turn = turn
        self.image = self.img_turn[turn]

class Ship(Drawable):
    def __init__(self, navy, ship_setup):
        Drawable.__init__(self, surface=ship_setup.image)
        self.navy = navy
        self.orient = ship_setup.orient
        self.cases = list()
        for box in ship_setup.cases_covered:
            self.cases.append([box.pos, False])
        self.set_position()

    def set_position(self):
        first_box_pos = self.cases[0][0]
        first_box = self.navy.boxes[first_box_pos]
        if self.orient == "horizontal":
            self.move(x=first_box.x, centery=first_box.centery)
        else:
            self.move(y=first_box.y, centerx=first_box.centerx)

    def destroyed(self):
        return all(case[1] is True for case in self.cases)

    def hit(self, pos):
        for case in self.cases:
            if case[0] == pos:
                case[1] = True
                return True
        return False

class Navy:
    def __init__(self, setup: NavySetup):
        self.map = [[0 for _ in range(10)] for _ in range(10)]
        self.grid = Image(IMG["grid"])
        self.grid.set_size(setup.navy_grid.size)
        self.boxes = dict()
        self.init_boxes()
        self.ships = list()
        for ship in setup.ships.values():
            ship = Ship(self, ship)
            self.ships.append(ship)
        self.cases = list()

    @classmethod
    def from_random_setup(cls):
        setup = NavySetup(False)
        setup.random_positions()
        return cls(setup)

    def init_boxes(self):
        c = round(self.grid.w / 10)
        for j in range(10):
            for i in range(10):
                box = Box(IMG["green_box"], IMG["red_box"], size=(c, c), x=(c * i), y=(c * j))
                box.hide()
                self.boxes[i, j] = box

    def draw(self, surface):
        grid = Drawable(self.grid.image.copy())
        grid.move(center=self.grid.center)
        for box in self.boxes.values():
            box.draw(grid.image)
        for ship in self.ships:
            ship.draw(grid.image)
        for case in self.cases:
            case.draw(grid.image)
        grid.draw(surface)

    def destroyed(self):
        return all(ship.destroyed() for ship in self.ships)

    def move_cursor(self, mouse_pos):
        for box in self.boxes.values():
            box.hide()
        for coords, box in self.boxes.items():
            rect = box.rect.move(self.grid.x, self.grid.y)
            if rect.collidepoint(mouse_pos):
                box.show()
                return coords
        return (-1, -1)

    def add_case(self, img: str, box: Box):
        case = Image(IMG[img], size=box.size)
        case.move(center=box.center)
        self.cases.append(case)
        box.hit = True
        box.hide()

    def hit_box(self, pos: tuple):
        x, y = pos
        box = self.boxes[pos]
        if box.hit:
            return True
        for ship in self.ships:
            if ship.hit(pos):
                self.add_case("cross", box)
                self.map[y][x] = 2
                if ship.destroyed():
                    self.display_destroyed_ship(ship)
                return True
        self.add_case("hatch", box)
        self.map[y][x] = 1
        return False

    def display_destroyed_ship(self, ship: Ship):
        ship.show()
        offsets = [
            (-1, -1),
            (0, -1),
            (1, -1),
            (-1, 0),
            (1, 0),
            (-1, 1),
            (0, 1),
            (1, 1)
        ]
        for case in ship.cases:
            x, y = case[0]
            self.map[y][x] = 3
            for u, v in offsets:
                box = self.boxes.get((x + u, y + v))
                if box is None:
                    continue
                if not box.hit:
                    self.add_case("hatch", box)

class AI:
    def __init__(self):
        self.cases_hitted = list()
        self.possibilities = [(i, j) for i in range(10) for j in range(10)]

    def play(self, navy_map: list):
        for x, y in self.cases_hitted.copy():
            if navy_map[y][x] != 2:
                self.cases_hitted.remove((x, y))
        for x, y in self.possibilities.copy():
            if navy_map[y][x] != 0:
                if navy_map[y][x] == 2:
                    self.cases_hitted.append((x, y))
                self.possibilities.remove((x, y))
        if len(self.cases_hitted) > 0:
            return self.hit_the_ship(navy_map)
        return random.choice(self.possibilities)

    def hit_the_ship(self, navy_map: list):
        if len(self.cases_hitted) == 1:
            return self.find_ship(navy_map, *self.cases_hitted[0])
        self.cases_hitted.sort()
        index = 1 if self.cases_hitted[0][0] == self.cases_hitted[-1][0] else 0
        first, second = list(self.cases_hitted[0]), list(self.cases_hitted[-1])
        first[index] -= 1
        second[index] += 1
        potential_boxes = list()
        for x, y in (first, second):
            if x not in range(10) or y not in range(10):
                continue
            if navy_map[y][x] == 0:
                potential_boxes.append((x, y))
        return random.choice(potential_boxes)

    def find_ship(self, navy_map: list, x: int, y: int):
        offsets = [
            (0, -1),
            (-1, 0),
            (1, 0),
            (0, 1)
        ]
        potential_boxes = list()
        for i, j in [(x + u, y + v) for u, v in offsets]:
            if i in range(10) and j in range(10) and navy_map[j][i] == 0:
                potential_boxes.append((i, j))
        return random.choice(potential_boxes)

class Finish(Window):
    def __init__(self, gameplay_surface, player_who_won: bool):
        Window.__init__(self)
        self.bg = Drawable(gameplay_surface)
        veil = pygame.Surface(self.window_rect.size, pygame.SRCALPHA).convert_alpha()
        veil.fill((0, 0, 0, 150))
        self.veil = Drawable(veil)
        params_for_all_buttons = {
            "font": ("calibiri", 50),
            "bg": GREEN,
            "over_bg": GREEN_DARK,
            "active_bg": GREEN_LIGHT,
            "outline": 5,
            "outline_color": BLACK
        }
        winner = {True: "I", False: "Enemy"}[player_who_won] + " " + "won"
        self.frame_size = int(0.5 * self.window_rect.w), int(0.5 * self.window_rect.h)
        self.frame = RectangleShape(self.frame_size, GREEN_DARK, outline=5)
        self.winner = Text(winner, ("calibri", 100), BLACK)
        self.ask = Text(f"Restart the party ?", ("calibri", 80), BLACK)
        self.restart_button = Button(self, "Restart", command=self.restart_the_game, **params_for_all_buttons)
        self.cancel_button = Button(self, "Return to menu", command=self.stop, **params_for_all_buttons)
        self.restart = False
        self.place_objects()

    def place_objects(self):
        self.bg.move(center=self.window_rect.center)
        self.frame.move(center=self.window_rect.center)
        self.winner.move(centerx=self.window_rect.centerx, bottom=self.frame.rect.centery - 10)
        self.ask.move(centerx=self.winner.centerx, top=self.winner.bottom + 20)
        self.restart_button.move(centerx=self.frame.centerx - (self.frame.w / 4), bottom=self.frame.bottom - 50)
        self.cancel_button.move(centerx=self.frame.centerx + (self.frame.w / 4), bottom=self.frame.bottom - 50)

    def restart_the_game(self):
        self.restart = True
        self.stop()

class Gameplay(Window):
    def __init__(self, navy_setup, player_socket: socket.socket, turn: bool):
        Window.__init__(self, bg_color=navy_setup.bg_color)
        self.socket = player_socket
        self.navy = Navy(navy_setup)
        self.navy.grid.move(topleft=navy_setup.navy_grid.topleft)
        arrow = Image(IMG["arrow_blue"], rotate=180, size=(70, 70))
        self.quit_button = ImageButton(self, arrow, command=self.stop)
        self.quit_button.move(x=20, y=20)
        self.enemy_navy = Navy.from_random_setup()
        self.enemy_navy.grid.move(right=self.window_rect.right - self.navy.grid.left, centery=self.navy.grid.centery)
        for ship in self.enemy_navy.ships:
            ship.hide()
        self.cursor_pos = (-1, -1)
        self.turn_checker = TurnArrow(self, turn, self.navy.grid, self.enemy_navy.grid)
        self.bind_mouse(self.choose_box)
        self.bind_event(pygame.MOUSEBUTTONDOWN, lambda event: self.click_on_box())
        self.ai = AI()
        self.finish = None

    def ai_play(self):
        cursor_pos = self.ai.play(self.navy.map)
        status = self.navy.hit_box(cursor_pos)
        self.check_victory()
        self.turn_checker.change_turn(not status)
        if not self.turn_checker.is_my_turn():
            self.after(500, self.ai_play)

    def choose_box(self, mouse_pos):
        if not self.turn_checker.is_my_turn():
            return
        self.cursor_pos = self.enemy_navy.move_cursor(mouse_pos)

    def click_on_box(self):
        if not self.turn_checker.is_my_turn() or self.cursor_pos == (-1, -1):
            return
        status = self.enemy_navy.hit_box(self.cursor_pos)
        self.check_victory()
        self.turn_checker.change_turn(status)
        if not self.turn_checker.is_my_turn():
            self.after(500, self.ai_play)

    def check_victory(self):
        if not self.navy.destroyed() and not self.enemy_navy.destroyed():
            return
        self.draw_screen()
        self.finish = Finish(self.window.copy(), self.turn_checker.is_my_turn())
        self.finish.mainloop()
        self.stop()