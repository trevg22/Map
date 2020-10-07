# Map Viewer
# View.py
# Handles gui functionality and drives controller
import os
import tkinter as tk
from tkinter import ttk

from Controller import Controller
from mapFrame import MapParentFrame, TextFrame, MapControlFrame,MapPlotFrame
from NetFrame import NetParentFrame,NetControlFrame,NetMapFrame
from WindowManger import WindowManager
from NetFrame import NetParentFrame
from NetController import NetController
from ColorFrame import ColorParentFrame
# Main gui class that has controller member


class View:

    def __init__(self):
        self.mapController = Controller()
        self.netController=NetController()

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
        fileMenu.add_command(label="Spawn Color",command=self.spawn_colorTool)
        fileMenu.add_command(label='Spawn Network', command=self.spawn_network)
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
        self.mapController.plot_cellPatches(frame)
        self.mapController.config_mapPlot(frame)
        self.mapController.config_mapWidgets(frame.controlFrame)

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

    def spawn_colorTool(self):
        cFrame=ColorParentFrame("Color",self)
        self.rootWm.add_frame(cFrame)
        self.frames.append(cFrame)
        self.mapController.config_colorWidgets(cFrame)
    def spawn_network(self):
        nFrame=NetParentFrame("network",self)
        self.rootWm.add_frame(nFrame)
    # remove frame from view
    def remove_frame(self, frame):
        for child in frame.winfo_children():
            if child in self.frames:
                self.frames.remove(child)

    def spinup_mapDataSet(self):
        cwd = os.getcwd()
        dataFile = tk.filedialog.askopenfilename(initialdir=cwd)
        self.mapController.map_spinupDataSet(self.frames, dataFile)

    # event capture for time slider

    def map_timeSliderReleased(self, frame, event):
        self.mapController.update_map(frame)

    # event capture for sim Id drop down
    def map_simIdDropdownChanged(self, frame, event):
        self.mapController.update_map(frame)

    # event capture for response drop down
    def map_responseDropDownChanged(self, frame, event):
        self.mapController.update_map(frame)

        if isinstance(frame, MapParentFrame):
            plotFrame = frame.get_plotFrame()
            dataFrame = plotFrame.get_dataFrame()
        elif isinstance(frame, MapControlFrame):
            plotFrame = frame.get_plotFrame()

            self.mapController.update_legend(4, frame)
            dataFrame = plotFrame.get_dataFrame()
            if dataFrame is not None:
                dataFrame.set_currLine(frame.get_respDropDownVal())
                dataFrame.view_currLine()

    # mouse moved event

    def map_mouseMoved(self, frame, event):
        if frame.get_dataFrame()is not None:
            self.mapController.mapDetect_cellChange(frame, event)

    # mouse click event
    def map_mouseClicked(self, frame, event):
        if isinstance(frame,MapPlotFrame):
            self.mapController.cell_selected(frame, event)
            print("Mouse clicked")

        if isinstance(frame,NetMapFrame):
            self.netController.point_clicked(frame,event)
            print("controller called")

    def pick_test(self,frame,event):
        print(event.name)
        print(event.guiEvent)
        print("Picke Event")
        print(event.artist)

    def cell_changed(self, frame, cell):
        pass

# save button was changed on color props
    def responsePropsChanged(self,args,frame):
        responses=self.mapController.responses
        responseIndex=args["responseIndex"]

        if "maxVal" in args:
            responses[responseIndex].max=args["maxVal"]

        if "minVal" in args:
            responses[responseIndex].min=args["minVal"]

        if "hue" in args:
            responses[responseIndex].hue=args["hue"]

        maxVal=responses[responseIndex].max
        minVal=responses[responseIndex].min
        hue=responses[responseIndex].hue
        frame.update_entrys(minVal,maxVal,hue)
        
        for loopFrame in self.frames:
            if isinstance(loopFrame,MapParentFrame):
                controlFrame=loopFrame.get_controlFrame()
                self.mapController.update_map(controlFrame)
                
        print("response things changed")


    def colorResponseChanged(self,frame,event):
        responses=self.mapController.responses
        responseIndex=frame.get_respDropIndex()

        maxVal=responses[responseIndex].max
        minVal=responses[responseIndex].min
        hue=responses[responseIndex].hue
        frame.update_entrys(minVal,maxVal,hue)


    def densityToggled(self,frame):
        self.mapController.update_map(frame)
        print("Toggled")

    def scaleFacChanged(self,frame,event):
        if isinstance(frame,MapControlFrame):
            plotframe=frame.get_plotFrame()
            cell=plotframe.get_currCell()
            self.mapController.write_cellData(plotframe,cell)