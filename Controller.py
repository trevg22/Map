# Map Viewer
# Class to interface directly with model
# and impliment some view functionality
import colorsys
import json
import os
import time
from typing import List

import cartopy.crs as ccrs
import wx
from cartopy.feature import BORDERS, COASTLINE, LAND, NaturalEarthFeature
from matplotlib import cm
from matplotlib.image import imread
from matplotlib.patches import Patch

import settings
from ColorFrame import ColorParentFrame
from DataReader import Reader, indepVar, simInst
from MapModel import MapModel
from Polymap import CellPatch, PolygonPath
from Response import Response
from WxFrames import MapControlPanel, MapParentPanel, MapPlotPanel


class Controller:
    def __init__(self, view):
        self.MapModel = MapModel()
        self.currCell = None
        self.selected_cell = None
        self.view = view
        self.tpamSlice = None
        self.prevTime = -1
        self.prevSimId = -1
        self.prevTarget = -1
        self.prevSide = -1

    # read in data and config widgets based on data
    def map_spinupDataSet(self, frames, mavFile):
        self.MapModel.read_mav(mavFile)
        self.initialize_respObjs()
        self.MapModel.create_cells()
        vorCells = self.MapModel.get_vorCells()
        self.create_cellPatches(vorCells)
        # self.config_widgets(frames)

    # creat cellPatches from voronoi polygons

    def create_cellPatches(self, vorCells):
        cellPatches = []
        for cell in vorCells:
            path = PolygonPath(cell.polygon)
            cellPatch = CellPatch(path, cell, picker=True, alpha=0.3)
            cellPatches.append(cellPatch)
        return cellPatches

    # config widgets based on data input
    def config_widgets(self, frames):
        for frame in frames:
            if isinstance(frame, MapParentFrame):
                self.config_mapPlot(frame)
                self.config_mapWidgets(frame.controlFrame)

            elif isinstance(frame, ColorParentFrame):
                self.config_colorWidgets(frame)

            elif isinstance(frame, MapControlFrame):
                self.config_mapWidgets(frame)

    # config map widgets sliders/dropdowns
    def config_controlWidgets(self, panel: MapControlPanel):

        # Config ind var dropdowns
        indVars: List[indepVar] = self.MapModel.get_indepVars()
        for var in indVars:
            # drop = ttk.Combobox(frame)
            maxWidth = 0
            for label in var.labels:
                if len(label) > maxWidth:
                    maxWidth = len(label)
            drop = wx.ComboBox(panel, style=wx.CB_READONLY)
            drop.AppendItems(var.labels)
            drop.SetSelection(0)
            drop.Bind(
                wx.EVT_TEXT,
                lambda event: self.view.map_simIdDropdownChanged(panel, event),
            )
            label = wx.StaticText(panel, label=str(var.name))
            panel.simIdLabels = label
            panel.simDrops = drop
        panel.place_widgets()
        panel.bind_widgets()
        resp_targs = self.MapModel.get_responseNames()
        self.query_tpamforSlice(panel, "tpam2.json")
        timeRange, stepsPerDay = self.MapModel.get_timeParams()
        timeSliderRes = 1 / stepsPerDay
        panel.timeSlider.SetMin(timeRange[0])
        panel.timeSlider.SetMax(timeRange[1] * stepsPerDay)
        panel.timeSlider.SetTickFreq(1)
        panel.timeSpin.SetRange(timeRange[0], timeRange[1])
        panel.timeSpin.SetFormat("%f")
        panel.timeSpin.SetDigits(2)
        panel.timeSpin.SetIncrement(0.25)

        targNamelen = 0
        respNameLen = 0

        respNames = []
        targNames = []
        for string in resp_targs:
            underInd = string.rfind("_")
            respName = string[:underInd]
            targName = string[underInd + 1 :]
            if len(targName) > targNamelen:
                targNamelen = len(targName)

            if len(respName) > respNameLen:
                respNameLen = len(respName)

            if targName not in targNames:
                targNames.append(targName)
            if respName not in respNames:
                respNames.append(respName)
                panel.respDrop.Clear()
        panel.respDrop.AppendItems(respNames)
        panel.respDrop.SetSelection(0)
        self.view.filter_drop(panel, None)

    def config_settingsNoteBook(self, book, controlPanel):
        colorPanel = book.colorPanel
        numRespNames = controlPanel.respDrop.GetCount()
        respNames = []
        for x in range(numRespNames):
            respNames.append(controlPanel.respDrop.GetString(x))

        colorPanel.respDrop.AppendItems(respNames)
        colorPanel.respDrop.SetSelection(0)
        self.view.filter_drop(colorPanel, None)
        resp_targ = colorPanel.resp_targ
        currResp = self.responses[resp_targ]
        colorPanel.colorScaleDrop.SetValue(currResp.cmapStr)

        # config matplotlib fig/plot cellpatches

    def config_mapPlot(self, panel: MapParentPanel):
        plotPanel: MapPlotPanel = panel.plotPanel
        cwd = os.getcwd()
        background = "natural-earth.png"
        backPath = os.path.join(cwd, background)
        if os.path.exists(backPath):
            plotPanel.ax.imshow(
                imread(backPath),
                origin="upper",
                transform=ccrs.PlateCarree(),
                extent=[-180, 180, -90, 90],
            )
        cellCenters = self.MapModel.get_cellCenters()
        xrange, yrange = self.get_vorPlotLim(cellCenters)
        plotPanel.ax.set_xlim(xrange)
        plotPanel.ax.set_ylim(yrange)
        states_provinces = NaturalEarthFeature(
            category="cultural",
            name="admin_1_states_provinces_lines",
            scale="50m",
            facecolor="none",
        )

        plotPanel.ax.add_feature(LAND)
        plotPanel.ax.add_feature(COASTLINE)
        plotPanel.ax.add_feature(BORDERS)
        plotPanel.ax.add_feature(states_provinces, edgecolor="gray", facecolor="none")

    # update map based on control widget values

    def update_map(self, panel):
        print("updating map with", type(panel))
        if isinstance(panel, MapControlPanel):
            plotPanel: MapPlotPanel = panel.plotPanel
            controlPanel: MapControlPanel = panel

        elif isinstance(panel, MapParentPanel):
            plotPanel: MapPlotPanel = panel.plotPanel
            controlPanel: MapControlPanel = panel.controlPanel

        plotPanel.patchAlphas = 0.3

        vorCells = self.MapModel.get_vorCells()
        numCells = len(vorCells)
        responses = self.responses
        simIndex = self.find_currSimIndex(controlPanel)
        timeRange, stepsPerDay = self.MapModel.get_timeParams()
        timeStep = controlPanel.timeSpin.GetValue()
        densityOn = 0
        timeIndex = round(timeStep * stepsPerDay)

        resp_targ = controlPanel.resp_targ
        currResp = self.responses[resp_targ]

        responseIndex = currResp.index

        if densityOn:
            densityMax = self.MapModel.find_normalizedMax(responseIndex)
        dataList = []

        for cell in range(numCells):
            data = self.MapModel.get_dataBySimTimeCellResp(
                simIndex, timeIndex, cell + 1, responseIndex
            )
            dataList.append(data)
            if densityOn:
                area = vorCells[cell].area
                color = currRespgen_colorNorm(data, densityMax, area)
            else:
                color = currResp.gen_color(data)
                color = currResp.gen_cmapColor(data)
            # update color on plot
            plotPanel.cellPatches[cell].set_facecolor(color)
            if color != [1, 1, 1]:
                plotPanel.cellPatches[cell].set_alpha(1)
            else:
                pass

        plotPanel.figure.subplots_adjust(
            bottom=0, top=1, left=0, right=1, wspace=0, hspace=0
        )
        plotPanel.canvas.draw()

        # resp = responses[responseIndex]
        # ax = plotPanel.ax
        # fig = plotPanel.figure
        # cax = fig.add_axes([.27, .8, .5, .05])
        # ax.colorbar(cm.ScalarMappable(norm=resp.normalizer,
        #                              cmap=resp.cmapStr), cax=ax, orientation='horizontal', loc=11)
        # ax.colorbar(

        # print("axes", ax)
        # ax.figure.colorbar(norm=resp.normalizer, cmap=resp.cmapStr, ax=ax)

    # create/update legend based on param values

    def update_legend(self, panel):
        if isinstance(panel, MapParentPanel):
            controlPanel: MapControlPanel = panel.controlPanel
            plotPanel: MapPlotPanel = panel.plotPanel

        elif isinstance(panel, MapControlPanel):
            controlPanel: MapControlPanel = panel
            plotPanel: MapPlotPanel = controlPanel.plotPanel

        numThresh = plotPanel.numThresh
        resp_targ = controlPanel.resp_targ

        response: Response = self.responses[resp_targ]
        responseIndex = response.index

        max1 = response.max
        min1 = response.min
        lowThresh = response.smallValPerc
        patches = []
        smallVal = max1 * lowThresh

        lowLabel = ">" + "{:.2e}".format(smallVal)
        patches.append(Patch(facecolor=[1, 1, 1], label=lowLabel))
        for x in range(numThresh):
            colorThresh = ((x + 1) * (max1 - min1) / (numThresh)) + min1
            # color = response.gen_color(colorThresh)
            color = response.gen_cmapColor(colorThresh)
            dataThresh = str("{:.2f}".format(colorThresh))
            patches.append(Patch(facecolor=color, label=dataThresh))

        location = plotPanel.legendLoc
        if location == "none":
            plotPanel.ax.legend().set_visible(False)
        else:
            plotPanel.ax.legend(handles=patches, loc=location)
        plotPanel.canvas.draw()

    # generate a color based on linear scaled
    # hue currently hard coded

    def find_currSimIndex(self, panel: MapControlPanel):
        simId = panel.simId
        simList: List[simInst] = self.MapModel.get_simList()

        for index, sim in enumerate(simList):
            simPrefix = "".join([str(x) for x in sim.simPrefix])
            if simPrefix == simId:
                return index
        print("Sim Index not found")
        return 0

    # detect if the mouse has changed cell

    def mapDetect_cellChange(self, panel: MapPlotPanel, event):
        if event.inaxes == panel.ax:
            # Check if mouse in is currCell
            mouse_in_cell = self.MapModel.is_point_in_cell(
                event.xdata, event.ydata, self.currCell
            )
            if mouse_in_cell == False:
                # find what cell mouse is in
                self.currCell, found = self.MapModel.determine_cell_from_point(
                    event.xdata, event.ydata
                )

                if found:
                    panel.hoverCell = self.currCell
                else:
                    pass
            else:
                pass

    # if cell is selected highlight cell and write databox
    def cell_selected(self, panel: MapPlotPanel, event):
        print("cell selected")
        artist = event.artist
        if self.selected_cell is not None:
            self.selected_cell.set_linewidth(1.0)
        artist.set_linewidth(3.0)

        self.selected_cell = artist
        panel.currCell = artist

        if panel.dataPanel is not None and panel.currCell is not None:
            self.write_cellData(panel)
            self.write_tpamData(panel)
        panel.canvas.draw()

    # write data box if cell is selected

    def write_cellData(self, panel):
        if panel.currCell is not None:
            if isinstance(panel, MapPlotPanel):
                controlPanel = panel.controlPanel
                cell = panel.currCell
                dataPanel: MapdataPanel = panel.dataPanel
            elif isinstance(panel, MapParentPanel):
                controlPanel = panel.controlPanel
                dataPanel = panel.plotPanel.dataPanel
            if dataPanel is not None:
                responses = self.MapModel.get_responseNames()
                resp_targ = (
                    str(controlPanel.respDrop.GetStringSelection())
                    + "_"
                    + (controlPanel.tgtDrop.GetStringSelection())
                )
                dataView = dataPanel.dataView
                simIndex = self.find_currSimIndex(controlPanel)
                stepsPerDay = self.MapModel.get_timeParams()[1]
                timeStep = controlPanel.timeSpin.GetValue()

                timeIndex = round(timeStep * stepsPerDay)
                # response = controlFrame.get_respDropDownIndex()
                vorCells = self.MapModel.get_vorCells()
                densityOn = 0
                scaleFac = 1
                cellNum = cell.get_cellNum()
                dataView.Clear()
                filterStr = ""
                underPos = resp_targ.find("_")
                print("filter mode", dataPanel.filterMode)
                if dataPanel.filterMode == "Single":
                    filterStr = resp_targ

                elif dataPanel.filterMode == "Response":
                    filterStr = resp_targ[:underPos]

                elif dataPanel.filterMode == "Target":
                    filterStr = resp_targ[underPos:]

                for index, response in enumerate(responses):
                    data = self.MapModel.get_dataBySimTimeCellResp(
                        simIndex, timeIndex, cellNum, index
                    )
                    if densityOn:
                        area = vorCells[cellNum - 1].area
                        data = (data * scaleFac) / area

                    dataLine = response + ": " + "{0:.2f}".format(data) + "\n"
                    if response == resp_targ:
                        dataView.write(dataLine)
                    elif filterStr in response:
                        dataView.write(dataLine)

    def write_tpamData(self, plotPanel):
        dataPanel = plotPanel.dataPanel
        controlPanel = plotPanel.controlPanel
        tpamPanel = dataPanel.tpamGrid
        cell = plotPanel.currCell

        for row in range(tpamPanel.grid.GetNumberRows()):
            tpamPanel.grid.SetRowLabelValue(row, "")
        tpamPanel.grid.ClearGrid()
        if plotPanel.currCell is not None:
            cellNum = cell.get_cellNum()

            if self.tpamSlice is not None and "c" + str(cellNum) in self.tpamSlice:
                cellSlice = self.tpamSlice["c" + str(cellNum)]
                kam = cellSlice["K"]
                currRow = 0
                tpamPanel.grid.SetCellValue(currRow, 0, "KAM")
                tpamPanel.grid.SetCellValue(currRow + 1, 0, "Alive")
                tpamPanel.grid.SetCellValue(currRow + 1, 1, "Pres Alive")
                tpamPanel.grid.SetCellValue(currRow + 1, 2, "Pres Dead")
                tpamPanel.grid.SetCellValue(currRow + 1, 3, "Dead")
                currRow = currRow + 2
                tpamPanel.grid.SetRowLabelValue(currRow, "Alive")
                tpamPanel.grid.SetRowLabelValue(currRow + 1, "Dead")
                for rIndex, row in enumerate(kam):
                    for cIndex, col in enumerate(row):
                        tpamPanel.grid.SetCellValue(
                            rIndex + currRow, cIndex, str(row[cIndex])
                        )
                currRow = currRow + 2
                currRow = currRow + 1
                tpamPanel.grid.SetCellValue(currRow, 0, "Lam")
                currRow = currRow + 1
                tpamPanel.grid.SetRowSize(
                    currRow, 2 * tpamPanel.grid.GetDefaultRowSize()
                )
                tpamPanel.grid.SetCellValue(currRow, 0, "Moving &\nDetected")
                tpamPanel.grid.SetCellValue(currRow, 1, "Moving &\nTracked")
                tpamPanel.grid.SetCellValue(currRow, 2, "Moving &\nTracked")
                tpamPanel.grid.SetCellValue(currRow, 3, "Stopped &\nImaged")
                tpamPanel.grid.SetCellValue(currRow, 4, "Lost")
                currRow = currRow + 1
                tpamPanel.grid.SetRowLabelValue(currRow, "Moving")
                tpamPanel.grid.SetRowLabelValue(currRow + 1, "Stopped")
                tpamPanel.grid.SetRowLabelValue(currRow + 2, "Hiding")
                lam = cellSlice["L"]
                for rIndex, row in enumerate(lam):
                    for cIndex, col in enumerate(row):
                        tpamPanel.grid.SetCellValue(
                            rIndex + currRow, cIndex, str(row[cIndex])
                        )

                currRow = currRow + 4
                tpamPanel.grid.SetCellValue(currRow, 0, "IDAM")
                currRow = currRow + 1
                idam = cellSlice["I"]
                col = 0
                row = 0
                for ele in idam:

                    if col == 5:
                        col = 0
                        row = row + 1
                    tpamPanel.grid.SetCellValue(row + currRow, col, str(ele))
                    col = col + 1
            else:
                tpamPanel.grid.SetCellValue(0, 0, "No Tpam data")
        else:
            tpamPanel.grid.SetCellValue(0, 0, "No Cell Selected")

    def initialize_respObjs(self):
        default_hue = 185
        responsesNames = self.get_reponseNames()
        simList = self.MapModel.get_simList()
        self.responses = {}
        for index, resp_targ in enumerate(responsesNames):
            resp = Response()
            resp.find_respMax(simList, index)
            resp.find_respMin(simList, index)
            resp.gen_cmap("viridis")
            resp.hue = default_hue
            resp.type = "linear"
            resp.index = index
            self.responses[resp_targ] = resp

    def snapShot(self):

        virtFrame = MapParentFrame("virtMap", self.view)
        virtFrame.init_frames(None)
        self.config_widgets([virtFrame])
        controlFrame = virtFrame.get_controlFrame()
        plotFrame = virtFrame.get_plotFrame()
        responseNames = self.get_reponseNames()
        with open("snapshots.json", "r") as f:
            data = json.load(f)

            snapshots = data["snaps"]

        cwd = os.getcwd()
        snapPath = os.path.join(cwd, "snaps")
        if not os.path.exists(snapPath):
            os.mkdir(snapPath)
        for snap in snapshots:
            name = snap["name"]
            simId: List[int] = [int(x) for x in list(snap["simId"])]
            resp_targ = str(snap["response"])
            underInd = resp_targ.rfind("_")
            resp = resp_targ[:underInd]
            targ = resp_targ[underInd + 1 :]
            times = snap["times"]
            hue = snap["hue"]
            if "zoom" in snap:
                zoom = snap["zoom"]
                plotFrame.ax.set_ylim(zoom[1][0], zoom[1][1])
                plotFrame.ax.set_xlim(zoom[0][0], zoom[0][1])

            if "legendLoc" in snap:
                plotFrame.legendLoc = str(snap["legendLoc"])
            controlFrame.set_runDrops(simId)
            respIndex = responseNames.index(resp_targ)

            controlFrame.set_respDropIndex(responseNames[respIndex])
            controlFrame.respDropDown.set(resp)
            controlFrame.targDropDown.set(targ)
            currResp = self.responses[respIndex]
            prevHue = currResp.hue
            currResp.hue = hue

            for time in times:
                self.update_legend(controlFrame)
                controlFrame.timeSlider.set(time)
                self.update_map(controlFrame)
                imgName = os.path.join(
                    snapPath,
                    str(name)
                    + "_"
                    + str(simId)
                    + "_"
                    + str(resp_targ)
                    + "_"
                    + str(time)
                    + ".png",
                )
                plotFrame.fig.savefig(imgName, bbox_inches="tight")

        currResp.hue = prevHue

    def plot_cellPatches(self, frame):
        vorCells = self.MapModel.get_vorCells()
        frame.plot_cellPatches(self.create_cellPatches(vorCells))

    def get_vorPlotLim(self, cellCenters):

        coordsInv = zip(*cellCenters)
        coordsInv = list(coordsInv)
        min_x = min(coordsInv[0])
        max_x = max(coordsInv[0])
        min_y = min(coordsInv[1])
        max_y = max(coordsInv[1])
        return [[min_x, max_x], [min_y, max_y]]

    def get_reponseNames(self):
        return self.MapModel.get_responseNames()

    def query_tpamforSlice(self, panel, fileName):
        controlPanel = panel
        simId = controlPanel.simId
        target = controlPanel.target
        stepsPerDay = self.MapModel.get_timeParams()[1]
        timeStep = controlPanel.timeSpin.GetValue()
        time = round(timeStep * stepsPerDay)
        side = 0
        if (
            simId != self.prevSimId
            or time != self.prevTime
            or side != self.prevSide
            or target != self.prevTarget
        ):
            self.tpamSlice = self.MapModel.getTpamByTimeSideTarget(
                fileName, simId, time, side, target
            )
            self.prevSimId = simId
            self.prevTime = time
            self.prevSide = side
            self.prevTarget = target

        plotPanel = controlPanel.plotPanel
        dataPanel = plotPanel.dataPanel
        if dataPanel is not None:
            self.write_tpamData(plotPanel)
