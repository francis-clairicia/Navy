# -*- coding:Utf-8 -*

import random
from math import sin, cos
import pygame
from constant import IMG
from my_pygame.window import Window
from my_pygame.classes import Image, ImageButton, Button, Text
from my_pygame.colors import GREEN, GREEN_DARK, GREEN_LIGHT, WHITE
from vector import Vector

class BoxSetup(Image):
    def __init__(self, valid: str, invalid: str, pos: tuple, *args, **kwargs):
        Image.__init__(self, valid, *args, **kwargs)
        self.colors = {
            "green": self.image,
            "red": Image(invalid, *args, **kwargs).image
        }
        self.actual = "green"
        self.ship = None
        self.pos = pos

    @property
    def in_use(self):
        return self.ship is not None

    def set_color(self, color: str):
        self.image = self.colors[color]
        self.actual = color

    def is_valid(self):
        return self.actual == "green"

class ShipSetup(Image):

    def __init__(self, ship_size, navy_setup, image_filepath, *args, **kwargs):
        Image.__init__(self, image_filepath, *args, **kwargs)
        self.navy_setup = navy_setup
        self.ship_size = ship_size
        self.case_size = navy_setup.case_size
        self.clicked = False
        self.on_move = False
        self.pos_offset = (0, 0)
        self.cases_covered = list()
        self.nb_cases_covered = 0
        self.set_on_map = False
        self.vector_repos = list()
        self.orient = "horizontal"
        self.rotate(90)
        self.set_width(self.case_size * ship_size)
        self.default_rect = self.image.get_rect()
        navy_setup.bind_event(pygame.MOUSEBUTTONDOWN, self.select_event)
        navy_setup.bind_event(pygame.MOUSEBUTTONUP, lambda event: self.unselect_event())
        navy_setup.bind_event(pygame.MOUSEMOTION, self.move_event)

    @property
    def on_map(self):
        return len(self.cases_covered) > 0

    def set_default_pos(self, **kwargs):
        self.move(**kwargs)
        self.default_rect = self.rect.copy()

    def select_event(self, event):
        if not self.rect.collidepoint(event.pos):
            return
        self.navy_setup.set_object_priority(self, self.navy_setup.end_list)
        self.clicked = True
        self.pos_offset = (event.pos[0] - self.rect.left, event.pos[1] - self.rect.top)

    def unselect_event(self):
        was_clicked = self.clicked
        self.clicked = False
        if not was_clicked:
            return
        if self.on_move:
            self.on_move = False
            self.place_ship()
        else:
            self.rotate_ship()

    def rotate_ship(self):
        if len(self.cases_covered) == 0:
            return
        first_box = self.cases_covered[0]
        x, y = first_box.pos
        new_cases = list()
        if self.orient == "horizontal":
            for i in range(1, self.ship_size):
                box = self.navy_setup.cases_rect.get((x, y + i))
                if box is None or box.in_use:
                    return
                new_cases.append(box)
            self.rotate(-90)
            self.orient = "vertical"
        else:
            for i in range(1, self.ship_size):
                box = self.navy_setup.cases_rect.get((x + i, y))
                if box is None or box.in_use:
                    return
                new_cases.append(box)
            self.rotate(90)
            self.orient = "horizontal"
        if self.orient == "horizontal":
            self.set_default_pos(x=first_box.x, centery=first_box.centery)
        else:
            self.set_default_pos(y=first_box.y, centerx=first_box.centerx)
        for box in self.cases_covered:
            box.ship = None
        self.cases_covered.clear()
        self.cases_covered += [first_box] + new_cases
        for box in self.cases_covered:
            box.ship = self

    def place_ship(self):
        active_cases = list()
        for box in self.navy_setup.cases_rect.values():
            if box.is_shown():
                active_cases.append(box)
            box.hide()
        if len(active_cases) > 0 and all(box.is_valid() for box in active_cases):
            for box in self.cases_covered:
                box.ship = None
            for box in active_cases:
                box.ship = self
            self.cases_covered.clear()
            self.cases_covered += active_cases
            first_box = active_cases[0]
            if self.orient == "horizontal":
                self.set_default_pos(x=first_box.x, centery=first_box.centery)
            else:
                self.set_default_pos(y=first_box.y, centerx=first_box.centerx)
        else:
            axis = Vector(1, 0)
            vector_direction = Vector.from_two_points(self.topleft, self.default_rect.topleft)
            angle = axis.angle_with_vector(vector_direction)
            if self.default_rect.y < self.y:
                angle = -angle
            self.vector_repos = [cos(angle), sin(angle)]
            self.reposition()

    def move_event(self, event):
        if not self.clicked:
            return
        self.on_move = True
        topleft = list(event.pos)
        for i in range(2):
            topleft[i] -= self.pos_offset[i]
        self.move(topleft=tuple(topleft))
        self.nb_cases_covered = 0
        cases = list()
        for box in self.navy_setup.cases_rect.values():
            self.show_cases(box)
            if box.is_shown():
                cases.append(box)
        if any((not self.navy_setup.valid_box(box, self)) for box in cases):
            for box in cases:
                box.set_color("red")

    def show_cases(self, box: BoxSetup):
        box.hide()
        grid = self.navy_setup.navy_grid
        if not grid.rect.collidepoint(self.topleft) or not grid.rect.collidepoint(self.topright):
            return
        if self.nb_cases_covered == self.ship_size:
            return
        if self.orient == "horizontal":
            if (box.top <= self.centery <= box.bottom) is False:
                return
            if self.left > box.centerx or self.right < box.centerx:
                return
        else:
            if (box.left <= self.centerx <= box.right) is False:
                return
            if self.top > box.centery or self.bottom < box.centery:
                return
        box.show()
        box.set_color("green")

    def reposition(self):
        self.on_move = True
        if self.x == self.default_rect.x and self.y == self.default_rect.y:
            self.on_move = False
            return
        speed = 20
        if self.x != self.default_rect.x:
            offset = self.vector_repos[0] * speed
            new_x = self.x + offset
            if (self.x <= self.default_rect.x <= new_x) or (new_x <= self.default_rect.x <= self.x):
                new_x = self.default_rect.x
            self.move(x=new_x, y=self.y)
        if self.y != self.default_rect.y:
            offset = self.vector_repos[1] * speed
            new_y = self.y + offset
            if (self.y <= self.default_rect.y <= new_y) or (new_y <= self.default_rect.y <= self.y):
                new_y = self.default_rect.y
            self.move(y=new_y, x=self.x)
        self.navy_setup.after(10, self.reposition)

