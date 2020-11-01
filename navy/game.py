# -*- coding: Utf-8 -*

import socket
import select
import pickle
import random
import json
import pygame
from typing import Sequence, Dict, Any, Tuple, Union
from my_pygame import Window, DrawableList, DrawableListHorizontal, DrawableListVertical
from my_pygame import Image, ImageButton, Text, RectangleShape, Button
from my_pygame import GREEN, GREEN_DARK, GREEN_LIGHT, BLACK, WHITE, YELLOW, TRANSPARENT, RED, RED_DARK
from .constants import RESOURCES, NB_LINES_BOXES, NB_COLUMNS_BOXES, BOX_SIZE
from .player import Player

class Box(Button):
    def __init__(self, master, navy, size: Tuple[int, int], pos: Tuple[int, int]):
        params = {
            "size": size,
            "bg": TRANSPARENT,
            "hover_bg": GREEN,
            "active_bg": GREEN_DARK,
            "disabled_bg": TRANSPARENT,
            "disabled_hover_bg": RED,
            "disabled_active_bg": RED_DARK,
            "outline_color": WHITE,
            "highlight_color": WHITE,
        }
        Button.__init__(self, master=master, callback=lambda: master.hit_a_box(navy, self), **params)
        self.pos = pos

class Ship(Image):

    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"

    def __init__(self, name: str, boxes: Sequence[Tuple[int, int]], orient: str):
        Image.__init__(self, RESOURCES.IMG[name])
        self.name = name
        self.__orient = Ship.VERTICAL
        self.ship_size = len(boxes)
        self.boxes_pos = [tuple(box_pos) for box_pos in boxes]
        self.set_height(self.ship_size * BOX_SIZE[0])
        self.orient = orient
        self.__boxes_covered = list()

    def get_setup(self) -> Dict[str, Dict[str, Any]]:
        return {"name": self.name, "boxes": self.boxes_pos, "orient": self.orient}

    @property
    def orient(self) -> str:
        return self.__orient

    @orient.setter
    def orient(self, orient: str) -> None:
        if orient in (Ship.VERTICAL, Ship.HORIZONTAL) and orient != self.__orient:
            if orient == Ship.HORIZONTAL:
                self.rotate(90)
            else:
                self.rotate(-90)
            self.__orient = orient

    @property
    def boxes_covered(self) -> Sequence[Box]:
        return self.__boxes_covered

    @boxes_covered.setter
    def boxes_covered(self, boxes: Sequence[Box]) -> None:
        self.__boxes_covered = boxes

    def destroyed(self) -> bool:
        return all(box.state == Button.DISABLED for box in self.boxes_covered)

    def place_ship(self, boxes: Sequence[Box]):
        left = min(boxes, key=lambda box: box.left).left
        top = min(boxes, key=lambda box: box.top).top
        right = max(boxes, key=lambda box: box.right).right
        bottom = max(boxes, key=lambda box: box.bottom).bottom
        width = right - left
        height = bottom - top
        rect = pygame.Rect(left, top, width, height)
        self.center = rect.center
        self.boxes_covered = boxes

class Navy(DrawableListVertical):

    BOX_NO_HIT = 0
    BOX_HATCH = 1
    BOX_CROSS = 2
    BOX_SHIP_DESTROYED = 3

    def __init__(self, master, setup: Sequence[Dict[str, Any]]):
        DrawableListVertical.__init__(self, offset=0, bg_color=(0, 157, 255))
        self.master = master
        self.map = dict()
        for i in range(NB_LINES_BOXES):
            box_line = DrawableListHorizontal(offset=0)
            for j in range(NB_COLUMNS_BOXES):
                box = Box(master, navy=self, size=BOX_SIZE, pos=(i, j))
                box_line.add(box)
                self.map[(i, j)] = Navy.BOX_NO_HIT
            self.add(box_line)
        self.ships_list = DrawableList()
        self.box_hit_img = DrawableList()
        for ship_infos in setup:
            self.add_ship(Ship(**ship_infos))

    def after_drawing(self, surface: pygame.Surface) -> None:
        self.ships_list.draw(surface)
        self.box_hit_img.draw(surface)

    def add_ship(self, ship: Ship) -> None:
        self.ships_list.add(ship)
        self.move()

    def get_box(self, line: int, column: int) -> Box:
        return {box.pos: box for box in self.boxes}.get((line, column))

    def set_box_clickable(self, click: bool) -> None:
        for box in self.boxes:
            if click:
                box.enable_key_joy()
                box.enable_mouse()
            else:
                box.disable_key_joy()
                box.disable_mouse()
            box.hover = False

    def destroyed(self) -> bool:
        return len(self.ships) == 10 and all(ship.destroyed() for ship in self.ships)

    @property
    def boxes(self) -> Sequence[Box]:
        return self.drawable

    @property
    def ships(self) -> Sequence[Ship]:
        return self.ships_list.drawable

    def move(self, **kwargs):
        DrawableListVertical.move(self, **kwargs)
        for ship in self.ships:
            ship.place_ship(list(filter(lambda box: box.pos in ship.boxes_pos, self.boxes)))

    def box_hit(self, box: Box) -> bool:
        return False

    def set_box_hit(self, box: Box, img: str):
        box.state = Button.DISABLED
        image = Image(RESOURCES.IMG[img], size=box.size)
        image.center = box.center
        self.box_hit_img.add(image)
        self.map[box.pos] = {"hatch": Navy.BOX_HATCH, "cross": Navy.BOX_CROSS}[img]

    def hit_all_boxes_around_ship(self, ship: Ship):
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
        for box in ship.boxes_covered:
            line, column = box.pos
            self.map[box.pos] = Navy.BOX_SHIP_DESTROYED
            for u, v in offsets:
                box = self.get_box(line + u, column + v)
                if box is None:
                    continue
                if box.state == Button.NORMAL:
                    self.set_box_hit(box, "hatch")

