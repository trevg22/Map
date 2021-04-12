import time
from typing import List

import cartopy.crs as ccrs
import matplotlib as mpl
import wx
import wx.grid as grid
import wx.lib.agw.aui as aui
import wx.lib.agw.floatspin as fs
import wx.lib.mixins.inspection as wit
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import \
    NavigationToolbar2WxAgg as NavigationToolbar

import settings
from Polymap import CellPatch
from SettingsPanel import SettingsNotebook


class MapParentPanel(wx.Panel):
    def __init__(self, parent, view):
        super().__init__(parent=parent)
        self.parent = parent
        self.view = view
        self._controlPanel = MapControlPanel(parent, view)
        self._plotPanel = MapPlotPanel(parent, view)

        self._controlPanel.plotPanel = self._plotPanel
        self.plotPanel.controlPanel = self._controlPanel
        self.placePanels()

    def placePanels(self):
        vSizer = wx.BoxSizer(wx.VERTICAL)
        col0 = wx.BoxSizer(wx.HORIZONTAL)
        col1 = wx.BoxSizer(wx.HORIZONTAL)

        col0.Add(self._controlPanel, 1, wx.EXPAND | wx.ALL, 0)
        col1.Add(self._plotPanel, 1, wx.EXPAND | wx.ALL, 0)
        vSizer.Add(col0, 0, wx.EXPAND | wx.ALL, 0)
        vSizer.Add(col1, 1, wx.EXPAND | wx.ALL, 0)

        self.parent.SetSizer(vSizer)

    @property
    def plotPanel(self):
        return self._plotPanel

    @property
    def controlPanel(self):
        return self._controlPanel


class MapControlPanel(wx.Panel):
    def __init__(self, parent, view, *args, **kwargs):
        super().__init__(parent=parent, *args, **kwargs)
        self.view = view
        self._simDrops = []
        self._simIdLabels = []
        self._plotPanel = None
        self._settingsNotebook = None
        

    def place_widgets(self):
        self.grid = wx.FlexGridSizer(5 + len(self.simIdLabels), 3, 3)
        for label in self.simIdLabels:
            self.grid.Detach(label)
            self.grid.Add(label, 0, 0, 2)

        self.timeSpin = fs.FloatSpin(self, size=(60, 25))
        timeLabel = wx.StaticText(self, label="Time")
        timeSpace = wx.StaticText(self, label="")
        self.grid.Add(timeSpace, 0, 0, 0)
        self.timeSlider = wx.Slider(self, -1, style=wx.SL_HORIZONTAL)
        respLabel = wx.StaticText(self, label="Response")
        self.respDrop = wx.ComboBox(self, -1, style=wx.CB_READONLY)
        tgtLabel = wx.StaticText(self, label="Target")
        self.tgtDrop = wx.ComboBox(self, -1, style=wx.CB_READONLY)
        settLabel = wx.StaticText(self, label="Settings")
        self.settButton = wx.Button(self, size=(25, 25), label="\u2699")
        self.grid.Add(timeLabel, 0, 0, 0)
        self.grid.Add(respLabel, 0, 0, 0)
        self.grid.Add(tgtLabel, 0, 0, 0)
        self.grid.Add(settLabel, 0, 0, 0)

        for drop in self.simDrops:
            # self.grid.Detach(drop)
            self.grid.Add(drop, 0, 0, 0)
        self.grid.Add(self.timeSpin, 0, 0, 0)
        self.grid.Add(self.timeSlider, 0, 0, 0)
        self.grid.Add(self.respDrop, 0, 0, 0)
        self.grid.Add(self.tgtDrop, 0, 0, 0)
        self.grid.Add(self.settButton, 0, 0, 0)
        self.SetSizer(self.grid)

    def bind_widgets(self):
        self.timeSlider.Bind(
            wx.EVT_SCROLL_THUMBTRACK, self.timeSlider_update, self.timeSlider
        )
        self.timeSlider.Bind(
            wx.EVT_SCROLL_THUMBRELEASE,
            lambda event: self.view.map_timeSliderReleased(self, event),
            self.timeSlider,
        )
        self.timeSpin.Bind(fs.EVT_FLOATSPIN, self.timeSpin_update, self.timeSpin)
        self.respDrop.Bind(
            wx.EVT_TEXT, lambda event: self.response_update(self, event), self.respDrop
        )
        self.tgtDrop.Bind(
            wx.EVT_TEXT,
            lambda event: self.view.map_responseChanged(self, event),
            self.tgtDrop,
        )

        self.settButton.Bind(
            wx.EVT_BUTTON,
            lambda event: self.view.spawn_settingsPanel(self),
            self.settButton,
        )

    @property
    def resp_targ(self):
        resp = (
            str(self.respDrop.GetStringSelection())
            + "_"
            + (self.tgtDrop.GetStringSelection())
        )
        return resp

    @property
    def plotPanel(self):
        return self._plotPanel

    @property
    def settingsNotebook(self):
        return self._settingsNotebook

    @settingsNotebook.setter
    def settingsNotebook(self, panel):
        self._settingsNotebook = panel

    @property
    def simDrops(self):
        return self._simDrops

    @property
    def simIdLabels(self):
        return self._simIdLabels

    @property
    def simId(self):
        id = ""
        for drop in self.simDrops:
            id = id + str(drop.GetCurrentSelection() + 1)
        return id

    @property
    def target(self):
        return self.tgtDrop.GetStringSelection()

    @property
    def time(self):
        return self.timeSpin.GetValue()

    @plotPanel.setter
    def plotPanel(self, panel):
        self._plotPanel = panel

    @simDrops.setter
    def simDrops(self, drop):
        self._simDrops.append(drop)

    @simIdLabels.setter
    def simIdLabels(self, label):
        self._simIdLabels.append(label)

    def timeSpin_update(self, event):
        timeInc = float(self.timeSpin.GetIncrement())
        sliderIndex = round(self.timeSpin.GetValue() / timeInc)
        self.timeSlider.SetValue(sliderIndex)
        self.view.map_timeSliderChanged(self, None)

    def timeSlider_update(self, event):
        sliderIndex = self.timeSlider.GetValue()
        timeInc = float(self.timeSpin.GetIncrement())
        simTime = sliderIndex * timeInc
        
        self.timeSpin.SetValue(simTime)
        self.view.map_timeSliderChanged(self, None)

    def response_update(self, panel, event):
        self.view.filter_drop(self, event)
        self.view.map_responseChanged(panel, event)


