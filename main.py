import tkinter as tk
from tkinter import ttk, Button, Frame, Toplevel, Label, Scale, LEFT, SOLID, SUNKEN, DoubleVar, PhotoImage
import easygui
from converter import savToJson
from utils import Galaxy, System, Planet, Deposit
import json
import sys
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.colors import Normalize, TwoSlopeNorm
import math
import urllib.request

# TODO: Neaten code by adding and removing global variables, comment

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

class StellarisSGV:
    def __init__(self, master):
        self.master = master
        master.title("Stellaris SGV")

        self.view = Frame(self.master, width=450, height=450)
        self.sidebar = Frame(self.master, relief=SUNKEN, bd=2, width=100, height=450)


        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=0)
        
        # self.sidebar.grid(row=0, column=1, sticky="nsew")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.cmap = plt.cm.get_cmap('RdYlBu_r')
        self.create_buttons(self.sidebar, 0)

    def create_view(self):

        self.view.grid(row=0, column=0, sticky="nsew")

        self.galaxy = None

        vbar = AutoScrollbar(self.view, orient='vertical')
        hbar = AutoScrollbar(self.view, orient='horizontal')
        vbar.grid(row=1, column=1, sticky='ns')
        hbar.grid(row=2, column=0, sticky='we')
        self.canvas = tk.Canvas(self.view, highlightthickness=0,
                                xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        self.canvas.grid(row=1, column=0, sticky='nswe')
        vbar.configure(command=self.scroll_y)  # bind scrollbars to the canvas
        hbar.configure(command=self.scroll_x)

        self.view.rowconfigure(1, weight=1) # make canvas expandable
        self.view.columnconfigure(0, weight=1)

        self.tooltip = False
        self.tipwindow= None

        self.BBox = [0, 0, 0, 0]
        self.minx, self.miny = self.BBox[0], self.BBox[1]
        self.width, self.height = self.BBox[2], self.BBox[3]
        # set container for zooming
        self.imscale = 1.0  # scale for the canvaas image
        self.delta = 1.3  # zoom magnitude
        self.container = self.canvas.create_rectangle(0,0,0,0,width=1)  #self.canvas.create_rectangle(BBox[0]-5,BBox[1]-5,BBox[2]+5,BBox[3]+5, width=1)  

        # bind buttons
        self.canvas.bind('<Configure>', self.show_image)  # canvas is resized
        self.canvas.bind('<ButtonPress-1>', self.move_from)
        self.canvas.bind('<B1-Motion>',     self.move_to)
        self.canvas.bind('<MouseWheel>', self.wheel)  # with Windows and MacOS, but not Linux
        self.canvas.bind('<Button-5>',   self.wheel)  # only with Linux, wheel scroll down
        self.canvas.bind('<Button-4>',   self.wheel)  # only with Linux, wheel scroll up


    def create_buttons(self, parent, create_sliders):
        
        self.jso = Button(parent, text="Import from .json", command=self.import_json)
        self.jso.grid(row=0, column=0, sticky="w")
        self.sav = Button(parent, text="Import from .sav", command=self.import_sav)
        self.sav.grid(row=0, column=1, sticky="w")
        
        self.scales = []

        # create sliders
        if create_sliders:
            self.jso.grid_configure(row=0, column=0)
            self.sav.grid_configure(row=1, column=0)
            resources = ['minerals', 'energy', 'physics', 'society', 'engineering']
            colors = ["red", "yellow", "blue", "green", "orange"]
            for i in range(len(resources)):
                var = DoubleVar()
                var.set(500)
                callback = lambda event, tag=i: self.weight_update(event, tag)
                b = Scale(parent, from_=1, to=1000, variable=var, length=135, orient='horizontal', troughcolor=colors[i],
                    resolution=1, label=resources[i], showvalue=0)
                b.grid(row=2+i, column=0, sticky="w")
                b.bind('<ButtonRelease-1>', self.redraw) # redraw when user release scale
                self.scales.append(var)

    def redraw(self, event):
        # Only redraw if mouse isn't being held down

        galaxy = self.galaxy
        systems = galaxy.systems

        

        total = sum([scale.get() for scale in self.scales])
        weights = [scale.get()/total for scale in self.scales]

        for s in systems:
            s.updateScore(weights, galaxy.min_resources, galaxy.max_resources)
        galaxy.calcScoreRange()
        galaxy.calcMedian()
        try:
            norm = TwoSlopeNorm(vmin=galaxy.min_score, vcenter=galaxy.median_score, vmax=galaxy.max_score)
        except: # Use regular Normalize in the case TwoSlopeNorm fails
            norm = Normalize(vmin=galaxy.min_score, vmax=galaxy.max_score)
        
        for i in range(len(systems)):
            s = systems[i]


            normed = norm(s.score)
            rgba = self.cmap(normed)
            color = self.convert_to_hex(rgba)

            self.canvas.itemconfig(self.system_to_circ[i], fill=color)


    def scroll_y(self, *args, **kwargs):
        ''' Scroll canvas vertically and redraw the image '''
        self.canvas.yview(*args, **kwargs)  # scroll vertically
        # self.show_image()  # redraw the image

    def scroll_x(self, *args, **kwargs):
        ''' Scroll canvas horizontally and redraw the image '''
        self.canvas.xview(*args, **kwargs)  # scroll horizontally
        # self.show_image()  # redraw the image

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
            if int(i * self.imscale) < 30*5: return  # image is less than 30 pixels
            self.imscale /= self.delta
            scale        /= self.delta
        if event.num == 4 or event.delta == 120:  # scroll up
            i = min(self.canvas.winfo_width(), self.canvas.winfo_height())
            if i < self.imscale*30: return  # 1 pixel is bigger than the visible area
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

    def import_json(self):
        file = easygui.fileopenbox()

        with open(file) as f:
            data = json.load(f)['gamestate']
            self.convert_to_universe(data)


    def import_sav(self):
        file = easygui.fileopenbox()
        data = savToJson(file)['gamestate']
        self.convert_to_universe(data)

    def convert_to_universe(self, data):
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

        ### Calculate system resource divergences
        for s in galaxy.systems:
            s.calcDivergence(galaxy.avg_resources)
        galaxy.calcDivergenceRange()

        ### LOADING RESt OF APP
        self.sav.grid_forget()
        self.jso.grid_forget()
        self.create_view()
        self.sidebar.grid_configure(row=0, column=2)
        self.create_buttons(self.sidebar, 1)

        ### Calculate system scores
        total = sum([scale.get() for scale in self.scales])
        weights = [scale.get()/total for scale in self.scales]

        for s in galaxy.systems:
            s.updateScore(weights, galaxy.min_resources, galaxy.max_resources)
        galaxy.calcScoreRange()
        galaxy.calcMedian()

        ### Setting BBox corners
        bbox = (minx, miny, maxx, maxy)
        self.BBox = bbox
        self.container = self.canvas.create_rectangle(bbox[0]-5, bbox[1]-5, bbox[2]+5, bbox[3]+5, width=1)
        self.minx, self.miny = bbox[0], bbox[1]
        self.width, self.height = bbox[2], bbox[3]

        self.draw_universe(galaxy)

    def convert_to_hex(self, rgba_color):
        red = int(rgba_color[0]*255)
        green = int(rgba_color[1]*255)
        blue = int(rgba_color[2]*255)
        hexcolor = '#{r:02x}{g:02x}{b:02x}'.format(r=red,g=green,b=blue)
        return hexcolor
            
    def system_enter(self, event, i):
        if self.tooltip:
            return
        system=self.galaxy.systems[i]
        #mins = PhotoImage(file='Minerals.gif')
        self.text = '{n:^18s}\nMinerals:{m}\nEnergy:{e}\nPhysics:{p}\nSociety:{s}\nEngineering:{en}'.format(n=system.name,m=system.resources[0],e=system.resources[1],p=system.resources[2],s=system.resources[3],en=system.resources[4])
        x = self.master.winfo_pointerx()
        y = self.master.winfo_pointery()
        abs_coord_x = event.x + self.master.winfo_rootx() + 10
        abs_coord_y = event.y + self.master.winfo_rooty() + 10
        tw = Toplevel()
        self.tipwindow = tw
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (abs_coord_x, abs_coord_y))
        label = Label(tw, text=self.text, justify=LEFT,
                    background="#ffffff", relief=SOLID, borderwidth=1,
                    font=("questrial", "18", "normal"))
        label.pack(ipadx=1)
        self.tooltip = True

    def system_exit(self, event, i):
        tw = self.tipwindow
        self.tipwindow = None
        if self.tooltip:
            tw.destroy()
            self.tooltip = False  

    def draw_universe(self, galaxy):
        self.galaxy = galaxy
        systems = galaxy.systems

        #make key for colors
        self.key = tk.Canvas(self.view, height=15, width=385)
        self.key.grid(row=0, column=0, sticky='ne')

        self.key.create_text(0,0, anchor='nw', text="Worst")
        self.key.create_text(355,0, anchor='nw', text="Best")
        
        for s in systems:
            for c in s.hyperlanes:
                p1 = s.pos
                p2 = systems[c].pos
                self.canvas.create_line(p1[0], p1[1], p2[0], p2[1])

        self.system_to_circ = {}

        print(galaxy.min_score, galaxy.max_score, galaxy.avg_score, galaxy.median_score)
        try:
            norm = TwoSlopeNorm(vmin=galaxy.min_score, vcenter=galaxy.median_score, vmax=galaxy.max_score)
        except: # Use regular Normalize in the case TwoSlopeNorm fails
            norm = Normalize(vmin=galaxy.min_score, vmax=galaxy.max_score)
        for i in range(len(systems)):
            s = systems[i]
            p = s.pos
            normed = norm(s.score)
            rgba = self.cmap(normed)
            color = self.convert_to_hex(rgba)

            circ_id = self.canvas.create_circle(p[0], p[1], 5, fill=color, activewidth=4, tags=i)
            self.system_to_circ[i] = circ_id
            enter_callback = lambda event, tag=i: self.system_enter(event, tag)
            leave_callback = lambda event, tag=i: self.system_exit(event, tag)
            self.canvas.tag_bind(circ_id, "<Enter>", enter_callback)
            self.canvas.tag_bind(circ_id, "<Leave>", leave_callback)
        self.color_key(False)


    def color_key(self, scale_change, norm = Normalize(vmin=40, vmax=345)):

        self.line_to_id = {}
        i = 40
        while i < 345:
            spot = norm(i)
            rgbb = self.cmap(spot)
            color = self.convert_to_hex(rgbb)
            #print("Color is " + color)
            line_id = self.key.create_line(i,0,i,10, fill=color)
            self.line_to_id[i] = line_id
            i += 1



root = tk.Tk()
root.minsize(450, 200)
app = StellarisSGV(root)
root.mainloop()