class PlayerNavy(Navy):
    def __init__(self, master, player: Player, setup: Sequence[Dict[str, Any]]):
        Navy.__init__(self, master, setup)
        self.set_box_clickable(False)
        self.player = player

    def box_hit(self, box: Box) -> bool:
        for ship in self.ships:
            if box in ship.boxes_covered:
                self.set_box_hit(box, "cross")
                if ship.destroyed():
                    RESOURCES.play_sfx("destroy")
                    self.hit_all_boxes_around_ship(ship)
                    self.player.send("ship_destroyed", json.dumps(ship.get_setup()))
                else:
                    self.player.send("attack_success")
                    RESOURCES.play_sfx("explosion")
                return True
        self.player.send("attack_failed")
        RESOURCES.play_sfx("splash")
        self.set_box_hit(box, "hatch")
        return False

    def send_non_destroyed_ships(self):
        if self.player.connected():
            self.player.send("non_destroyed_ships", json.dumps([ship.get_setup() for ship in filter(lambda ship: not ship.destroyed(), self.ships)]))

class OppositeNavy(Navy):
    def __init__(self, master, player: Player, ai_setup: Sequence[Dict[str, Any]]):
        Navy.__init__(self, master, list())
        self.player = player
        self.ai_setup = ai_setup

    def box_hit(self, box: Box) -> bool:
        if not self.player.connected():
            return self.ai_box_hit(box)
        return self.player_box_hit(box)

    def ai_box_hit(self, box: Box) -> bool:
        for ship_infos in self.ai_setup.copy():
            boxes_covered = list(filter(lambda box: box.pos in ship_infos["boxes"], self.boxes))
            if box in boxes_covered:
                self.set_box_hit(box, "cross")
                if all(box.state == Button.DISABLED for box in boxes_covered):
                    RESOURCES.play_sfx("destroy")
                    ship = Ship(**ship_infos)
                    self.ai_setup.remove(ship_infos)
                    self.add_ship(ship)
                    self.hit_all_boxes_around_ship(ship)
                else:
                    RESOURCES.play_sfx("explosion")
                return True
        self.set_box_hit(box, "hatch")
        RESOURCES.play_sfx("splash")
        return False

    def player_box_hit(self, box: Box) -> bool:
        self.player.send("attack", json.dumps(box.pos))
        result, value = self.player.wait_for("attack_success", "attack_failed", "ship_destroyed")
        if result in ["attack_success", "ship_destroyed"]:
            self.set_box_hit(box, "cross")
            if result == "ship_destroyed":
                try:
                    ship_infos = json.loads(value)
                except json.JSONDecodeError:
                    pass
                else:
                    RESOURCES.play_sfx("destroy")
                    ship = Ship(**ship_infos)
                    self.add_ship(ship)
                    self.hit_all_boxes_around_ship(ship)
            else:
                RESOURCES.play_sfx("explosion")
            return True
        self.set_box_hit(box, "hatch")
        RESOURCES.play_sfx("splash")
        return False

    def show_all_non_destroyed_ships(self) -> Sequence[Ship]:
        if not self.player.connected():
            ship_setup = self.ai_setup
        else:
            ship_setup = json.loads(self.player.wait_for("non_destroyed_ships")[1])
        all_ships = list()
        for ship_infos in ship_setup:
            ship = Ship(**ship_infos)
            self.add_ship(ship)
            all_ships.append(ship)
            for box in ship.boxes_covered:
                box.hover = False
                box.state = Button.NORMAL
        return all_ships

