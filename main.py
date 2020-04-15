import json
import sys
from converter import savToJson
from utils import System, Planet, Deposit
from interface import Zoom_Advanced, ImportButton

import tkinter as tk
from tkinter import ttk


    #for i in range(3):
    #     print(systems[i].toString())

root = tk.Tk()
app = ImportButton(root, 0)
root.mainloop()

