# Map Viewer
# NetFrame.py
# Contains Frame classes for network tool functionality
# Inherited from ttk.frame
from tkinter import ttk
import tkinter as tk
from tkinter.ttk import Frame, LabelFrame

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)


class NetParentFrame(LabelFrame):

    def __init__(self,label,view ):
        self.label = label
        self.view = view

    def init_frames(self, master):
        super().__init__(master)
        self.plotFrame = NetMapFrame(self.view,master=self)
        self.controlFrame = NetControlFrame(self.view,master=self)
        self.pack_children()

    def pack_children(self):
        self.controlFrame.grid(row=0, column=0)
        self.plotFrame.grid(row=1, column=0)


class NetControlFrame(Frame):

    def __init__(self,view, master=None):
        self.view=view
        super().__init__(master)
        self.blah = 1
        self.pack_children()

    def pack_children(self):
        self.zXmin = ttk.Entry(self)
        self.zXmax = ttk.Entry(self)
        self.zYmin = ttk.Entry(self)
        self.zYmax = ttk.Entry(self)
        self.zButton = ttk.Button(self, text="Zoom")

        self.zXmin.grid(row=0, column=0)
        self.zXmax.grid(row=0, column=1)
        self.zYmin.grid(row=1, column=0)
        self.zYmax.grid(row=1, column=1)
        self.zButton.grid(row=2, column=1)

    def config_wigets(self):
        pass


class NetMapFrame(Frame):

    def __init__(self,view, master=None):
        self.view=view
        if master is not None:
            super().__init__(master)
        self.fig = plt.Figure()
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        toolbar = NavigationToolbar2Tk(self.canvas, self)
        toolbar.update()
        self.config_widgetDefaults()

    def config_widgetDefaults(self):
        self.fig.canvas.mpl_connect(
            'button_press_event', lambda event: self.view.map_mouseClicked(self, event))

        self.fig.canvas.mpl_connect(
            'pick_event', lambda event: self.view.map_mouseClicked(self,event))

    def plot_point(self, x, y, marker=None):
        self.ax.plot(x, y, marker=marker,picker=5)

    def draw_canvas(self):
        self.canvas.draw()

    def plot_patch(self, patch):
        self.ax.add_patch(patch)

    def remove_patch(self, patch):
        patch.remove()
