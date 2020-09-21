# Map Viewer
# View.py
# Handles gui functionality and drives controller
import os
import tkinter as tk
from tkinter import ttk

from Controller import Controller
from mapFrame import MapParentFrame, TextFrame, MapControlFrame
from WindowManger import WindowManager

# Main gui class that has controller member


class View:

    def __init__(self):
        self.controller = Controller()

        self.frames = []

    def init_mainWindow(self, parent):
        self.rootWm = WindowManager(parent, self)
        self.create_menuBar(parent)

    def create_dropDown(self):
        pass
    
    # create menu bar at top

    def create_menuBar(self, frame):
        menuBar = tk.Menu(frame)
        fileMenu = tk.Menu(menuBar, tearoff=0)
        fileMenu.add_command(label='Load Mav', command=self.spinup_mapDataSet)
        # fileMenu.add_command(label='Network',command=self.create_network_hardcoded)
        # fileMenu.add_command(label='toggle',command=self.toggle_GUI)
        fileMenu.add_command(label='Spawn Map', command=self.spawn_map)
        fileMenu.add_command(label="Spawn Data Box",
                             command=self.spawn_dataBox)
        menuBar.add_cascade(label='File', menu=fileMenu)
        editMenu = tk.Menu(menuBar, tearoff=0)
        menuBar.add_cascade(label='Edit', menu=editMenu)
        viewMenu = tk.Menu(menuBar, tearoff=0)
        menuBar.add_cascade(label='View', menu=viewMenu)
        frame.config(menu=menuBar)

    # create map and pass to window manager

    def spawn_map(self):
        frame = MapParentFrame("Map", self)
        self.rootWm.add_frame(frame)
        self.frames.append(frame)
        self.controller.plot_cellPatches(frame)
        self.controller.config_mapPlot(frame)
        self.controller.config_mapWidgets(frame.controlFrame)

        for currFrame in self.frames:
            if isinstance(currFrame, TextFrame):
                plotFrame = frame.get_mapFrame()
                plotFrame.set_dataFrame(currFrame)

    # create dataBox and pass to window manager

    def spawn_dataBox(self):
        tFrame = TextFrame("Data", self)
        tFrame.set_currLine("")
        self.rootWm.add_frame(tFrame)
        self.frames.append(tFrame)

        for frame in self.frames:
            if isinstance(frame, MapParentFrame):
                mFrame = frame.get_mapFrame()
                mFrame.set_dataFrame(tFrame)
                tFrame.set_parent(mFrame)

    # remove frame from view
    def remove_frame(self, frame):
        for child in frame.winfo_children():
            if child in self.frames:
                self.frames.remove(child)

    def spinup_mapDataSet(self):
        cwd = os.getcwd()
        dataFile = tk.filedialog.askopenfilename(initialdir=cwd)
        self.controller.map_spinupDataSet(self.frames, dataFile)

    # event capture for time slider

    def map_timeSliderReleased(self, frame, event):
        self.controller.update_map(frame)

    # event capture for sim Id drop down
    def map_simIdDropdownChanged(self, frame, event):
        self.controller.update_map(frame)

    # event capture for response drop down
    def map_responseDropDownChanged(self, frame, event):
        self.controller.update_map(frame)

        if isinstance(frame, MapParentFrame):
            plotFrame = frame.get_plotFrame()
            dataFrame = plotFrame.get_dataFrame()
        elif isinstance(frame, MapControlFrame):
            plotFrame = frame.get_plotFrame()

            self.controller.update_legend(4, frame)
            dataFrame = plotFrame.get_dataFrame()
            if dataFrame is not None:
                dataFrame.set_currLine(frame.get_respDropDownVal())
                dataFrame.view_currLine()

    # mouse moved event

    def map_mouseMoved(self, frame, event):
        if frame.get_dataFrame()is not None:
            self.controller.mapDetect_cellChange(frame, event)

    # mouse click event
    def map_mouseClicked(self, frame, event):
        self.controller.cell_selected(frame, event)

    def cell_changed(self, frame, cell):
        pass
