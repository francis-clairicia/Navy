# -*- coding: Utf-8 -*

import socket
import select
import random
from typing import Optional, Any
from threading import Thread

class Player(Thread):

    def __init__(self, player_socket: socket.socket, player_id: int):
        Thread.__init__(self, daemon=True)
        self.__socket = player_socket
        self.__id = int(player_id)
        self.__loop = False
        self.__ready = False
        self.__msg = dict()
        self.__last = None
        self.__spliter = "=|="

    def run(self) -> None:
        if self.__socket is None:
            return
        self.__loop = True
        while self.__loop:
            try:
                read_socket = bool(len(select.select([self.__socket], [], [], 0.05)[0]) > 0)
            except (socket.error, ValueError, TypeError):
                read_socket = False
            finally:
                if not read_socket:
                    continue
                try:
                    msg = self.__socket.recv(4096)
                except:
                    msg = None
                if msg is None:
                    continue
                msg = msg.decode().split(self.__spliter)
                if len(msg) == 2:
                    self.__msg[msg[0]] = msg[1]

    def stop(self) -> None:
        if self.__loop:
            self.__loop = False
            self.join()
            if self.__socket is not None:
                self.send("quit")
                self.__socket.close()
                self.__socket = None

    def connected(self) -> bool:
        return bool(self.__socket is not None)

    def get_default_turn(self) -> bool:
        if not self.connected():
            return True
        if self.__id == 1:
            my_turn = random.choice([True, False])
            self.send("turn", "no" if my_turn else "yes")
            return my_turn
        result, my_turn = self.wait_for("turn")
        if result == "quit":
            return False
        return bool(my_turn == "yes")

    def send(self, key: str, value: Optional[Any] = "yes") -> int:
        if not self.connected():
            return -1
        try:
            data = f"{key}{self.__spliter}{value}"
            written = self.__socket.send(data.encode())
        except:
            self.__msg["quit"] = "yes"
            self.stop()
            written = -1
        return written

    def recv(self, msg: str) -> (str, None):
        self.__last = self.__msg.pop(msg, None)
        return self.get()

    def get(self) -> (str, None):
        return self.__last

    def wait_for(self, *messages: str) -> str:
        while not self.recv("quit"):
            if not self.connected():
                break
            for msg in messages:
                if self.recv(msg):
                    return msg, self.get()
        return "quit", self.get()