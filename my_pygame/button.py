# -*- coding: Utf-8 -*

from typing import Optional, Any, Callable
import pygame
from pygame.font import Font
from .image import Image
from .text import Text
from .shape import RectangleShape
from .clickable import Clickable
from .window import Window

class Button(Clickable, RectangleShape):
    def __init__(self, master: Window, text=str(), font=None, img=None, compound="left",
                 callback: Optional[Callable[..., Any]] = None, state="normal",
                 size=None, outline=2, outline_color=(0, 0, 0),
                 bg=(255, 255, 255), fg=(0, 0, 0),
                 hover_bg=(235, 235, 235), hover_fg=None, hover_sound=None,
                 active_bg=(128, 128, 128), active_fg=None, on_click_sound=None,
                 disabled_bg=(128, 128, 128), disabled_fg=None, disabled_sound=None,
                 disabled_hover_bg=None, disabled_hover_fg=None,
                 disabled_active_bg=None, disabled_active_fg=None,
                 highlight_color=(0, 0, 255),
                 **kwargs):
        self.text = Text(text, font, fg, justify=Text.T_CENTER, img=img, compound=compound)
        if not isinstance(size, (list, tuple)) or len(size) != 2:
            size = (self.text.w + 20, self.text.h + 20)
        RectangleShape.__init__(self, *size, color=bg, outline=outline, outline_color=outline_color, **kwargs)
        self.fg = fg
        self.bg = bg
        self.hover_fg = fg if hover_fg is None else hover_fg
        self.hover_bg = bg if hover_bg is None else hover_bg
        self.active_fg = fg if active_fg is None else active_fg
        self.active_bg = bg if active_bg is None else active_bg
        self.disabled_fg = fg if disabled_fg is None else disabled_fg
        self.disabled_bg = bg if disabled_bg is None else disabled_bg
        self.disabled_hover_bg = self.disabled_bg if disabled_hover_bg is None else disabled_hover_bg
        self.disabled_hover_fg = self.disabled_fg if disabled_hover_fg is None else disabled_hover_fg
        self.disabled_active_bg = self.disabled_bg if disabled_active_bg is None else disabled_active_bg
        self.disabled_active_fg = self.disabled_fg if disabled_active_fg is None else disabled_active_fg
        Clickable.__init__(self, master, callback, state, hover_sound, on_click_sound, disabled_sound, highlight_color=highlight_color)

    def set_text(self, string: str) -> None:
        self.text.message = string
        self.set_size(self.text.w + 20, self.text.h + 20)

    def get_text(self) -> str:
        return self.text.message

    def set_font(self, font) -> None:
        self.text.font = font
        self.set_size(self.text.w + 20, self.text.h + 20)

    def get_font(self) -> Font:
        return self.text.font

    @property
    def img(self):
        return self.text.img

    @img.setter
    def img(self, img: Image):
        self.text.img = img
        self.set_size(self.text.w + 20, self.text.h + 20)

    def after_drawing(self, surface: pygame.Surface) -> None:
        RectangleShape.after_drawing(self, surface)
        self.text.move(center=self.center)
        self.text.draw(surface)

    def on_hover(self) -> None:
        if self.state == Clickable.DISABLED:
            bg = self.disabled_hover_bg if not self.active else self.disabled_active_bg
            fg = self.disabled_hover_fg if not self.active else self.disabled_active_fg
        else:
            bg = self.hover_bg if not self.active else self.active_bg
            fg = self.hover_fg if not self.active else self.active_fg
        self.color = bg
        self.text.color = fg

    def on_leave(self) -> None:
        self.set_default_colors()

    def on_change_state(self) -> None:
        if self.hover:
            self.on_hover()
        elif self.active:
            self.on_active_set()
        else:
            self.set_default_colors()

    def set_default_colors(self):
        if self.state == Clickable.DISABLED:
            bg = self.disabled_bg
            fg = self.disabled_fg
        else:
            bg = self.bg
            fg = self.fg
        self.color = bg
        self.text.color = fg

    def on_active_set(self) -> None:
        if self.state == Clickable.DISABLED:
            bg = self.disabled_active_bg
            fg = self.disabled_active_fg
        else:
            bg = self.active_bg
            fg = self.active_fg
        self.color = bg
        self.text.color = fg

    def on_active_unset(self) -> None:
        self.set_default_colors()

class ImageButton(Button):

    def __init__(self, master, img: pygame.Surface, hover_img: Optional[pygame.Surface] = None, active_img: Optional[pygame.Surface] = None, size=None, width=None, height=None, rotate=0, show_bg=False, offset=3, **kwargs):
        Button.__init__(self, master, img=Image(img, size=size, width=width, height=height, rotate=rotate), compound="center", **kwargs)
        self.default_img = self.img
        self.hover_img = Image(hover_img, size=size, width=width, height=height, rotate=rotate) if isinstance(hover_img, pygame.Surface) else None
        self.active_img = Image(active_img, size=size, width=width, height=height, rotate=rotate) if isinstance(active_img, pygame.Surface) else None
        self.show_background(show_bg)
        self.__offset = offset
        self.offset = 0

    def show_background(self, status: bool) -> None:
        self.__show = bool(status)

    def image_drawing_condition(self) -> bool:
        return self.__show

    def after_drawing(self, surface: pygame.Surface) -> None:
        if self.__show:
            RectangleShape.after_drawing(self, surface)
        self.text.move(center=self.center)
        self.text.move_ip(0, self.offset)
        self.text.draw(surface)

    def on_hover(self):
        Button.on_hover(self)
        if self.active_img and self.active:
            self.img = self.active_img
        elif self.hover_img and self.hover:
            self.img = self.hover_img
        else:
            self.img = self.default_img

    def on_active_set(self):
        Button.on_active_set(self)
        if self.active_img:
            self.img = self.active_img
        self.offset = self.__offset

    def on_active_unset(self):
        self.img = self.default_img
        self.offset = 0