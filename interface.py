# -*- coding: utf-8 -*-
# Advanced zoom example. Like in Google Maps.
# It zooms only a tile, but not the whole image. So the zoomed tile occupies
# constant memory and not crams it with a huge resized image for the large zooms.
import random
import tkinter as tk
from tkinter import ttk
from tkinter import *
from PIL import Image, ImageTk
import easygui
import json
import sys
from converter import savToJson
from utils import Galaxy, System, Planet, Deposit
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.colors import Normalize



class AutoScrollbar(ttk.Scrollbar):
    ''' A scrollbar that hides itself if it's not needed.
        Works only if you use the grid geometry manager '''
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.grid_remove()
        else:
            self.grid()
            ttk.Scrollbar.set(self, lo, hi)

    def pack(self, **kw):
        raise tk.TclError('Cannot use pack with this widget')

    def place(self, **kw):
        raise tk.TclError('Cannot use place with this widget')

class Zoom_Advanced(ttk.Frame):
    ''' Advanced zoom of the image '''
    def __init__(self, mainframe, galaxy, BBox):
        ''' Initialize the main Frame '''
        ttk.Frame.__init__(self, master=mainframe)
        self.master.title('Stellaris SGV')
        # Vertical and horizontal scrollbars for canvas
        vbar = AutoScrollbar(self.master, orient='vertical')
        hbar = AutoScrollbar(self.master, orient='horizontal')
        vbar.grid(row=0, column=1, sticky='ns')
        hbar.grid(row=1, column=0, sticky='we')
        # Create canvas and put image on it
        self.canvas = tk.Canvas(self.master, highlightthickness=0,
                                xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        self.canvas.grid(row=0, column=0, sticky='nswe')
        self.canvas.update()  # wait till canvas is created
        vbar.configure(command=self.scroll_y)  # bind scrollbars to the canvas
        hbar.configure(command=self.scroll_x)
        
        # Make the canvas expandable
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)
        
        # Bind events to the Canvas
        self.canvas.bind('<Configure>', self.show_image)  # canvas is resized
        self.canvas.bind('<ButtonPress-1>', self.move_from)
        self.canvas.bind('<B1-Motion>',     self.move_to)
        self.canvas.bind('<MouseWheel>', self.wheel)  # with Windows and MacOS, but not Linux
        self.canvas.bind('<Button-5>',   self.wheel)  # only with Linux, wheel scroll down
        self.canvas.bind('<Button-4>',   self.wheel)  # only with Linux, wheel scroll up
        

        self.minx, self.miny = BBox[0], BBox[1]
        self.width, self.height = BBox[2], BBox[3]
        self.imscale = 1.0  # scale for the canvaas image
        self.delta = 1.3  # zoom magnitude
        
        # Put image into container rectangle and use it to set proper coordinates to the image
        self.container = self.canvas.create_rectangle(BBox[0]-5,BBox[1]-5,BBox[2]+5,BBox[3]+5, width=1)   
        
        self.draw_universe(galaxy)
        ImportButton(mainframe, 1)
        self.show_image()





    def convert_to_hex(self, rgba_color):
        red = int(rgba_color[0]*255)
        green = int(rgba_color[1]*255)
        blue = int(rgba_color[2]*255)
        hexcolor = '#{r:02x}{g:02x}{b:02x}'.format(r=red,g=green,b=blue)
        return hexcolor


    def draw_universe(self, galaxy):
        systems = galaxy.systems
        self.cmap = plt.cm.get_cmap('Spectral')

        for s in systems:
            for c in s.hyperlanes:
                p1 = s.pos
                p2 = systems[c].pos
                self.canvas.create_line(p1[0], p1[1], p2[0], p2[1])

        for s in systems:
            p = s.pos

            norm = matplotlib.colors.Normalize(vmin=self.minx, vmax=self.width)
            normed = norm(p[0])
            rgba = self.cmap(normed)
            color = self.convert_to_hex(rgba)
            if "Faranis" in s.name:
                print(p)

            self.canvas.create_circle(p[0], p[1], 5, fill=color, activefill='black')


    def scroll_y(self, *args, **kwargs):
        ''' Scroll canvas vertically and redraw the image '''
        self.canvas.yview(*args, **kwargs)  # scroll vertically
        self.show_image()  # redraw the image

    def scroll_x(self, *args, **kwargs):
        ''' Scroll canvas horizontally and redraw the image '''
        self.canvas.xview(*args, **kwargs)  # scroll horizontally
        self.show_image()  # redraw the image

    def move_from(self, event):
        ''' Remember previous coordinates for scrolling with the mouse '''
        self.canvas.scan_mark(event.x, event.y)

    def move_to(self, event):
        ''' Drag (move) canvas to the new position '''
        self.canvas.scan_dragto(event.x, event.y, gain=1)
        self.show_image()  # redraw the image

    def wheel(self, event):
        ''' Zoom with mouse wheel '''
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        bbox = self.canvas.bbox(self.container)  # get image area
        if bbox[0] < x < bbox[2] and bbox[1] < y < bbox[3]: pass  # Ok! Inside the image
        else: return  # zoom only inside image area
        scale = 1.0

        # Respond to Linux (event.num) or Windows (event.delta) wheel event
        if event.num == 5 or event.delta == -120:  # scroll down
            i = min(self.width, self.height)
            if int(i * self.imscale) < 30: return  # image is less than 30 pixels
            self.imscale /= self.delta
            scale        /= self.delta
        if event.num == 4 or event.delta == 120:  # scroll up
            i = min(self.canvas.winfo_width(), self.canvas.winfo_height())
            if i < self.imscale: return  # 1 pixel is bigger than the visible area
            self.imscale *= self.delta
            scale        *= self.delta
        self.canvas.scale('all', x, y, scale, scale)  # rescale all canvas objects
        self.show_image()

    def show_image(self, event=None):
        ''' Show image on the Canvas '''
        bbox1 = self.canvas.bbox(self.container)  # get image area
        # Remove 1 pixel shift at the sides of the bbox1
        bbox1 = (bbox1[0] + 1, bbox1[1] + 1, bbox1[2] - 1, bbox1[3] - 1)
        bbox2 = (self.canvas.canvasx(0),  # get visible area of the canvas
                 self.canvas.canvasy(0),
                 self.canvas.canvasx(self.canvas.winfo_width()),
                 self.canvas.canvasy(self.canvas.winfo_height()))
        bbox = [min(bbox1[0], bbox2[0]), min(bbox1[1], bbox2[1]),  # get scroll region box
                max(bbox1[2], bbox2[2]), max(bbox1[3], bbox2[3])]
        if bbox[0] == bbox2[0] and bbox[2] == bbox2[2]:  # whole image in the visible area
            bbox[0] = bbox1[0]
            bbox[2] = bbox1[2]
        if bbox[1] == bbox2[1] and bbox[3] == bbox2[3]:  # whole image in the visible area
            bbox[1] = bbox1[1]
            bbox[3] = bbox1[3]

        self.canvas.configure(scrollregion=bbox)  # set scroll region
        x1 = max(bbox2[0] - bbox1[0], 0)  # get coordinates (x1,y1,x2,y2) of the image tile
        y1 = max(bbox2[1] - bbox1[1], 0)
        x2 = min(bbox2[2], bbox1[2]) - bbox1[0]
        y2 = min(bbox2[3], bbox1[3]) - bbox1[1]
        if int(x2 - x1) > 0 and int(y2 - y1) > 0:  # show image if it in the visible area
            x = min(int(x2 / self.imscale), self.width)   # sometimes it is larger on 1 pixel...
            y = min(int(y2 / self.imscale), self.height)  # ...and sometimes not

    def _create_circle(self, x, y, r, **kwargs):
        return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)
    tk.Canvas.create_circle = _create_circle