class TurnArrow(Image):
    def __init__(self, default: bool, **kwargs):
        self.arrow = {
            True: RESOURCES.IMG["green_triangle"],
            False: RESOURCES.IMG["red_triangle"]
        }
        self.__turn = True
        Image.__init__(self, self.arrow[self.__turn], **kwargs)
        self.turn = default

    @property
    def turn(self) -> bool:
        return self.__turn

    @turn.setter
    def turn(self, state: bool) -> None:
        self.__turn = bool(state)
        self.load(self.arrow[self.__turn], keep_width=True, keep_height=True)

class AI:
    def __init__(self):
        self.box_hitted = list()
        self.possibilities = [(i, j) for i in range(NB_LINES_BOXES) for j in range(NB_COLUMNS_BOXES)]

    def play(self, navy_map: Dict[Tuple[int, int], int]) -> Tuple[int, int]:
        for box_pos in filter(lambda pos: navy_map[pos] == Navy.BOX_SHIP_DESTROYED, self.box_hitted.copy()):
            self.box_hitted.remove(box_pos)
        for box_pos in filter(lambda pos: navy_map[pos] != Navy.BOX_NO_HIT, self.possibilities.copy()):
            if navy_map[box_pos] == Navy.BOX_CROSS:
                self.box_hitted.append(box_pos)
            self.possibilities.remove(box_pos)
        if self.box_hitted:
            return self.track_ship(navy_map)
        return random.choice(self.possibilities)

    def track_ship(self, navy_map: Dict[Tuple[int, int], int]) -> Tuple[int, int]:
        if len(self.box_hitted) == 1:
            return self.find_ship(navy_map, *self.box_hitted[0])
        self.box_hitted.sort()
        index = 1 if self.box_hitted[0][0] == self.box_hitted[-1][0] else 0
        first, second = list(self.box_hitted[0]), list(self.box_hitted[-1])
        first[index] -= 1
        second[index] += 1
        potential_boxes = list()
        for x, y in [first, second]:
            if (x, y) in navy_map and navy_map[x, y] == Navy.BOX_NO_HIT:
                potential_boxes.append((x, y))
        return random.choice(potential_boxes)

    def find_ship(self, navy_map: Dict[Tuple[int, int], int], line: int, column: int) -> Tuple[int, int]:
        offsets = [
            (0, -1),
            (-1, 0),
            (1, 0),
            (0, 1)
        ]
        potential_boxes = list()
        for pos in [(line + u, column + v) for u, v in offsets]:
            if pos in navy_map and navy_map[pos] == Navy.BOX_NO_HIT:
                potential_boxes.append(pos)
        if not potential_boxes:
            navy_list = [[0 for _ in range(NB_COLUMNS_BOXES)] for _ in range(NB_LINES_BOXES)]
            for (l, c), value in navy_map.items():
                navy_list[l][c] = value if (l, c) != (line, column) else f"({value})"
            for line in navy_list:
                print(line)
            print(f"IndexError: {e}")
            exit(1)
        return random.choice(potential_boxes)