class MapPlotPanel(wx.Panel):
    def __init__(self, parent, view, *args, **kwargs):
        super().__init__(parent=parent)
        self.view = view
        self._dataPanel = None
        self._controlPanel = None
        self._alpha = 0
        self._currCell = None
        self._hoverCell = 0
        self.legendLoc = "lower left"
        self.numThresh = settings.numLegendEntries
        self.text=[]
        self.initPlot()
        self.bind_widgets()

    def initPlot(self, dpi=None):
        self.figure = mpl.figure.Figure(dpi=dpi, figsize=(2, 2))
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.toolbar = NavigationToolbar(self.canvas)
        self.toolbar.Realize()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 1, wx.EXPAND)
        sizer.Add(self.toolbar, 0, wx.LEFT | wx.EXPAND)
        self.SetSizer(sizer)
        self.ax = self.figure.add_subplot(111, projection=ccrs.PlateCarree())

    def bind_widgets(self):
        self.figure.canvas.mpl_connect(
            "motion_notify_event", lambda event: self.view.map_mouseMoved(self, event)
        )

        self.figure.canvas.mpl_connect(
            "pick_event", lambda event: self.view.map_mouseClicked(self, event)
        )

    def plot_cellPatches(self, cellPatches):
        self._cellPatches = cellPatches
        for patch in cellPatches:
            patch.set_facecolor([1, 1, 1])
            self.ax.add_patch(patch)
        self.ax.plot(1, 1, marker=" ")
        self.canvas.draw()
        self.canvas.Refresh()
        # self.Refresh()

    @property
    def patchAlphas(self):
        return self._alpha

    @patchAlphas.setter
    def patchAlphas(self, alpha):
        self._alpha = alpha
        for patch in self._cellPatches:
            patch.set_alpha(self._alpha)

    @property
    def dataBox(self):
        return self._dataBox

    @dataBox.setter
    def dataBox(self, box):
        self._dataBox = box

    @property
    def controlPanel(self):
        return self._controlPanel

    @controlPanel.setter
    def controlPanel(self, frame):
        self._controlPanel = frame

    @property
    def cellPatches(self):
        return self._cellPatches

    @property
    def dataPanel(self):
        return self._dataPanel

    @dataPanel.setter
    def dataPanel(self, panel):
        self._dataPanel = panel

    @property
    def currCell(self):
        return self._currCell

    @currCell.setter
    def currCell(self, cell: CellPatch):
        self._currCell = cell
        self.dataPanel.selectCell = cell.get_cellNum()

    @property
    def hoverCell(self):
        return self._hoverCell

    @hoverCell.setter
    def hoverCell(self, cellNum):
        self._hoverCell = cellNum
        self.dataPanel.hoverCell = cellNum


