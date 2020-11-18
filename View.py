# Map Viewer
# View.py
# Handles gui functionality and drives controller
import os
import tkinter as tk
from tkinter import ttk

from ColorFrame import ColorParentFrame
from Controller import Controller
from mapFrame import MapControlFrame, MapParentFrame, MapPlotFrame, TextFrame, MapSettingsFrame
import settings
from WindowManger import WindowManager

from Response import Response
# Main gui class that has controller member


class View:

    def __init__(self):
        self.mapController = Controller(self)

        self.frames = []

    def init_mainWindow(self, parent):
        self.parent = parent
        self.rootWm = WindowManager(parent, self)
        self.create_menuBar(parent)

    def create_dropDown(self):
        pass

    # create menu bar at top

    def create_menuBar(self, frame):
        menuBar = tk.Menu(frame)
        fileMenu = tk.Menu(menuBar, tearoff=0)
        fileMenu.add_command(label='Load Mav', command=self.spinup_mapDataSet)
        gridSpawnMenu = tk.Menu(fileMenu, tearoff=0)
        fileMenu.add_cascade(label='Grid Spawn', menu=gridSpawnMenu)
        gridSpawnMenu.add_command(
            label='Map', command=lambda: self.spawn_map('grid'))
        gridSpawnMenu.add_command(
            label='Color', command=lambda: self.spawn_colorTool('grid'))
        gridSpawnMenu.add_command(
            label='Data Box', command=lambda: self.spawn_dataBox('grid'))

        floatSpawnMenu = tk.Menu(fileMenu)
        fileMenu.add_cascade(label='Float Spawn', menu=floatSpawnMenu)
        floatSpawnMenu.add_command(
            label='Map', command=lambda: self.spawn_map('floating'))
        floatSpawnMenu.add_command(
            label='Color', command=lambda: self.spawn_colorTool('floating'))
        floatSpawnMenu.add_command(
            label='Data Box', command=lambda: self.spawn_dataBox('floating'))
        
        floatSpawnMenu.add_command(label='Control Frame',command=lambda :self.spawn_controlFrame('floating'))

        menuBar.add_cascade(label='File', menu=fileMenu)
        editMenu = tk.Menu(menuBar, tearoff=0)
        menuBar.add_cascade(label='Edit', menu=editMenu)
        viewMenu = tk.Menu(menuBar, tearoff=0)
        menuBar.add_cascade(label='View', menu=viewMenu)
        saveMenu = tk.Menu(menuBar, tearoff=0)
        menuBar.add_cascade(label='Save', menu=saveMenu)
        saveMenu.add_command(label='Snapshot', command=self.save_snapShot)

        frame.config(menu=menuBar)

    # create map and pass to window manager

    def spawn_map(self, WM_mode):
        frame = MapParentFrame("Map", self)
        self.rootWm.add_frame(frame, mode=WM_mode)
        self.frames.append(frame)
        self.mapController.plot_cellPatches(frame)
        self.mapController.config_mapPlot(frame)
        self.mapController.config_mapWidgets(frame.controlFrame)
        self.mapController.update_map(frame)
        self.mapController.update_legend(settings.numLegendEntries, frame)
        controlFrame:MapControlFrame=frame.get_controlFrame()
        self.map_responseChanged(controlFrame,None) # update map for first time 
        print("2nd added")
        # controlFrame.grid(row=0, column=0, sticky=tk.N+tk.E+tk.W+tk.S)
        for currFrame in self.frames:
            if isinstance(currFrame, TextFrame):
                plotFrame = frame.get_plotFrame()
                plotFrame.set_dataFrame(currFrame)

    # create dataBox and pass to window manager

    def spawn_dataBox(self, WM_mode):
        tFrame = TextFrame("Data", self)
        tFrame.set_currLine("")
        self.rootWm.add_frame(tFrame, mode=WM_mode)
        self.frames.append(tFrame)

        for frame in self.frames:
            if isinstance(frame, MapParentFrame):
                mFrame = frame.get_plotFrame()
                mFrame.set_dataFrame(tFrame)
                tFrame.set_parent(mFrame)

    def spawn_colorTool(self, WM_mode):
        cFrame = ColorParentFrame("Color", self)
        self.rootWm.add_frame(cFrame, mode=WM_mode)
        self.frames.append(cFrame)
        self.mapController.config_colorWidgets(cFrame)

    

    def spawn_controlFrame(self,WM_mode):
        cFrame=MapControlFrame(self)
        self.rootWm.add_frame(cFrame,mode=WM_mode)
        self.mapController.config_mapWidgets(cFrame)

    def spawn_plotSettings(self, parent):
        sFrame: MapSettingsFrame = MapSettingsFrame('Plot Settings', self)
        sFrame.parent = parent
        self.rootWm.add_frame(sFrame, mode='floating')

    # remove frame from view
    def remove_frame(self, frame):
        for child in frame.winfo_children():
            if child in self.frames:
                self.frames.remove(child)

    def spinup_mapDataSet(self):
        cwd = os.getcwd()
        dataFile = tk.filedialog.askopenfilename(initialdir=cwd)
        self.parent.title(self.parent.title()+" -> "+dataFile)
        self.mapController.map_spinupDataSet(self.frames, dataFile)

    # event capture for time slider

    def map_timeSliderReleased(self, frame, event):
        self.mapController.update_map(frame)

    # event capture for sim Id drop down
    def map_simIdDropdownChanged(self, frame, event):
        self.mapController.update_map(frame)

    # event capture for response drop down
    def map_responseChanged(self, frame, event):

        if isinstance(frame, MapParentFrame):
            plotFrame = frame.get_plotFrame()
            dataFrame = plotFrame.get_dataFrame()
        elif isinstance(frame, MapControlFrame):
            self.filter_drop(frame,event)
            self.mapController.update_map(frame)
            plotFrame = frame.get_plotFrame()

            self.mapController.update_legend(settings.numLegendEntries, frame)
            dataFrame = plotFrame.get_dataFrame()
            if dataFrame is not None:
                dataFrame.set_currLine(frame.get_respDropDownVal())
                dataFrame.view_currLine()

    # mouse moved event

    def map_mouseMoved(self, frame, event):
        if frame.get_dataFrame() is not None:
            self.mapController.mapDetect_cellChange(frame, event)

    # mouse click event
    def map_mouseClicked(self, frame, event):
        if isinstance(frame, MapPlotFrame):
            self.mapController.cell_selected(frame, event)
            print("Mouse clicked")


    def pick_test(self, frame, event):
        print(event.name)
        print(event.guiEvent)
        print("Pick Event")
        print(event.artist)

    def cell_changed(self, frame, cell):
        pass

