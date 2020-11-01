# -*- coding: Utf-8 -*

import pygame
from .drawable import Drawable

class RectangleShape(Drawable):

    def __init__(self, width: int, height: int, color: tuple, outline=0, outline_color=(0, 0, 0), **kwargs):
        Drawable.__init__(self, pygame.Surface((int(width), int(height)), flags=pygame.SRCALPHA), **kwargs)
        self.color = color
        self.outline = outline
        self.outline_color = outline_color

    def after_drawing(self, surface: pygame.Surface) -> None:
        if self.outline > 0:
            pygame.draw.rect(surface, self.outline_color, self.rect, self.outline)

    @property
    def color(self):
        return self.__color

    @color.setter
    def color(self, value: tuple):
        self.fill(value)
        self.__color = value

class CircleShape(Drawable):
    def __init__(self, radius: int, color: tuple, outline=0, outline_color=(0, 0, 0), **kwargs):
        Drawable.__init__(self, **kwargs)
        self.fill((0, 0, 0, 0))
        self.radius = radius
        self.color = color
        self.outline = outline
        self.outline_color = outline_color

    def after_drawing(self, surface: pygame.Surface) -> None:
        if self.outline > 0:
            pygame.draw.circle(surface, self.outline_color, self.center, self.radius, self.outline)

    @property
    def color(self):
        return self.__color

    @color.setter
    def color(self, value: tuple):
        self.__color = value
        self.__update_surface()

    @property
    def radius(self) -> int:
        return self.__radius

    @radius.setter
    def radius(self, value: int) -> None:
        self.__radius = int(value)
        self.__update_surface()

    def __update_surface(self):
        try:
            new_image = pygame.Surface((self.radius * 2, self.radius * 2), flags=pygame.SRCALPHA)
            new_image.fill((0, 0, 0, 0))
            if self.color:
                pygame.draw.circle(new_image, self.color, (self.radius, self.radius), self.radius)
            self.image = new_image
        except AttributeError:
            pass