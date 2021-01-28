# Map Viewer
# View.py
# Handles gui functionality and drives controller
import os
import tkinter as tk
from tkinter import ttk
import wx
from Frames.WxFrames import WxFrame,MapControlPanel,MapParentPanel,MapPlotPanel,MapdataPanel

import settings
from ColorFrame import ColorParentFrame
from Controller import Controller
from MapFrame import (MapControlFrame, MapParentFrame, MapPlotFrame,
                      MapSettingsFrame, TextFrame)
from Response import Response
from WindowManger import WindowManager

# Main gui class that has controller member


class View:

    def __init__(self):
        self.mapController = Controller(self)

        self.frames = []
        self.panels=[]

    def init_mainWindow(self ):
        
        frame=WxFrame(None)
        self.spinup_mapDataSet()
        self.spawn_mapPanel(frame)
        self.spawn_dataPanel()
        # self.spawn_plotPanel(frame)
        print("spawned")
        frame.Show()
    # create menu bar at top
    
    def spawn_controlPanel(self,parent):
        panel=MapControlPanel(parent,self)

    def spawn_dataPanel(self):
        frame=WxFrame(None)
        dataPanel=MapdataPanel(frame,self)
        hSizer=wx.BoxSizer(wx.HORIZONTAL)
        vSizer=wx.BoxSizer(wx.VERTICAL)
        hSizer.Add(dataPanel,1,1,20)
        vSizer.Add(hSizer,1,1,20)
        frame.SetSizer(vSizer)
        frame.Show()

        for panel in self.panels:
            if isinstance(panel,MapParentPanel):
                panel.plotPanel.dataPanel=dataPanel
        self.panels.append(panel)

    def spawn_mapPanel(self,parent):
        parPanel=MapParentPanel(parent,self)
        self.panels.append(parPanel)
        plotPanel=parPanel.plotPanel
        controlPanel=parPanel.controlPanel
        # frame = MapParentFrame("Map", self)
        self.mapController.plot_cellPatches(plotPanel)
        self.mapController.config_mapPlot(parPanel)
        self.mapController.config_controlWidgets(controlPanel)
        self.mapController.update_map(parPanel)
        self.mapController.update_legend(settings.numLegendEntries, parPanel)
        # controlFrame: MapControlFrame = frame.get_controlFrame()
        # update map for first time
        # self.map_responseChanged(controlFrame, None)

    def spawn_plotPanel(self,parent):
        panel=MapPlotPanel(parent)

    
    def spawn_map(self, WM_mode):
        frame = MapParentFrame("Map", self)
        self.rootWm.add_frame(frame, mode=WM_mode)
        self.frames.append(frame)
        self.mapController.plot_cellPatches(frame)
        self.mapController.config_mapPlot(frame)
        self.mapController.config_mapWidgets(frame.controlFrame)
        self.mapController.update_map(frame)
        self.mapController.update_legend(settings.numLegendEntries, frame)
        controlFrame: MapControlFrame = frame.get_controlFrame()
        # update map for first time
        self.map_responseChanged(controlFrame, None)
        # controlFrame.grid(row=0, column=0, sticky=tk.N+tk.E+tk.W+tk.S)
        for currFrame in self.frames:
            if isinstance(currFrame, TextFrame):
                plotFrame = frame.get_plotFrame()
                plotFrame.set_dataFrame(currFrame)

    # create dataBox and pass to window manager

    
    def spawn_colorTool(self, WM_mode):
        cFrame = ColorParentFrame("Color", self)
        self.rootWm.add_frame(cFrame, mode=WM_mode)
        self.frames.append(cFrame)
        self.mapController.config_colorWidgets(cFrame)

    def spawn_controlFrame(self, WM_mode):
        cFrame = MapControlFrame(self)
        self.rootWm.add_frame(cFrame, mode=WM_mode)
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
        cwd='C:/Users/trevor.griggs/Dev/projects/map-viewer/mav/'
        # dataFile = tk.filedialog.askopenfilename(initialdir=cwd)
        dataFile=os.path.join(cwd,'BRc1-mav-1120EAf-0_5-4.json')

        # self.parent.title(self.parent.title()+" -> "+dataFile)

        self.mapController.map_spinupDataSet(self.panels, dataFile)

    # event capture for time slider

    def map_timeSliderReleased(self, frame, event):
        self.mapController.update_map(frame)
        

    # event capture for sim Id drop down
    def map_simIdDropdownChanged(self, panel, event):
        self.mapController.update_map(panel)
        plotPanel=panel.plotPanel


    # event capture for response drop down
    def map_responseChanged(self, panel, event):

        if isinstance(frame, MapParentFrame):
            plotFrame = frame.get_plotFrame()
            dataFrame = plotFrame.get_dataFrame()
        elif isinstance(frame, MapControlFrame):
            self.mapController.update_map(frame)
            # plotFrame = frame.get_plotFrame()
            # controlFrame: MapControlFrame = frame

            self.mapController.update_legend(settings.numLegendEntries, frame)
            dataFrame = plotFrame.get_dataFrame()
            # if dataFrame is not None:
                # self.mapController.write_cellData(plotFrame)
                # dataFrame.set_currLine(controlFrame.get_currResp_targ())
                # dataFrame.view_currLine()

    # mouse moved event

    def map_mouseMoved(self, panel, event):
        if panel.dataPanel is not None:
            self.mapController.mapDetect_cellChange(panel, event)

    # mouse click event
    def map_mouseClicked(self, panel, event):
        if isinstance(panel, MapPlotPanel):
            self.mapController.cell_selected(panel, event)


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

    def colorResponseChanged(self, frame, event):
        responses = self.mapController.responses
        responseIndex = frame.get_respDropIndex()

        curResp: Response = responses[responseIndex]
        frame.update_entrys(curResp)

    def densityToggled(self, frame):
        self.mapController.update_map(frame)

    def scaleFacChanged(self, frame, event):
        if isinstance(frame, MapControlFrame):
            plotframe = frame.get_plotFrame()
            self.mapController.write_cellData(plotframe)

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

    def filter_drop(self, panel, event):
        print("drop filtered")
        if isinstance(panel, MapControlPanel):
            targs = []
            resp_targs = self.mapController.get_reponseNames()
            respName = panel.respDrop.GetStringSelection()

            for string in resp_targs:
                if respName in string:
                    underInd = string.rfind('_')
                    targ = string[underInd+1:]
                    if targ not in targs:
                        targs.append(targ)
            oldTarg = panel.tgtDrop.GetStringSelection()
            panel.tgtDrop.Clear()
            panel.tgtDrop.AppendItems(targs)
            if oldTarg in targs:
                panel.tgtDrop.SetSelection(targs.index(oldTarg))
            else:
                panel.tgtDrop.SetSelection(0)

            # self.map_responseChanged(frame,None)

    def dataBoxMode_changed(self,event,frame:MapPlotFrame):
        self.mapController.write_cellData(frame)