import json
import sys
from converter import savToJson
from utils import System, Planet, Deposit
from interface import Zoom_Advanced

import tkinter as tk
from tkinter import ttk


# data = savToJson("test_save.sav")['gamestate']

with open('data.json') as f:

    systems = []
    planets = []
    deposits = []

    minx, miny = sys.maxsize, sys.maxsize
    maxx, maxy = -1*sys.maxsize, -1*sys.maxsize

    data = json.load(f)['gamestate']

    ### Populating deposits list
    for key,val in data['deposit'].items():
        deposits.append(Deposit(val))

    ### Populating planets list
    for key,val in data['planets']['planet'].items():
        planets.append(Planet(val))

        for ID in planets[-1].deposit_ids:
            planets[-1].addDeposit(deposits[ID])

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

    root = tk.Tk()
    app = Zoom_Advanced(root, systems, bbox)
    root.mainloop()