class ImportButton(object):
    def __init__(self, parent, new):
        self.parent = parent
        self.parent.title('Stellaris SGV')
        
        self.parent.geometry('450x400')

        self.right_frame = Frame(self.parent, bd=3, relief="solid")
        self.right_frame.grid(row=0, rowspan=4, column=2, sticky='ns')
        self.jso = Button(self.right_frame, text="Import from .json", command=self.import_json)
        self.sav = Button(self.right_frame, text="Import from .sav", command=self.import_sav)
        if new:
            self.jso.grid_configure(row=0, column=0, padx=0, pady=0)
            self.sav.grid_configure(row=1, column=0, padx=0, pady=0)
            
            self.energy = Scale(self.right_frame,from_=0, to=1, orient='horizontal', troughcolor="yellow", resolution=0.01, label='Energy', command=self.energy_updates)
            self.energy.grid(row=2,column=0)
            self.minerals = Scale(self.right_frame,from_=0, to=1, orient='horizontal', troughcolor="red", resolution=0.01, label='Minerals', command=self.minerals_updates)
            self.minerals.grid(row=3,column=0)
            self.physics = Scale(self.right_frame,from_=0, to=1, orient='horizontal', troughcolor="blue", resolution=0.01, label='Physics', command=self.physics_updates)
            self.physics.grid(row=4,column=0)
            self.biology = Scale(self.right_frame,from_=0, to=1, orient='horizontal', troughcolor="green", resolution=0.01, label='Biology', command=self.biology_updates)
            self.biology.grid(row=5,column=0)
            self.engineering = Scale(self.right_frame,from_=0, to=1, orient='horizontal', troughcolor="orange", resolution=0.01, label='Engineering', command=self.engineering_updates)
            self.engineering.grid(row=6,column=0)
            


        else:
            self.jso.grid(row=2, column=0)
            self.sav.grid(row=2, column=1)



    def engineering_updates(self, changed_weight):
        self.weight_update(changed_weight, "engineering")

    def biology_updates(self, changed_weight):
        self.weight_update(changed_weight, "biology")

    def physics_updates(self, changed_weight):
        self.weight_update(changed_weight, "physics")

    def minerals_updates(self, changed_weight):
        self.weight_update(changed_weight, "minerals")
    
    def energy_updates(self, changed_weight):
        self.weight_update(changed_weight, "energy")


    def weight_update(self, new_weight, scale):
        new_weight = float(new_weight)
        print(scale + " is now " + str(new_weight))


    def import_json(self):
        file = easygui.fileopenbox()

        with open(file) as f:
            data = json.load(f)['gamestate']
            self.convert_to_universe(data, self.parent)


    def import_sav(self):
        file = easygui.fileopenbox()

        data = savToJson(file)['gamestate']

        self.convert_to_universe(data, self.parent)


    def convert_to_universe(self, data, root):
        systems = []
        planets = []
        deposits = []

        minx, miny = sys.maxsize, sys.maxsize
        maxx, maxy = -1*sys.maxsize, -1*sys.maxsize

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
            miny = min(miny, y)
            maxx = max(maxx, x)
            maxy = max(maxy, y)

            systems.append(System(val))
            
            for ID in systems[-1].planet_ids:
                systems[-1].addPlanet(planets[ID])

        ### Creating galaxy container
        galaxy = Galaxy(systems)
        galaxy.print_stats()


        ### Setting BBox corners
        bbox = (minx, miny, maxx, maxy)
        self.sav.grid_forget()
        self.jso.grid_forget()
        self.right_frame.grid_forget()
        Zoom_Advanced(root, galaxy, bbox)


# path = '../../him.png'  # place path to your image here
# root = tk.Tk()
# app = Zoom_Advanced(root, path=path)
# root.mainloop()