class MapdataPanel(wx.Panel):
    def __init__(self, parent, view):
        super().__init__(parent=parent)
        self.view = view
        self._plotPanel = None
        self.tpamGrid = None
        self.place_widgets()
        self.config_widgets()
        self.bind_widgets()

    def place_widgets(self):
        self.hoverLabel = wx.StaticText(self, label="Hover:")
        self.selectLabel = wx.StaticText(self, label="Selected:")
        self.dataView = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        self.filterDrop = wx.Choice(self)
        self.dataView.SetMinSize((300, 600))
        col0 = wx.BoxSizer(wx.HORIZONTAL)
        col1 = wx.BoxSizer(wx.HORIZONTAL)
        col2 = wx.BoxSizer(wx.HORIZONTAL)
        col3 = wx.BoxSizer(wx.HORIZONTAL)
        vSizer = wx.BoxSizer(wx.VERTICAL)
        col0.Add(self.hoverLabel, 1, 1, 20)
        col1.Add(self.selectLabel, 1, 1, 20)
        col2.Add(self.filterDrop, 1, 1, 20)
        col3.Add(self.dataView, 1, 1, 20)
        vSizer.Add(col0, 0, 1, 20)
        vSizer.Add(col1, 0, 1, 20)
        vSizer.Add(col2, 0, 1, 20)
        vSizer.Add(col3, 0, 1, 20)

        self.SetSizer(vSizer)
        self.Layout()

    def config_widgets(self):
        filterChoice = ["Response", "Target", "Single"]
        self.filterDrop.AppendItems(filterChoice)
        self.filterDrop.SetSelection(0)

    def bind_widgets(self):
        self.filterDrop.Bind(
            wx.EVT_CHOICE,
            lambda event: self.view.write_cellData(self.plotPanel, event),
            self.filterDrop,
        )

    @property
    def filterMode(self):
        index = self.filterDrop.GetSelection()
        return self.filterDrop.GetString(index)

    @property
    def plotPanel(self):
        return self._plotPanel

    @plotPanel.setter
    def plotPanel(self, panel):
        self._plotPanel = panel

    @property
    def hoverCell(self):
        return self._hoverCell

    @hoverCell.setter
    def hoverCell(self, cellNum):
        self._hoverCell = cellNum
        self.hoverLabel.SetLabel("Hover: " + str(cellNum))

    @property
    def selectCell(self):
        return self._currCell

    @selectCell.setter
    def selectCell(self, cellNum):
        self.selectLabel.SetLabel("Selected: " + str(cellNum))


class TpamGrid(wx.Panel):
    def __init__(self, parent, view):
        super().__init__(parent=parent)

        self.view=view
        sideLabel=wx.StaticText(self,label="Side")
        self.sideDrop=wx.ComboBox(self)
        self.sideDrop.Clear()
        self.sideDrop.AppendItems(["Red","Blue"])
        self.sideDrop.SetSelection(0)
        self.grid = grid.Grid(self)
        self.currRow = 0
        self.grid.CreateGrid(30, 12)
        self.grid.HideColLabels()
        
        vSizer = wx.BoxSizer(wx.VERTICAL)
        hSizer=wx.BoxSizer(wx.HORIZONTAL)
        hSizer.Add(sideLabel,1,1,5)
        hSizer.Add(self.sideDrop,1,1,5)
        vSizer.Add(hSizer,0,0,0)
        vSizer.Add(self.grid, 1, 1, 5)
        self.SetSizer(vSizer)

        self.bind_widgets()

    def bind_widgets(self):
        self.sideDrop.Bind(wx.EVT_TEXT,lambda event:self.view.query_tpamforSlice(event,side=self.sideDrop.GetSelection()))
        
    def write_2d(self, row, data):
        self.grid.InsertRows(self.currRow, 1)

        for row in data:
            self.write_row(row)
            self.currRow = self.currRow + 1

    def write_row(self, data):
        for col, data in enumerate(data):
            self.grid.SetCellValue(self.currRow, col, str(data))
