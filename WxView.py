# Map Viewer
# View.py
# Handles gui functionality and drives controller
import _thread
import os

import wx

import settings
from AppMenu import AppMenu
from Controller import Controller
from Response import Response
from SettingsPanel import SettingsNotebook, ColorPanel
from WxFrames import (
    MapControlPanel,
    MapdataPanel,
    MapParentPanel,
    MapPlotPanel,
    TpamGrid,
)

# Main gui class that has controller member


class View(wx.Frame):
    def __init__(self):
        # super().__init__(wx.ID_ANY,"Map Viewer",size=(500,500))
        super().__init__(None, size=(500, 500))
        self.mapController = Controller(self)
        self.tpamFile = "tpam2.json"
        self.frames = []
        self.panels = []

    def init_mainWindow(self):

        frame = self
        menuBar = AppMenu(frame, self)
        self.spinup_mapDataSet(None)
        self.spawn_mapPanel(frame)
        self.spawn_dataPanel(None)
        # self.spawn_tpamGrid()
        frame.Show()

    # create menu bar at top

    def spawn_controlPanel(self, parent):
        panel = MapControlPanel(parent, self)

    def spawn_tpamGrid(self):
        frame = wx.Frame(None)
        panel = TpamGrid(frame, None)
        frame.Show()

    def spawn_dataPanel(self, event):
        frame = wx.Frame(None)
        dataPanel = MapdataPanel(frame, self)
        hSizer = wx.BoxSizer(wx.HORIZONTAL)
        vSizer = wx.BoxSizer(wx.VERTICAL)
        hSizer.Add(dataPanel, 1, 1, 20)
        vSizer.Add(hSizer, 1, 1, 20)
        frame.SetSizer(vSizer)
        frame.Show()
        frame2 = wx.Frame(None)
        tpamPanel = TpamGrid(frame2, None)
        dataPanel.tpamGrid = tpamPanel
        frame2.Show()

        for panel in self.panels:
            if isinstance(panel, MapParentPanel):
                panel.plotPanel.dataPanel = dataPanel
                dataPanel.plotPanel = panel.plotPanel
        self.panels.append(panel)

    def spawn_settingsPanel(self, controlPanel):
        frame = wx.Frame(None)

        noteBook = SettingsNotebook(self)
        controlPanel.settingsNotebook = noteBook
        # settingsNotebook = wx.Notebook()
        noteBook.Create(frame)
        noteBook.OnCreate(None)
        noteBook.controlPanel = controlPanel
        self.mapController.config_settingsNoteBook(noteBook, controlPanel)
        noteBook.Reparent(frame)
        hSizer = wx.BoxSizer(wx.HORIZONTAL)
        vSizer = wx.BoxSizer(wx.VERTICAL)
        hSizer.Add(noteBook, 0, 1, 20)
        vSizer.Add(hSizer, 0, 1, 20)
        frame.SetSizer(vSizer)
        frame.Show()

    def spawn_mapPanel(self, parent):
        parPanel = MapParentPanel(parent, self)
        self.panels.append(parPanel)
        plotPanel = parPanel.plotPanel
        controlPanel = parPanel.controlPanel
        # frame = MapParentFrame("Map", self)
        self.mapController.plot_cellPatches(plotPanel)
        self.mapController.config_mapPlot(parPanel)
        self.mapController.config_controlWidgets(controlPanel)
        self.mapController.update_map(parPanel)
        self.mapController.update_legend(parPanel)
        # controlFrame: MapControlFrame = frame.get_controlFrame()
        # update map for first time
        # self.map_responseChanged(controlFrame, None)

    def spawn_plotPanel(self, parent):
        panel = MapPlotPanel(parent)

    def spinup_mapDataSet(self, event):
        cwd = os.getcwd()

        with wx.FileDialog(
            self,
            "Open json file",
            defaultDir=cwd,
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
        ) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return  # the user changed their mind

            dataFile = fileDialog.GetPath()
            try:
                with open(dataFile, "r") as file:
                    pass
            except IOError:
                wx.LogError("Cannot open file '%s'." % dataFile)

            self.mapController.map_spinupDataSet(self.panels, dataFile)

    # event capture for time slider

    def map_timeSliderChanged(self, panel, event):
        self.mapController.update_map(panel)
        # self.mapController.query_tpamforSlice(panel,self.tpamFile)

    def map_timeSliderReleased(self, panel, event):
        self.mapController.update_map(panel)
        # self.mapController.query_tpamforSlice(panel,self.tpamFile)
        _thread.start_new_thread(
            self.mapController.query_tpamforSlice, (panel, self.tpamFile)
        )

    # event capture for sim Id drop down

    def map_simIdDropdownChanged(self, panel, event):
        self.mapController.update_map(panel)
        plotPanel = panel.plotPanel
        self.mapController.query_tpamforSlice(panel, self.tpamFile)

    # event capture for response drop down

    def map_responseChanged(self, panel, event):

        if isinstance(panel, MapParentPanel):
            plotFrame = panel.plotPanel
            dataFrame = plotPanel.dataPanel
        elif isinstance(panel, MapControlPanel):
            self.mapController.update_map(panel)
            controlPanel = panel
            plotPanel = panel.plotPanel
            dataPanel = plotPanel.dataPanel

            self.mapController.update_legend(controlPanel)
            # self.mapController.query_tpamforSlice(controlPanel,self.tpamFile)
            _thread.start_new_thread(
                self.mapController.query_tpamforSlice, (panel, self.tpamFile)
            )
            responses = self.mapController.responses
            resp_targ = controlPanel.resp_targ
            currResp = responses[resp_targ]

            if dataPanel is not None:
                self.mapController.write_cellData(plotPanel)

    def update_map(self, panel):
        if isinstance(panel, colorPanel):
            updatePanel = panel.controlPanel
        self.mapController.update_map(updatePanel)
        self.mapController.update_legend(updatePanel)

    def update_legend(self, panel):
        self.mapController.update_legend(panel)

    # mouse moved event

    def settings_handler(self, params, func):
        if "response" in params:
            resp = self.mapController.responses[params["response"]]
            func(resp)

        elif "plotPanel" in params:
            plotPanel = params["plotPanel"].plotPanel
            func(plotPanel)

    def map_mouseMoved(self, panel, event):
        if panel.dataPanel is not None:
            self.mapController.mapDetect_cellChange(panel, event)

    # mouse click event
    def map_mouseClicked(self, panel, event):
        if isinstance(panel, MapPlotPanel):
            self.mapController.cell_selected(panel, event)

    def write_cellData(self, panel, event):
        self.mapController.write_cellData(panel)

    # save button was changed on color props

    def save_snapShot(self):
        self.mapController.snapShot()

    def filter_drop(self, panel, event):
        print("drop filtered")
        if isinstance(panel, MapControlPanel) or isinstance(panel, colorPanel):
            targs = []
            resp_targs = self.mapController.get_reponseNames()
            respName = panel.respDrop.GetStringSelection()

            for string in resp_targs:
                if respName in string:
                    underInd = string.rfind("_")
                    targ = string[underInd + 1 :]
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
