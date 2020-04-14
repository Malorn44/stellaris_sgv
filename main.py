import json
import sys
from converter import savToJson
from utils import System, Planet
from interface import Zoom_Advanced

import tkinter as tk
from tkinter import ttk


# data = savToJson("test_save.sav")['gamestate']

with open('data.json') as f:

    systems = []
    planets = []

    minx, miny = sys.maxsize, sys.maxsize
    maxx, maxy = -1*sys.maxsize, -1*sys.maxsize

    data = json.load(f)['gamestate']

    ### Populating planets list
    for key,val in data['planets']['planet'].items():
        planets.append(Planet(val))

    ### Populating systems list
    for key,val in data['galactic_object'].items():
        x = val['coordinate']['x']
        y = val['coordinate']['y']

        # updating max and min positions
        minx = min(minx, x)
        miny = min(miny, x)
        maxx = max(maxx, x)
        maxy = max(maxy, y)

        systems.append(System(val))
        
        for ID in systems[-1].planet_ids:
            systems[-1].addPlanet(planets[ID])

    ### Setting BBox corners
    bbox = (minx, miny, maxx, maxy)



    for i in range(3):
        print(systems[i].toString())

    root = tk.Tk()
    app = Zoom_Advanced(root, systems, bbox)
    root.mainloop()

