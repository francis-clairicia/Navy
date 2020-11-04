# -*- coding:Utf-8 -*

import os
import sys
from cx_Freeze import setup, Executable

#############################################################################
# Recupération des valeurs

application = "navy"

app_globals = dict()

with open(os.path.join(application, "version.py")) as file:
    exec(file.read(), app_globals)

executable_infos = {
    "project_name": "Navy game",
    "description": "A python-based sea battle game",
    "author": "Francis Clairicia-Rose-Claire-Josephine",
    "version": app_globals["__version__"],
    "executables": [
        {
            "script": "run.pyw",
            "name": "Navy",
            "base": "Win32GUI",
            "icon": "resources/img/icon.ico"
        }
    ]
}

options = {
    "path": sys.path,
    "includes": [
        application,
        "pygame",
        "my_pygame",
        "my_pygame"
    ],
    "excludes": [],
    "include_files": [
        "resources",
    ],
    "optimize": 0,
    "silent": True
}

print("-----------------------------------{ cx_Freeze }-----------------------------------")
print("Project Name: {project_name}".format(**executable_infos))
print("Author: {author}".format(**executable_infos))
print("Version: {version}".format(**executable_infos))
print("Description: {description}".format(**executable_infos))
print()
for i, infos in enumerate(executable_infos["executables"], start=1):
    print(f"Executable number {i}")
    print("Name: {name}".format(**infos))
    print("Icon: {icon}".format(**infos))
    print()
print("Modules: {includes}".format(**options))
print("Additional files/folders: {include_files}".format(**options))
print()

while True:
    OK = input("Is this ok ? (y/n) : ").lower()
    if OK in ("y", "n"):
        break

if OK == "n":
    sys.exit(0)

print("-----------------------------------------------------------------------------------")

if "tkinter" not in options["includes"]:
    options["excludes"].append("tkinter")

# pour inclure sous Windows les dll system de Windows necessaires
if sys.platform == "win32":
    options["include_msvcr"] = True

#############################################################################
# preparation de la cible

executables = list()
for infos in executable_infos["executables"]:
    target = Executable(
        script=os.path.join(sys.path[0], infos["script"]),
        base=infos["base"] if sys.platform == "win32" else None,
        targetName=infos["name"] + ".exe",
        icon=infos.get("icon"),
        copyright=executable_infos.get("copyright")
    )
    executables.append(target)

#############################################################################
# creation du setup

sys.argv = [sys.argv[0], "build"]

try:
    result = str()
    setup(
        name=executable_infos["project_name"],
        version=executable_infos["version"],
        description=executable_infos["description"],
        author=executable_infos["author"],
        options={"build_exe": options},
        executables=executables
    )
except Exception as e:
    result = f"{e.__class__.__name__}: {e}"
else:
    result = "Build done"
finally:
    print("-----------------------------------------------------------------------------------")
    print(result)
    print("-----------------------------------------------------------------------------------")
    os.system("pause")