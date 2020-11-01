# -*- coding: Utf-8 -*

import pygame
from .drawable import Drawable

class Image(Drawable):

    def __init__(self, surface: pygame.Surface, size=None, width=None, height=None, **kwargs):
        Drawable.__init__(self, surface=surface, **kwargs)
        self.__handle_img_size(size, width, height)

    def load(self, surface: pygame.Surface, keep_width=False, keep_height=False) -> None:
        width = height = None
        if keep_width and keep_height:
            width, height = self.size
        elif keep_width:
            width = self.width
        elif keep_height:
            height = self.height
        self.image = surface
        self.__handle_img_size(None, width, height)

    def __handle_img_size(self, size, width, height):
        w, h = self.size
        if size is not None:
            self.set_size(size)
        elif width is not None and height is not None:
            if w > width:
                self.set_width(width)
            if h > height:
                self.set_height(height)
        elif width is not None:
            self.set_width(width)
        elif height is not None:
            self.set_height(height)