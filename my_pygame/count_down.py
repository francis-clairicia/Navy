# -*- coding: Utf-8 -*

from .text import Text
from .window import Window

class CountDown(Text):

    __slots__ = ("__seconds", "__master", "__callback")

    def __init__(self, master: Window, seconds: int, format="{seconds}", *args, **kwargs):
        Text.__init__(self, str(), *args, **kwargs)
        self.__seconds = int(seconds)
        self.__time = 0
        self.__show = True
        self.__started = False
        self.__master = master
        self.__callback = None
        self.format = format
        self.hide()

    def start(self, at_end=None, show=True) -> None:
        self.__show = bool(show)
        if self.__show:
            self.show()
        self.__time = self.__seconds
        self.__started = True
        self.__callback = at_end if callable(at_end) else None
        self.__update_count()

    def stop(self) -> None:
        self.__started = False

    def started(self) -> bool:
        return self.__started

    def __update_count(self) -> None:
        if not self.__started:
            return
        if self.__time > 0:
            self.message = self.format.format(seconds=self.__time)
            self.__master.after(1000, self.__update_count)
            self.__time -= 1
        else:
            self.__end()

    def __end(self) -> None:
        self.hide()
        if callable(self.__callback):
            self.__callback()