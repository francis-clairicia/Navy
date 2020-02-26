# -*- coding: Utf-8 -*

import pygame
from pygame.font import Font, SysFont
from pygame.sprite import Sprite
try:
    from window import Window
except ImportError:
    from my_pygame.window import Window

class Drawable(Sprite):
    def __init__(self, surface=pygame.Surface((0, 0))):
        Sprite.__init__(self)
        self.image = surface
        self.draw_sprite = True

    @property
    def image(self):
        return self.__surface

    @image.setter
    def image(self, surface):
        self.__surface = surface
        self.rect = surface.get_rect()

    def draw(self, surface):
        if self.draw_sprite:
            surface.blit(self.image, self.rect)

    def move(self, **kwargs):
        self.rect = self.image.get_rect(**kwargs)
        return self.rect

class Image(Drawable):
    def __init__(self, filepath: str, size=None):
        Drawable.__init__(self, pygame.image.load(filepath).convert_alpha())
        if size is not None:
            if not isinstance(size, tuple) or len(size) != 2 or any(not isinstance(value, int) for value in size):
                raise TypeError("The size must be a tuple of integers of size 2")
            self.image = pygame.transform.smoothscale(self.image, size)
        self.rect = self.image.get_rect()

class Text(Drawable):
    def __init__(self, text: str, font, color: tuple):
        if isinstance(font, (tuple, list)):
            if str(font[0]).endswith((".ttf", ".otf")):
                self.font = Font(*font)
            else:
                self.font = SysFont(*font)
        else:
            self.font = font
        self.text = str(text)
        self.color = color
        Drawable.__init__(self, self.font.render(self.text, True, self.color))

    def get_string(self):
        return self.text

    def get_font(self):
        return self.font

    def refresh(self):
        save_x = self.rect.x
        save_y = self.rect.y
        self.image = self.font.render(self.text, True, self.color)
        self.move(x=save_x, y=save_y)

    def set_string(self, text: str):
        self.text = str(text)
        self.refresh()

    def set_color(self, color: tuple):
        self.color = tuple(color)
        self.refresh()

class RectangleShape(Drawable):
    def __init__(self, size: tuple, color: tuple, outline=0, outline_color=(0, 0, 0)):
        Drawable.__init__(self, surface=pygame.Surface(size))
        self.color = color
        self.outline = outline
        self.outline_color = outline_color

    def draw(self, surface):
        return self.draw_shape(surface)

    def draw_shape(self, surface):
        surface.blit(self.image, self.rect)
        if self.outline > 0:
            pygame.draw.rect(surface, self.outline_color, self.rect, self.outline)
        return self.rect

    def set_size(self, *args):
        save_center = self.rect.center
        self.image = pygame.Surface(args if len(args) == 2 else args[0])
        self.move(center=save_center)

    @property
    def color(self):
        return self.__color

    @color.setter
    def color(self, value: tuple):
        self.image.fill(value)
        self.__color = value


class Button(RectangleShape):
    def __init__(self, master: Window, text: str, font=None, command=None,
                 bg=(255, 255, 255), fg=(0, 0, 0),
                 outline=0, outline_color=(0, 0, 0),
                 over_bg=None, over_fg=None,
                 active_bg=None, active_fg=None):
        if font is None:
            font = SysFont(pygame.font.get_default_font(), 15)
        self.text = Text(text, font, fg)
        size = (self.text.rect.w + 20, self.text.rect.h + 20)
        RectangleShape.__init__(self, size, bg, outline, outline_color)
        self.fg = fg
        self.bg = bg
        self.over_fg = fg if over_fg is None else over_fg
        self.over_bg = bg if over_bg is None else over_bg
        self.active_fg = fg if active_fg is None else active_fg
        self.active_bg = bg if active_bg is None else active_bg
        self.callback = command
        self.active = False
        master.bind_event(pygame.MOUSEBUTTONDOWN, self.mouse_click_down)
        master.bind_event(pygame.MOUSEBUTTONUP, self.mouse_click_up)
        master.bind_mouse(self.mouse_motion)

    def draw(self, surface):
        self.draw_shape(surface)
        self.text.move(center=self.rect.center)
        self.text.draw(surface)

    @property
    def size(self):
        return self.rect.size

    def mouse_click_up(self, event):
        if not self.active:
            return
        self.active = False
        if self.rect.collidepoint(event.pos) and self.callback is not None:
            self.callback()

    def mouse_click_down(self, event):
        if self.rect.collidepoint(event.pos):
            self.active = True

    def mouse_motion(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.color = self.over_bg if self.active else self.active_bg
            self.text.set_color(self.over_fg if self.active else self.active_fg)
        else:
            self.color = self.bg
            self.text.set_color(self.fg)

class Entry(RectangleShape):
    def __init__(self, master: Window, font=None, width=10, bg=(255, 255, 255), fg=(0, 0, 0),
                 highlight_color=(128, 128, 128), **kwargs):
        self.text = Text("".join("1" for _ in range(width)), font, fg)
        size = (self.text.rect.w + 20, self.text.rect.h + 20)
        RectangleShape.__init__(self, size, bg, **kwargs)
        self.text.set_string("")
        self.width = width
        self.default_color = self.outline_color
        self.highlight_color = highlight_color
        self.focus = False
        master.bind_event(pygame.MOUSEBUTTONUP, self.focus_set)
        master.bind_event(pygame.KEYDOWN, self.key_press)

    def draw(self, surface):
        self.draw_shape(surface)
        self.text.move(left=self.rect.left + 10, centery=self.rect.centery)
        self.text.draw(surface)
        if self.focus:
            cursor_start = (self.text.rect.right + 2, self.text.rect.top)
            cursor_end = (self.text.rect.right + 2, self.text.rect.bottom)
            pygame.draw.line(surface, self.text.color, cursor_start, cursor_end, 2)

    def get(self):
        return self.text.get_string()

    def key_press(self, event):
        if not self.focus:
            return
        text = self.text.get_string()
        if event.key == pygame.K_BACKSPACE:
            self.text.set_string(text[:-1])
        elif len(text) < self.width:
            self.text.set_string(text + event.unicode)

    def focus_set(self, event):
        self.focus = self.rect.collidepoint(event.pos)
        self.outline_color = self.default_color if not self.focus else self.highlight_color