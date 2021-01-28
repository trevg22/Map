from typing import List

import cartopy.crs as ccrs
import matplotlib as mpl
import settings
import wx
import wx.lib.agw.aui as aui
import wx.lib.agw.floatspin as fs
import wx.lib.mixins.inspection as wit
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import \
    NavigationToolbar2WxAgg as NavigationToolbar


class MapParentPanel(wx.Panel):
    def __init__(self, parent, view):
        super().__init__(parent=parent)
        self.parent = parent
        self.view = view
        self._controlPanel = MapControlPanel(parent, view)
        self._plotPanel = MapPlotPanel(parent,view)

        self._controlPanel.plotPanel=self._plotPanel
        self.plotPanel.controlPanel=self._controlPanel
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
        self.view=view
        self._simDrops = []
        self._simIdLabels = []
        self._plotPanel = None
        self.place_widgets()
        self.bind_widgets()

    def place_widgets(self):
        self.timeSpin = fs.FloatSpin(self)
        
        timeLabel = wx.StaticText(self, label="Time")
        self.timeSlider = wx.Slider(
            self, -1, style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS)
        respLabel = wx.StaticText(self, label="Response")
        self.respDrop = wx.ComboBox(self, -1, style=wx.CB_READONLY)
        self.tgtDrop = wx.ComboBox(self, -1, style=wx.CB_READONLY)
        self.col0 = wx.BoxSizer(wx.HORIZONTAL)
        self.col0.Add(timeLabel, 1, 1, 20)
        self.col0.Add(respLabel, 1, 1, 20)
        self.col1 = wx.BoxSizer(wx.HORIZONTAL)
        self.col1.Add(self.timeSpin, 0, 1, 20)
        self.col1.Add(self.timeSlider, 0, 1, 20)
        self.col1.Add(self.respDrop, 1, 0, 20)
        self.col1.Add(self.tgtDrop, 1, 0, 20)
        rowSizer = wx.BoxSizer(wx.VERTICAL)
        rowSizer.Add(self.col0, 0, 1, 20)
        rowSizer.Add(self.col1, 1, 20)
        self.SetSizer(rowSizer)

    def bind_widgets(self):
        self.timeSlider.Bind(wx.EVT_SCROLL_THUMBTRACK,
                             self.timeSlider_update, self.timeSlider)
        # self.timeSlider.Bind(wx.EVT_SCROLL_THUMBRELEASE, lambda event: self.view.map_timeSliderReleased(
            # self, event), self.timeSlider)
        self.timeSpin.Bind(
            fs.EVT_FLOATSPIN, self.timeSpin_update, self.timeSpin)

    @ property
    def plotPanel(self):
        return self._plotPanel
    
    @ property
    def simDrops(self):
        return self._simDrops

    @ property
    def simIdLabels(self):
        return self._simIdLabels

    @property
    def simId(self):
        id=""
        for drop in self.simDrops:
            id=id+str(drop.GetCurrentSelection()+1)
        return id
    @ plotPanel.setter
    def plotPanel(self, panel):
        self._plotPanel = panel

    @ simDrops.setter
    def simDrops(self, drop):
        self._simDrops.append(drop)
        self.col1.Insert(0, drop, 0, 0, 20)

    @ simIdLabels.setter
    def simIdLabels(self, label):
        self._simIdLabels.append(label)
        self.col0.Insert(0, label, 0, 0, 20)

    def timeSpin_update(self, event):
        timeInc = float(self.timeSpin.GetIncrement())
        sliderIndex = round(self.timeSpin.GetValue()/timeInc)
        self.timeSlider.SetValue(sliderIndex)
        self.view.map_timeSliderReleased(self,None)

    def timeSlider_update(self, event):
        sliderIndex = self.timeSlider.GetValue()
        timeInc = float(self.timeSpin.GetIncrement())
        simTime = sliderIndex*timeInc
        self.timeSpin.SetValue(simTime)
        self.view.map_timeSliderReleased(self,None)


class MapPlotPanel(wx.Panel):

    def __init__(self, parent,view, *args, **kwargs):
        super().__init__(parent=parent)
        self.view=view
        self._dataPanel = None
        self._controlPanel = None
        self._alpha = 0
        self.legendLoc = settings.defLegendLoc
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
            "motion_notify_event", lambda event: self.view.map_mouseMoved(self, event))
        
        self.figure.canvas.mpl_connect(
            'pick_event', lambda event: self.view.map_mouseClicked(self, event))


    def plot_cellPatches(self, cellPatches):
        self._cellPatches = cellPatches
        for patch in cellPatches:
            patch.set_facecolor([1, 1, 1])
            self.ax.add_patch(patch)
        self.ax.plot(1, 1, marker=' ')
        self.canvas.draw()
        self.canvas.Refresh()
        # self.Refresh()

    @ property
    def patchAlphas(self):
        return self._alpha

    @ patchAlphas.setter
    def patchAlphas(self, alpha):
        self._alpha = alpha
        for patch in self._cellPatches:
            patch.set_alpha(self._alpha)

    @ property
    def dataBox(self):
        return self._dataBox

    @ dataBox.setter
    def dataBox(self, box):
        self._dataBox = box

    @ property
    def controlPanel(self):
        return self._controlPanel

    @ controlPanel.setter
    def controlPanel(self, frame):
        self._controlPanel = frame

    @property
    def cellPatches(self):
        return self._cellPatches

    @property
    def dataPanel(self):
        return self._dataPanel
    
    @dataPanel.setter
    def dataPanel(self,panel):
        self._dataPanel=panel

    @property
    def currCell(self):
        return self._currCell

    @currCell.setter
    def currCell(self,cell):
        self._currCell=cell

class MapdataPanel(wx.Panel):

    def __init__(self,parent,view):
        super().__init__(parent=parent)
        self.view=view
        self.dataView=wx.TextCtrl(self,style=wx.TE_MULTILINE)
        self.filterMode='Response'
        self.place_widgets()

    def place_widgets(self):
        col0=wx.BoxSizer(wx.HORIZONTAL)
        vSizer=wx.BoxSizer(wx.VERTICAL)
        col0.Add(self.dataView,1,1,20)
        vSizer.Add(col0,1,1,20)
        self.SetSizer(vSizer)

def main():
    app = wx.App()
    frame = WxFrame(None, title='Centering')
    mPanel = MapControlPanel(frame, None)
    frame.Show()
    app.MainLoop()


if __name__ == "__main__":
    main()
