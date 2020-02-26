# -*- coding: Utf-8 -*

import time
import pygame

class Window:
    def __init__(self, size=(1920, 1080), flags=0, fps=30, bg_color=(0, 0, 0)):
        self.window = pygame.display.get_surface()
        if self.window is None:
            self.window = pygame.display.set_mode(tuple(size), flags)
        self.window_rect = self.window.get_rect()
        self.main_clock = pygame.time.Clock()
        self.loop = False
        self.objects = list()
        self.event_handler_dict = dict()
        self.mouse_handler = list()
        self.fps = fps
        self.bg_color = bg_color
        self.time_after = 0
        self.time_start = 0
        self.callback_after = None

    def mainloop(self):
        self.loop = True
        while self.loop:
            self.main_clock.tick(self.fps)
            self.draw_screen()
            self.event_handler()

    def stop(self):
        self.on_quit()
        self.loop = False

    def on_quit(self):
        pass

    def draw_screen(self):
        self.window.fill(self.bg_color)
        for obj in self.objects:
            obj.draw(self.window)
        pygame.display.flip()

    def __setattr__(self, name, obj):
        if hasattr(obj, "draw"):
            self.objects.append(obj)
        return object.__setattr__(self, name, obj)

    def event_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT \
            or (event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_q)):
                self.loop = False
            event_list = self.event_handler_dict.get(event.type, list())
            for callback in event_list:
                callback(event)
        for callback in self.mouse_handler:
            callback(pygame.mouse.get_pos())
        if not self.time_after:
            return
        if time.time() - self.time_start >= (self.time_after / 1000):
            self.time_after = 0
            self.callback_after()

    def after(self, clock: float, callback):
        self.time_after = clock
        self.time_start = time.time()
        self.callback_after = callback

    def bind_event(self, event_type, callback):
        event_list = self.event_handler_dict.get(event_type)
        if event_list is None:
            event_list = self.event_handler_dict[event_type] = list()
        event_list.append(callback)

    def bind_mouse(self, callback):
        self.mouse_handler.append(callback)