# save button was changed on color props
    def responsePropsChanged(self, args, frame):
        responses = self.mapController.responses
        respIndex = args["responseIndex"]

        curResp: Response = responses[respIndex]

        if "maxVal" in args:
            curResp.max = args["maxVal"]

        if "minVal" in args:
            curResp.min = args["minVal"]

        if "hue" in args:
            curResp.hue = args["hue"]

        if "upperThresh" in args:
            curResp.upperThresh = args["upperThresh"]
            print("upperThresh Changed ", args["upperThresh"])
        if "lowerThresh" in args:
            curResp.lowerThresh = args["lowerThresh"]

        if "smallValPerc" in args:
            curResp.smallValPerc = args["smallValPerc"]

        frame.update_entrys(curResp)

        for loopFrame in self.frames:
            if isinstance(loopFrame, MapParentFrame):
                controlFrame = loopFrame.get_controlFrame()
                self.mapController.update_map(controlFrame)
                self.mapController.update_legend(
                    settings.numLegendEntries, controlFrame)
        print("response things changed")

    def colorResponseChanged(self, frame, event):
        responses = self.mapController.responses
        responseIndex = frame.get_respDropIndex()

        curResp: Response = responses[responseIndex]
        frame.update_entrys(curResp)

    def densityToggled(self, frame):
        self.mapController.update_map(frame)
        print("Toggled")

    def scaleFacChanged(self, frame, event):
        if isinstance(frame, MapControlFrame):
            plotframe = frame.get_plotFrame()
            cell = plotframe.get_currCell()
            self.mapController.write_cellData(plotframe, cell)

    def load_mapBackground(self, file):
        pass
        # self.img=

    def save_snapShot(self):
        self.mapController.snapShot()

    def updateAll_respProps(self, curRespInd):
        responses = self.mapController.responses
        curResp = responses[curRespInd]

        for resp in responses:
            resp.hue = curResp.hue
            resp.upperThresh = curResp.upperThresh
            resp.lowerThresh = curResp.lowerThresh
            resp.smallValPerc = curResp.smallValPerc

        self.update_mapParentFrames()

    def update_mapParentFrames(self):

        for frame in self.frames:
            if isinstance(frame, MapParentFrame):
                self.mapController.update_map(frame)
                self.mapController.update_legend(
                    settings.numLegendEntries, frame)

    def plotSettings_changed(self, args, frame):

        if isinstance(frame, MapParentFrame):
            plotFrame: MapPlotFrame = frame.get_plotFrame()
            controlFrame: MapControlFrame = frame.get_controlFrame()

        if "legendLoc" in args:
            plotFrame.legendLoc = args["legendLoc"]
            self.mapController.update_legend(
                settings.numLegendEntries, controlFrame)

    def filter_drop(self,frame,event):
        print("resp drop changed")
        if isinstance(frame,MapControlFrame):
            targs=[]
            resp_targs=self.mapController.get_reponseNames()
            respName=frame.respDropDown.get()

            for string in resp_targs:
                if respName in string:
                    underInd=string.rfind('_') 
                    targ=string[underInd+1:]
                    if targ not in targs:
                        targs.append(targ)
            oldTarg=frame.targDropDown.get()
            frame.targDropDown.config(values=targs)
            if oldTarg in targs:
                frame.targDropDown.set(oldTarg)
            else:
                frame.targDropDown.set(targs[0])
    
            # self.map_responseChanged(frame,None)