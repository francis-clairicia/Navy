# -*- coding: Utf-8 -*

import pygame
from pygame.font import Font, SysFont
from pygame.sprite import Sprite
try:
    from window import Window
except ImportError:
    from my_pygame.window import Window

class Drawable(Sprite):
    def __init__(self, surface=pygame.Surface((0, 0)), **kwargs):
        Sprite.__init__(self)
        self.image = surface
        self.draw_sprite = True
        self.move(**kwargs)

    def fill(self, color):
        self.image.fill(color)

    def show(self):
        self.draw_sprite = True

    def hide(self):
        self.draw_sprite = False

    def is_shown(self):
        return self.draw_sprite

    @property
    def image(self):
        return self.__surface

    @image.setter
    def image(self, surface):
        x = self.rect.x if hasattr(self, "rect") else 0
        y = self.rect.y if hasattr(self, "rect") else 0
        self.__surface = surface
        self.rect = surface.get_rect(x=x, y=y)

    def draw(self, surface):
        if self.draw_sprite:
            surface.blit(self.image, self.rect)

    def move(self, **kwargs):
        self.rect = self.image.get_rect(**kwargs)
        return self.rect

    def set_size(self, *args):
        size = args if len(args) == 2 else args[0]
        self.image = pygame.transform.smoothscale(self.image, size)

    def set_width(self, width):
        height = round(self.rect.h * width / self.rect.w)
        self.set_size(width, height)

    def set_height(self, height):
        width = round(self.rect.w * height / self.rect.h)
        self.set_size(width, height)

    left = property(lambda self: self.rect.left)
    right = property(lambda self: self.rect.right)
    top = property(lambda self: self.rect.top)
    bottom = property(lambda self: self.rect.bottom)
    x = left
    y = top
    size = property(lambda self: self.rect.size)
    width = property(lambda self: self.rect.width)
    height = property(lambda self: self.rect.height)
    w = width
    h = height
    center = property(lambda self: self.rect.center)
    centerx = property(lambda self: self.rect.centerx)
    centery = property(lambda self: self.rect.centery)
    topleft = property(lambda self: self.rect.topleft)
    topright = property(lambda self: self.rect.topright)
    bottomleft = property(lambda self: self.rect.bottomleft)
    bottomright = property(lambda self: self.rect.bottomright)
    midtop = property(lambda self: self.rect.midtop)
    midbottom = property(lambda self: self.rect.midbottom)
    midleft = property(lambda self: self.rect.midleft)
    midright = property(lambda self: self.rect.midright)

class Image(Drawable):
    def __init__(self, filepath: str, size=None, rotate=0, **kwargs):
        Drawable.__init__(self, pygame.image.load(filepath).convert_alpha())
        if size is not None:
            self.set_size(size)
        while not 0 <= rotate < 360:
            rotate += 360 if rotate < 0 else -360
        if rotate != 0:
            self.rotate(rotate)
        self.move(**kwargs)

    def rotate(self, angle):
        self.image = pygame.transform.rotate(self.image, angle)

class Text(Drawable):
    def __init__(self, text: str, font, color: tuple, **kwargs):
        if isinstance(font, (tuple, list)):
            if str(font[0]).endswith((".ttf", ".otf")):
                self.font = Font(*font)
            else:
                self.font = SysFont(*font)
        else:
            self.font = font
        self.text = str(text)
        self.color = color
        Drawable.__init__(self, self.font.render(self.text, True, self.color), **kwargs)

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
    def __init__(self, size: tuple, color: tuple, outline=0, outline_color=(0, 0, 0), **kwargs):
        Drawable.__init__(self, surface=pygame.Surface(size), **kwargs)
        self.color = color
        self.outline = outline
        self.outline_color = outline_color

    def draw(self, surface):
        if self.draw_sprite:
            self.draw_shape(surface)

    def draw_shape(self, surface):
        surface.blit(self.image, self.rect)
        if self.outline > 0:
            pygame.draw.rect(surface, self.outline_color, self.rect, self.outline)
        return self.rect

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
                 outline=2, outline_color=(0, 0, 0),
                 over_bg=(128, 128, 128), over_fg=None,
                 active_bg=(235, 235, 235), active_fg=None,
                 **kwargs):
        if font is None:
            font = SysFont(pygame.font.get_default_font(), 15)
        self.text = Text(text, font, fg)
        size = (self.text.w + 20, self.text.h + 20)
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
        if self.draw_sprite:
            self.draw_shape(surface)
            self.text.move(center=self.center)
            self.text.draw(surface)

    def mouse_click_up(self, event):
        if not self.active:
            return
        self.active = False
        self.on_click_up()
        if self.rect.collidepoint(event.pos) and self.callback is not None:
            self.callback()

    def mouse_click_down(self, event):
        if self.rect.collidepoint(event.pos):
            self.active = True
            self.on_click_down()

    def mouse_motion(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.color = self.over_bg if self.active else self.active_bg
            self.text.set_color(self.over_fg if self.active else self.active_fg)
        else:
            self.color = self.bg
            self.text.set_color(self.fg)

    def on_click_down(self):
        pass

    def on_click_up(self):
        pass

class ImageButton(Button):

    def __init__(self, master: Window, image: Image, show_bg=False, **kwargs):
        Button.__init__(self, master, str(), **kwargs)
        self.image_button = image
        self.show_background(show_bg)
        size = (self.image_button.w + 20, self.image_button.h + 20)
        self.offset = [0, 0]
        self.set_size(size)

    def show_background(self, status: bool):
        self._show = bool(status)

    def draw(self, surface):
        if self.draw_sprite:
            if self._show:
                self.draw_shape(surface)
            self.image_button.move(center=self.center)
            self.image_button.rect.move_ip(*self.offset)
            self.image_button.draw(surface)

    def on_click_up(self):
        if not self._show:
            self.offset[1] = 0

    def on_click_down(self):
        if not self._show:
            self.offset[1] = 3

class Entry(RectangleShape):
    def __init__(self, master: Window, font=None, width=10, bg=(255, 255, 255), fg=(0, 0, 0),
                 highlight_color=(128, 128, 128), **kwargs):
        self.text = Text("".join("1" for _ in range(width)), font, fg)
        size = (self.text.w + 20, self.text.h + 20)
        RectangleShape.__init__(self, size, bg, **kwargs)
        self.text.set_string("")
        self.nb_chars = width
        self.default_color = self.outline_color
        self.highlight_color = highlight_color
        self.focus = False
        master.bind_event(pygame.MOUSEBUTTONUP, self.focus_set)
        master.bind_event(pygame.KEYDOWN, self.key_press)

    def draw(self, surface):
        if self.draw_sprite:
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
        elif len(text) < self.nb_chars:
            self.text.set_string(text + event.unicode)

    def focus_set(self, event):
        self.focus = self.rect.collidepoint(event.pos)
        self.outline_color = self.default_color if not self.focus else self.highlight_color