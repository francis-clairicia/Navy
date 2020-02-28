# -*- coding: Utf-8

import os
import sys

RESSOURCES_FOLDER = os.path.join(sys.path[0], "ressources")
IMG_FOLDER = os.path.join(RESSOURCES_FOLDER, "img")
if not os.path.isdir(RESSOURCES_FOLDER):
    raise FileNotFoundError("Ressources folder not present")
if not os.path.isdir(IMG_FOLDER):
    raise FileNotFoundError("Image folder not present")
IMG = {
    "icon": os.path.join(IMG_FOLDER, "icon.png"),
    "menu_bg": os.path.join(IMG_FOLDER, "menu_background.jpg"),
    "logo": os.path.join(IMG_FOLDER, "logo.png"),
    "grid": os.path.join(IMG_FOLDER, "grid.png"),
    "red_box": os.path.join(IMG_FOLDER, "red_box.png"),
    "green_box": os.path.join(IMG_FOLDER, "green_box.png"),
    "arrow_blue": os.path.join(IMG_FOLDER, "arrow.png"),
    "reload_blue": os.path.join(IMG_FOLDER, "reload_blue.png"),
    "random": os.path.join(IMG_FOLDER, "random.png"),
    "battleship": os.path.join(IMG_FOLDER, "battleship.png"),
    "destroyer": os.path.join(IMG_FOLDER, "destroyer.png"),
    "patroal_boat": os.path.join(IMG_FOLDER, "patroal_boat.png"),
    "carrier": os.path.join(IMG_FOLDER, "carrier.png")
}
for img in IMG.values():
    if not os.path.isfile(img):
        raise FileNotFoundError(f"{img} not found")