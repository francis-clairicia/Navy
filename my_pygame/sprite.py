# -*- coding: Utf-8 -*

import itertools
from typing import List, Union, Dict
import pygame
from .surface import create_surface
from .drawable import Drawable
from .image import Image
from .clock import Clock

class Sprite(Drawable):

    def __init__(self):
        Drawable.__init__(self)
        self.__sprites = dict()
        self.__sprite_list = list()
        self.__nb_sprites = 0
        self.__sprite_idx = 0
        self.__clock = Clock()
        self.__wait_time = 0
        self.__animation = False
        self.__loop = False

    def get_sprite_dict(self) -> Dict[str, List[Image]]:
        return self.__sprites

    def get_actual_sprite_list(self) -> List[Image]:
        return self.__sprite_list

    def get_sprite_list(self, name: str) -> List[Image]:
        return self.__sprites.get(str(name), list())

    def get_all_sprites(self) -> List[Image]:
        return list(itertools.chain.from_iterable(self.__sprites.values()))

    def add_sprite(self, name: str, img: pygame.Surface, set_sprite=False, **kwargs) -> None:
        if not isinstance(img, pygame.Surface):
            return
        name = str(name)
        self.__sprites[name] = [Image(img, **kwargs)]
        if set_sprite:
            self.set_sprite_list(name)

    def add_sprite_list(self, name: str, img_list: List[pygame.Surface], set_sprite_list=False, **kwargs) -> None:
        if not img_list or any(not isinstance(obj, pygame.Surface) for obj in img_list):
            return
        name = str(name)
        self.__sprites[name] = sprite_list = list()
        for surface in img_list:
            sprite_list.append(Image(surface, **kwargs))
        if set_sprite_list:
            self.set_sprite_list(name)

    def add_spritesheet(self, name: str, img: pygame.Surface, rect_list: List[pygame.Rect], set_sprite_list=False, **kwargs) -> None:
        if not isinstance(img, pygame.Surface) or not rect_list:
            return
        self.add_sprite_list(name, [img.subsurface(rect) for rect in rect_list], set_sprite_list=set_sprite_list, **kwargs)

    def set_sprite_list(self, name: str) -> None:
        self.__sprite_list = self.get_sprite_list(name)
        self.__nb_sprites = len(self.__sprite_list)
        self.__sprite_idx = 0
        if self.__nb_sprites > 0:
            self.image = self.__sprite_list[0]
        else:
            self.image = create_surface((0, 0))

    def resize_sprite_list(self, name: str, **kwargs) -> None:
        for sprite in self.get_sprite_list(name):
            sprite.image = sprite.resize_surface(sprite.image, **kwargs)

    def resize_all_sprites(self, **kwargs) -> None:
        for sprite in self.get_all_sprites():
            sprite.image = sprite.resize_surface(sprite.image, **kwargs)
        self.image = self.resize_surface(self.image, **kwargs)

    def set_size(self, *size, smooth=True) -> None:
        pass

    def set_width(self, width: float, smooth=True)-> None:
        pass

    def set_height(self, height: float, smooth=True) -> None:
        pass

    @property
    def ratio(self) -> float:
        return self.__wait_time

    @ratio.setter
    def ratio(self, value: float) -> None:
        self.__wait_time = float(value)

    def animated(self) -> bool:
        return bool(self.__animation and self.__nb_sprites > 0)

    def before_drawing(self, surface: pygame.Surface) -> None:
        if self.animated() and self.__clock.elapsed_time(self.__wait_time):
            self.__sprite_idx = (self.__sprite_idx + 1) % self.__nb_sprites
            self.image = self.__sprite_list[self.__sprite_idx]
            if self.__sprite_idx == 0 and not self.__loop:
                self.__animation = False

    def start_animation(self, loop=False) -> None:
        self.__loop = bool(loop)
        self.__sprite_idx = 0
        self.restart_animation()

    def restart_animation(self) -> None:
        self.__animation = True
        self.__clock.tick()

    def stop_animation(self) -> None:
        self.__animation = False