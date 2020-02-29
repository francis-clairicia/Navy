# -*- coding: Utf-8 -*

import sys
import time
import pygame

class Window:

    def __init__(self, size=(1920, 1080), flags=0, fps=30, bg_color=(0, 0, 0)):
        if not pygame.get_init():
            status = pygame.init()
            if status[1] > 0:
                sys.exit(84)
        self.window = pygame.display.get_surface()
        self.main_window = False
        if self.window is None:
            self.window = pygame.display.set_mode(tuple(size), flags)
            self.main_window = True
        self.window_rect = self.window.get_rect()
        self.main_clock = pygame.time.Clock()
        self.loop = False
        self.objects = list()
        self.event_handler_dict = dict()
        self.key_handler_dict = dict()
        self.mouse_handler_list = list()
        self.fps = fps
        self.bg_color = bg_color
        self.time_after = -1
        self.time_start = 0
        self.callback_after = None
        self.bind_key(pygame.K_ESCAPE, lambda key: self.stop())
        self.bind_key(pygame.K_q, lambda key: self.stop())

    def __setattr__(self, name, obj):
        if hasattr(obj, "draw"):
            if hasattr(self, name):
                delattr(self, name)
            self.add(obj)
        return object.__setattr__(self, name, obj)

    def __delattr__(self, name):
        obj = getattr(self, name)
        self.remove(obj)
        return object.__delattr__(self, name)

    def add(self, obj):
        self.objects.append(obj)

    def remove(self, obj):
        try:
            self.objects.remove(obj)
        except ValueError:
            return

    @property
    def end_list(self):
        return len(self.objects)

    def set_object_priority(self, obj, new_pos, relative_to=None):
        former_pos = self.objects.index(obj)
        del self.objects[former_pos]
        if relative_to is not None:
            new_pos += self.objects.index(relative_to)
        self.objects.insert(new_pos, obj)

    def set_icon(self, icon_filepath):
        icon = pygame.image.load(icon_filepath).convert_alpha()
        pygame.display.set_icon(icon)

    def set_title(self, title: str):
        pygame.display.set_caption(title)

    def mainloop(self, fill_bg=True):
        self.loop = True
        if self.time_after >= 0:
            self.time_start = time.time()
        while self.loop:
            self.main_clock.tick(self.fps)
            self.draw_screen(fill_bg)
            self.refresh()
            self.event_handler()
            self.mouse_handler()

    def stop(self, force=False):
        self.on_quit()
        self.loop = False
        if self.main_window or force:
            pygame.quit()
            sys.exit(0)

    def on_quit(self):
        pass

    def draw_screen(self, fill=True):
        if fill:
            self.window.fill(self.bg_color)
        for obj in self.objects:
            obj.draw(self.window)

    @staticmethod
    def refresh():
        pygame.display.flip()

    def event_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stop(force=True)
            if event.type == pygame.KEYDOWN:
                self.key_handler(event.key)
            event_list = self.event_handler_dict.get(event.type, list())
            for callback in event_list:
                callback(event)
        if self.time_after < 0:
            return
        if time.time() - self.time_start >= (self.time_after / 1000):
            self.time_after = -1
            self.callback_after()

    def mouse_handler(self):
        for callback in self.mouse_handler_list:
            callback(pygame.mouse.get_pos())

    def key_handler(self, key_value):
        key_list = self.key_handler_dict.get(key_value, list())
        for callback in key_list:
            callback(key_value)

    def after(self, milliseconds: float, callback):
        self.time_after = milliseconds
        self.time_start = time.time()
        self.callback_after = callback

    def bind_event(self, event_type, callback):
        event_list = self.event_handler_dict.get(event_type)
        if event_list is None:
            event_list = self.event_handler_dict[event_type] = list()
        event_list.append(callback)

    def bind_mouse(self, callback):
        self.mouse_handler_list.append(callback)

    def bind_key(self, key_value, callback):
        key_list = self.key_handler_dict.get(key_value)
        if key_list is None:
            key_list = self.key_handler_dict[key_value] = list()
        key_list.append(callback)