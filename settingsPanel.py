import wx


class SettingsNotebook(wx.Notebook):
    def __init__(self, view):
        self.view = view
        print("notebook started")
        super().__init__()
        self._colorPanel = None
        self._controlPanel = None
        self._plotPanel = None
        # self.Bind(wx.EVT_WINDOW_CREATE, self.OnCreate)
        # self.AddPage(self.colorPanel, "Color")
        # print("Notebook created")

    def OnCreate(self, event):
        self._colorPanel = colorPanel(self, self.view)
        self._plotPanel = PlotSettingsPanel(self, self.view)
        self.AddPage(self._plotPanel, "Plot")
        self.AddPage(self._colorPanel, "Color")
        print("control panel set to", self._controlPanel)

    @property
    def colorPanel(self):
        return self._colorPanel

    @property
    def controlPanel(self):
        return self._controlPanel

    @controlPanel.setter
    def controlPanel(self, panel):
        self._controlPanel = panel
        self.colorPanel.controlPanel = panel
        self._plotPanel._controlPanel = panel


class ColorPanel(wx.Panel):
    def __init__(self, parent, view):
        super().__init__(parent=parent)
        self.view = view
        self._parent = parent
        self._controlPanel = None

        self.place_widgets()
        self.bind_widgets()
        self.config_defaults()

    def place_widgets(self):
        self._controlPanel = None
        self.respDrop = wx.ComboBox(self)
        self.tgtDrop = wx.ComboBox(self)
        self.colorScaleDrop = wx.ComboBox(self)
        self.save = wx.Button(self, label="apply")
        col0 = wx.BoxSizer(wx.HORIZONTAL)
        col1 = wx.BoxSizer(wx.HORIZONTAL)
        col2 = wx.BoxSizer(wx.HORIZONTAL)

        vSizer = wx.BoxSizer(wx.VERTICAL)

        col0.Add(self.respDrop, 0, 1, 20)
        col0.Add(self.tgtDrop, 0, 1, 20)
        col1.Add(self.colorScaleDrop, 0, 1, 20)
        col2.Add(self.save, 0, 1, 20)

        vSizer.Add(col0, 0, 1, 20)
        vSizer.Add(col1, 0, 1, 20)
        vSizer.Add(col2, 0, 1, 20)
        self.SetSizer(vSizer)

    def bind_widgets(self):
        self.save.Bind(wx.EVT_BUTTON, lambda event: self.save_pressed(event))
        self.respDrop.Bind(
            wx.EVT_COMBOBOX, lambda event: self.view.filter_drop(self, event)
        )

    def config_defaults(self):
        colorScaleChoices = ["viridis", "plasma", "inferno", "magma", "cividis"]
        self.colorScaleDrop.AppendItems(colorScaleChoices)

    def save_pressed(self, event):
        params = {}
        params["response"] = self.resp_targ
        func = self.update_response
        self.view.settings_handler(params, func)
        self.view.update_map(self)

    def update_response(self, response):
        response.cmapStr = self.colorScaleDrop.GetStringSelection()
        print("response updated")

    @property
    def resp_targ(self):
        resp = (
            self.respDrop.GetStringSelection() + "_" + self.tgtDrop.GetStringSelection()
        )
        return resp

    @property
    def controlPanel(self):
        return self._controlPanel

    @controlPanel.setter
    def controlPanel(self, panel):
        self._controlPanel = panel


class PlotSettingsPanel(wx.Panel):
    def __init__(self, parent, view):
        super().__init__(parent=parent)
        self.view = view
        self.place_widgets()
        self.config_defaults()
        self.bind_widgets()
        self._controlPanel = None

    def place_widgets(self):
        grid = wx.FlexGridSizer(2, 3, 5)
        legendLabel = wx.StaticText(self, label="Legend:")
        locLabel = wx.StaticText(self, label="Location")
        self.locDrop = wx.ComboBox(self)
        blank = wx.StaticText(self, label="")
        numThreshLabel = wx.StaticText(self, label="Entries")
        self.numThreshDrop = wx.ComboBox(self)

        grid.Add(legendLabel, 0, 0, 5)
        grid.Add(blank, 0, 0, 5)
        grid.Add(locLabel, 0, 0, 5)
        grid.Add(self.locDrop, 0, 0, 5)
        grid.Add(numThreshLabel, 0, 0, 5)
        grid.Add(self.numThreshDrop, 0, 0, 5)

        self.SetSizer(grid)

    def config_defaults(self):
        legendLocs = ["upper left", "upper right", "lower left", "lower right", "none"]
        self.locDrop.AppendItems(legendLocs)

        threshNums = list(range(2, 6))
        threshNums = [str(x) for x in threshNums]
        self.numThreshDrop.AppendItems(threshNums)

    def bind_widgets(self):
        self.locDrop.Bind(
            wx.EVT_COMBOBOX,
            lambda event: self.widget_updated(self.update_legendLoc, event),
        )
        self.numThreshDrop.Bind(
            wx.EVT_COMBOBOX,
            lambda event: self.widget_updated(self.update_numThresh, event),
        )
        print("widgets bound")

    def widget_updated(self, func, event):
        params = {}
        params["plotPanel"] = self._controlPanel
        self.view.settings_handler(params, func)
        print("widget update called")

    def update_legendLoc(self, plotPanel):
        plotPanel.legendLoc = self.locDrop.GetStringSelection()
        self.view.update_legend(self._controlPanel)

    def update_numThresh(self, plotPanel):
        plotPanel.numThresh = int(self.numThreshDrop.GetStringSelection())
        self.view.update_legend(self._controlPanel)