class FinishWindow(Window):
    def __init__(self, master, victory: bool):
        Window.__init__(self, master=master, bg_music=None if victory is None else RESOURCES.MUSIC["end"])
        self.master = master
        self.bg = RectangleShape(self.width, self.height, (0, 0, 0, 170))
        self.frame = RectangleShape(0.5 * self.width, 0.5 * self.height, GREEN_DARK, outline=2)
        self.victory = victory
        if victory is not None:
            message = "{winner} won".format(winner="You" if victory else "Enemy")
        else:
            message = "The enemy has left\nthe game"
        self.text_finish = Text(message, font=(None, 70))
        params_for_all_buttons = {
            "font": (None, 40),
            "bg": GREEN,
            "hover_bg": GREEN_LIGHT,
            "active_bg": GREEN_DARK,
            "highlight_color": YELLOW
        }
        self.button_restart = Button(self, "Restart", callback=self.restart, **params_for_all_buttons)
        self.button_return_to_menu = Button(self, "Return to menu", callback=self.stop, **params_for_all_buttons)
        self.ask_restart = False
        self.bind_key(pygame.K_ESCAPE, lambda event: self.stop())

    def update(self):
        if self.ask_restart:
            if self.master.player.recv("restart"):
                self.master.restart = True
                self.stop()
            elif self.master.player.recv("quit"):
                self.text_finish.message = "The enemy has left\nthe game"

    def place_objects(self):
        self.frame.center = self.center
        self.text_finish.center = self.frame.center
        if self.victory is not None:
            self.button_restart.move(bottom=self.frame.bottom - 20, centerx=self.frame.centerx - (self.frame.w // 4))
            self.button_return_to_menu.move(bottom=self.frame.bottom - 20, centerx=self.frame.centerx + (self.frame.w // 4))
        else:
            self.button_restart.hide()
            self.button_return_to_menu.move(bottom=self.frame.bottom - 20, centerx=self.frame.centerx)

    def restart(self):
        if self.master.player.connected():
            self.ask_restart = True
            self.master.player.send("restart")
            self.text_finish.message = "Waiting for\nenemy response"
            self.button_restart.hide()
            self.button_return_to_menu.move(bottom=self.frame.bottom - 20, centerx=self.frame.centerx)
        else:
            self.master.restart = True
            self.stop()

class Gameplay(Window):
    def __init__(self, player: Player, navy_setup: Sequence[Dict[str, Any]], ai_setup=None):
        Window.__init__(self, bg_color=(0, 200, 255), bg_music=RESOURCES.MUSIC["gameplay"])
        self.player = player
        self.button_back = ImageButton(self, RESOURCES.IMG["arrow_blue"], rotate=180, size=50, callback=self.stop, highlight_color=YELLOW)
        self.player_grid = PlayerNavy(self, player, navy_setup)
        self.opposite_grid = OppositeNavy(self, player, ai_setup or list())
        self.ai = AI() if not player.connected() else None
        self.turn_checker = TurnArrow(self.player.get_default_turn())
        self.restart = False
        self.bind_key(pygame.K_ESCAPE, lambda event: self.stop())
        self.text_finish = Text("Finish !!!", font=(None, 120), color=WHITE)
        self.game_finished = False

    def update(self):
        self.text_finish.set_visibility(self.game_finished)
        if self.game_finished:
            return
        if self.player_grid.destroyed():
            self.opposite_grid.set_box_clickable(False)
            self.highlight_ships(self.opposite_grid.show_all_non_destroyed_ships())
            self.after(3000, lambda victory=False: self.finish(victory))
            self.game_finished = True
        elif self.opposite_grid.destroyed():
            self.opposite_grid.set_box_clickable(False)
            self.player_grid.send_non_destroyed_ships()
            self.after(3000, lambda victory=True: self.finish(victory))
            self.game_finished = True
        elif self.player.connected():
            if self.player.recv("attack"):
                self.hit_a_box(self.player_grid, json.loads(self.player.get()))
            elif self.player.recv("quit"):
                self.finish(None)

    def finish(self, victory: bool):
        FinishWindow(self, victory).mainloop()
        self.stop()

    def highlight_ships(self, ships: Sequence[Ship]):
        for ship in ships:
            for box in ship.boxes_covered:
                box.hover = not box.hover
        self.after(500, lambda: self.highlight_ships(ships))

    def place_objects(self):
        self.button_back.move(x=20, y=20)
        self.text_finish.move(y=20, centerx=self.centerx)
        self.player_grid.move(x=20, centery=self.centery)
        self.opposite_grid.move(right=self.right - 20, centery=self.centery)
        self.turn_checker.set_width(self.opposite_grid.left - self.player_grid.right - 150)
        self.turn_checker.move(center=self.center)

    def hit_a_box(self, navy: Navy, box: Union[Tuple[int, int], Box]):
        if isinstance(box, (list, tuple)):
            box = navy.get_box(*box)
        hitted = navy.box_hit(box)
        if navy.destroyed():
            return
        turn = hitted if navy == self.opposite_grid else not hitted
        if turn is False:
            self.opposite_grid.set_box_clickable(False)
        wait_time = 1000 if turn != self.turn_checker.turn else 0
        self.after(wait_time, lambda: self.set_turn(turn))

    def set_turn(self, turn: bool):
        self.turn_checker.turn = turn
        if self.turn_checker.turn is True:
            self.opposite_grid.set_box_clickable(True)
        if self.turn_checker.turn is False and isinstance(self.ai, AI) and not self.player_grid.destroyed():
            self.after(1000, lambda: self.hit_a_box(self.player_grid, self.ai.play(self.player_grid.map)))