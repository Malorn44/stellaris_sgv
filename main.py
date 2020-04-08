import json
import sys
from converter import savToJson
from utils import System
from interface import Zoom_Advanced

import tkinter as tk
from tkinter import ttk


# data = savToJson("test_save.sav")['gamestate']

with open('data.json') as f:
    data = json.load(f)['gamestate']
    locs = []
    minx, miny = sys.maxsize, sys.maxsize
    maxx, maxy = -1*sys.maxsize, -1*sys.maxsize
    for key,val in data['galactic_object'].items():
        x = val['coordinate']['x']
        y = val['coordinate']['y']

        minx = min(minx, x)
        miny = min(miny, x)
        maxx = max(maxx, x)
        maxy = max(maxy, y)

        locs.append((x,y))


    # x = System(1)
    # x.print()

    root = tk.Tk()
    app = Zoom_Advanced(root, locs, minx, miny, maxx, maxy)
    root.mainloop()