class NavySetup(Window):

    def __init__(self, timer: bool):
        Window.__init__(self, bg_color=(0, 200, 255))
        self.start_game = False
        params_for_all_buttons = {
            "bg": GREEN,
            "over_bg": GREEN_DARK,
            "active_bg": GREEN_LIGHT
        }
        self.navy_grid = Image(IMG["grid"], size=(800, 800))
        self.navy_grid.move(x=20, centery=self.window_rect.centery)
        arrow = Image(IMG["arrow_blue"], rotate=180, size=(70, 70))
        self.quit_button = ImageButton(self, arrow, command=self.stop)
        self.quit_button.move(x=20, y=20)
        self.play_button = Button(self, "Play", font=("calibri", 100), command=self.play, **params_for_all_buttons)
        self.play_button.move(right=self.window_rect.right - 20, bottom=self.window_rect.bottom - 70)
        option_size = (100, 100)
        restart = Image(IMG["reload_blue"], size=option_size)
        self.restart_button = ImageButton(self, restart, show_bg=True, command=self.reinit_all_ships, **params_for_all_buttons)
        self.restart_button.move(left=self.navy_grid.right + 20, bottom=self.navy_grid.bottom)
        random_image = Image(IMG["random"], size=option_size)
        self.random_button = ImageButton(self, random_image, show_bg=True, command=self.random_positions, **params_for_all_buttons)
        self.random_button.move(left=self.restart_button.right + 30, centery=self.restart_button.centery)
        self.timer_format = "Time left: {0}"
        self.my_clock = 30
        self.timer = Text(self.timer_format.format(self.my_clock), ("calibri", 70), WHITE, right=self.window_rect.right - 20, top=20)
        if timer:
            self.after(1000, self.update_timer)
        else:
            self.timer.hide()
        self.case_size = round(self.navy_grid.w / 10)
        self.cases_rect = dict()
        self.init_cases()
        self.ships = dict()
        self.saves_rect = dict()
        self.ships["carrier"] = self.carrier = ShipSetup(4, self, IMG["carrier"])
        self.ships["battleship_1"] = self.battleship_1 = ShipSetup(3, self, IMG["battleship"])
        self.ships["battleship_2"] = self.battleship_2 = ShipSetup(3, self, IMG["battleship"])
        self.ships["destroyer_1"] = self.destroyer_1 = ShipSetup(2, self, IMG["destroyer"])
        self.ships["destroyer_2"] = self.destroyer_2 = ShipSetup(2, self, IMG["destroyer"])
        self.ships["destroyer_3"] = self.destroyer_3 = ShipSetup(2, self, IMG["destroyer"])
        self.ships["patroal_1"] = self.patroal_1 = ShipSetup(1, self, IMG["patroal_boat"])
        self.ships["patroal_2"] = self.patroal_2 = ShipSetup(1, self, IMG["patroal_boat"])
        self.ships["patroal_3"] = self.patroal_3 = ShipSetup(1, self, IMG["patroal_boat"])
        self.ships["patroal_4"] = self.patroal_4 = ShipSetup(1, self, IMG["patroal_boat"])
        self.carrier.set_default_pos(left=self.navy_grid.right + 100, top=self.navy_grid.top + 30)
        self.battleship_1.set_default_pos(left=self.carrier.left, top=self.carrier.bottom + 70)
        for i in range(1, 2):
            prev = self.ships[f"battleship_{i}"]
            actual = self.ships[f"battleship_{i + 1}"]
            actual.set_default_pos(left=prev.right + 30, centery=prev.centery)
        self.destroyer_1.set_default_pos(left=self.battleship_1.left, top=self.battleship_1.bottom + 70)
        for i in range(1, 3):
            prev = self.ships[f"destroyer_{i}"]
            actual = self.ships[f"destroyer_{i + 1}"]
            actual.set_default_pos(left=prev.right + 30, centery=prev.centery)
        self.patroal_1.set_default_pos(left=self.destroyer_1.left, top=self.destroyer_1.bottom + 70)
        for i in range(1, 4):
            prev = self.ships[f"patroal_{i}"]
            actual = self.ships[f"patroal_{i + 1}"]
            actual.set_default_pos(left=prev.right + 70, centery=prev.centery)
        for name, ship in self.ships.items():
            self.saves_rect[name] = ship.rect.copy()

    def init_cases(self):
        c = self.case_size
        n = self.navy_grid
        for j in range(10):
            for i in range(10):
                box = BoxSetup(IMG["green_box"], IMG["red_box"], (i, j), size=(c, c), x=n.x + (c * i), y=n.y + (c * j))
                box.hide()
                self.add(box)
                self.cases_rect[i, j] = box

    def update_timer(self):
        self.my_clock -= 1
        if self.my_clock == 0:
            for ship in self.ships.values():
                if not ship.on_map:
                    self.set_random_position(ship)
            self.play()
        else:
            self.timer.set_string(self.timer_format.format(self.my_clock))
            self.after(1000, self.update_timer)

    def play(self):
        if any(not ship.on_map for ship in self.ships.values()):
            return
        self.start_game = True
        self.stop()

    def valid_box(self, box: BoxSetup, relative_to: ShipSetup):
        x, y = box.pos
        offsets = [
            (-1, -1),
            (0, -1),
            (1, -1),
            (-1, 0),
            (0, 0),
            (1, 0),
            (-1, 1),
            (0, 1),
            (1, 1)
        ]
        for u, v in offsets:
            box = self.cases_rect.get((x + u, y + v))
            if box is None:
                continue
            if box.in_use and box.ship != relative_to:
                return False
        return True

    def reinit_all_ships(self):
        for name, ship in self.ships.items():
            if not ship.on_map:
                continue
            if ship.orient == "vertical":
                ship.orient = "horizontal"
                ship.rotate(90)
            ship.cases_covered.clear()
            ship.set_default_pos(topleft=self.saves_rect[name].topleft)
        for box in self.cases_rect.values():
            box.ship = None

    def random_positions(self):
        self.reinit_all_ships()
        for ship in self.ships.values():
            self.set_random_position(ship)

    def set_random_position(self, ship: ShipSetup):
        vertical = random.choice([True, False])
        if vertical:
            ship.rotate(-90)
            ship.orient = "vertical"
        else:
            ship.orient = "horizontal"
        first_box = random.choice(self.get_available_boxes(ship))
        for i in range(ship.ship_size):
            x, y = first_box.pos
            x += i if ship.orient == "horizontal" else 0
            y += i if ship.orient == "vertical" else 0
            box = self.cases_rect[x, y]
            box.ship = ship
            ship.cases_covered.append(box)
        if ship.orient == "horizontal":
            ship.set_default_pos(x=first_box.x, centery=first_box.centery)
        else:
            ship.set_default_pos(y=first_box.y, centerx=first_box.centerx)

    def get_available_boxes(self, ship: ShipSetup):
        available_boxes = list()
        for box in self.cases_rect.values():
            if not self.valid_box(box, ship):
                continue
            x, y = box.pos
            valid = True
            for i in range(1, ship.ship_size):
                u = x + i if ship.orient == "horizontal" else x
                v = y + i if ship.orient == "vertical" else y
                b = self.cases_rect.get((u, v))
                if b is None or (not self.valid_box(b, ship)):
                    valid = False
                    break
            if valid:
                available_boxes.append(box)
        return available_boxes

if __name__ == "__main__":
    NavySetup(False).mainloop()