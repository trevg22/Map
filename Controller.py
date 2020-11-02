# Map Viewer
# Class to interface directly with model
# and impliment some view functionality
import colorsys
import time

from descartes import PolygonPatch
from matplotlib.patches import Patch

from data_reader import Reader
from mapFrame import MapControlFrame, MapParentFrame, MapPlotFrame
from mapModel import mapModel
from Polymap import CellPatch, PolygonPath
from ColorFrame import ColorParentFrame
from tkinter import font
import tkinter as tk
from Response import Response


class Controller:

    def __init__(self):
        self.mapModel = mapModel()
        self.currCell = None
        self.selected_cell = None

    # read in data and config widgets based on data
    def map_spinupDataSet(self, frames, mavFile):
        self.mapModel.read_mav(mavFile)
        self.mapModel.read_colorJson('colors.json')
        self.initialize_respObjs()
        self.mapModel.create_cells()
        vorCells = self.mapModel.get_vorCells()
        self.create_cellPatches(vorCells)
        self.config_widgets(frames)

    # creat cellPatches from voronoi polygons
    def create_cellPatches(self, vorCells):
        cellPatches = []
        for cell in vorCells:
            path = PolygonPath(cell.polygon)
            cellPatch = CellPatch(path, cell, picker=True)
            cellPatches.append(cellPatch)
        return cellPatches

    # config widgets based on data input
    def config_widgets(self, frames):
        for frame in frames:
            if isinstance(frame, MapParentFrame):
                self.config_mapPlot(frame)
                self.config_mapWidgets(frame.controlFrame)

            if isinstance(frame, ColorParentFrame):
                self.config_colorWidgets(frame)

    def config_colorWidgets(self, frame):
        responsesNames = self.mapModel.get_responseNames()
        responses = self.responses
        frame.config_respDrop(values=responsesNames)
        frame.set_respDropIndex(responsesNames[0])
        minVal = responses[0].min
        maxVal = responses[0].max
        hue = responses[0].hue
        frame.update_entrys(minVal, maxVal, hue)
        print("configuring colors")

    # config map widgets sliders/dropdowns
    def config_mapWidgets(self, frame):
        simIds = self.mapModel.get_simIdList()
        responses = self.mapModel.get_responseNames()
        timeRange, stepsPerDay = self.mapModel.get_timeParams()
        timeSliderRes = 1/stepsPerDay
        frame.config_timeSlider(resolution=timeSliderRes, from_=timeRange[0],
                                to=timeRange[1], digits=4)
        frame.config_timeSpin(increment=timeSliderRes,
                              from_=timeRange[0], to=timeRange[1], format="%5.2f",width=7)
        
        frame.config_respDrop(values=responses)
        frame.config_simIdDrop(values=simIds)
        frame.set_simIdDropIndex(simIds[0])
        frame.set_respDropIndex(responses[0])

    # config matplotlib fig/plot cellpatches
    def config_mapPlot(self, frame):
        cellCenters = self.mapModel.get_cellCenters_merc()
        xrange, yrange = self.get_vorPlotLim(cellCenters)
        self.plot_cellPatches(frame)
        frame.set_plotLims(xrange, yrange)

    # update map based on control widget values
    def update_map(self, frame):
        if isinstance(frame, MapControlFrame):
            plotFrame = frame.get_master().get_mapFrame()

        vorCells = self.mapModel.get_vorCells()
        responses = self.responses
        simIndex = frame.get_simIdDropIndex()
        timeRange, stepsPerDay = self.mapModel.get_timeParams()
        timeStep = frame.get_timeSliderVal()
        densityOn = frame.get_densityToggle()
        timeIndex = round(timeStep*stepsPerDay)
        response = frame.get_respDropIndex()
        numCells = len(vorCells)

        if densityOn:
            densityMax = self.mapModel.find_normalizedMax(response)

        for cell in range(numCells):
            data = self.mapModel.get_dataBySimTimeCellResp(
                simIndex, timeIndex, cell+1, response)
            if densityOn:
                area = vorCells[cell].area
                color = responses[response].gen_colorNorm(
                    data, densityMax, area)
            else:
                color = responses[response].gen_color(data)
            # update color on plot
            plotFrame.update_cellPatch(color, cell+1)
                
        plotFrame.draw_canvas()

    # create/update legend based on param values
    def update_legend(self, numThresh, frame):
        responseIndex = frame.get_respDropIndex()
        responses = self.responses
        response = responses[responseIndex]
        max = response.max
        patches = []
        for x in range(numThresh):
            colorThresh = max/(x+1)
            color = response.gen_color(colorThresh)
            colorStr = str("{:.2f}".format(colorThresh))
            patches.append(Patch(facecolor=color, label=colorStr))

        plotFrame = frame.get_plotFrame()

        plotFrame.set_legend(patches)

    # generate a color based on linear scaled
    # hue currently hard coded

    def gen_colorLinear(self, data, max):
        # Hue value from HSL color standard(0-360 degrees)
        hue = 197
        hueFrac = hue/360  # normalize hue
        sat = 1  # represents 100 percent
        threshold = .90  # maximum light value to avoid moving to black

        if max > 0 and data is not None:
            lightness = (1-(data/max)*threshold)
            color = colorsys.hls_to_rgb(hueFrac, lightness, sat)
        else:
            color = [1, 0, 0]
        return color

    # detect if the mouse has changed cell
    def mapDetect_cellChange(self, frame, event):
        if event.inaxes == frame.get_axes():
            # Check if mouse in is currCell
            mouse_in_cell = self.mapModel.is_point_in_cell(
                event.xdata, event.ydata, self.currCell)
            # print("Mouse in Cell", mouse_in_cell)
            if mouse_in_cell == False:
                # find what cell mouse is in
                self.currCell, found = self.mapModel.determine_cell_from_point(
                    event.xdata, event.ydata)

                if found:
                    frame.set_hoverCell(self.currCell)
                    frame.get_dataFrame().write_hoverLabel(self.currCell)
                    #print("changed to cell : ", self.currCell)
                else:
                    pass
                    # return 0;
                    print("outside grid")
            else:
                pass
                # return -1
                # print("same cell")

    # if cell is selected highlight cell and write databox
    def cell_selected(self, frame, event):
        artist = event.artist
        if self.selected_cell is not None:
            self.selected_cell.set_linewidth(1.0)
        artist.set_linewidth(3.0)

        self.selected_cell = artist
        frame.set_currCell(artist)

        if frame.get_dataFrame() is not None:
            self.write_cellData(frame, artist)
        frame.draw_canvas()
        print("cell selected")
    # write data box if cell is selected
    def write_cellData(self, frame, cell):

        responses = self.mapModel.get_responseNames()
        if isinstance(frame, MapPlotFrame):
            controlFrame = frame.get_controlFrame()
        currResponse=controlFrame.get_respDropIndex()
        dataFrame = frame.get_dataFrame()
        textwidget=dataFrame.textBox
        bFont=font.Font(textwidget,textwidget.cget("font"))
        bFont.config(weight="bold")
        nFont=font.Font(textwidget,textwidget.cget("font"))
        textwidget.tag_configure("bold",font=bFont)
        simIndex = controlFrame.get_simIdDropIndex()
        timeRange, stepsPerDay = self.mapModel.get_timeParams()
        timeStep = controlFrame.get_timeSliderVal()
        
        timeIndex = round(timeStep*stepsPerDay)
        #response = controlFrame.get_respDropDownIndex()
        vorCells = self.mapModel.get_vorCells()
        densityOn = controlFrame.get_densityToggle()
        scaleFac = controlFrame.get_densityScaleFac()
        cellNum=cell.get_cellNum()
        dataFrame.clear()
        for index, response in enumerate(responses):
            data = self.mapModel.get_dataBySimTimeCellResp(
                simIndex, timeIndex, cellNum, index)
            if densityOn:
                area=vorCells[cellNum-1].area
                data = (data*scaleFac)/area
            dataLine = response+": "+"{0:.2f}".format(data)+"\n"
            # if index==currResponse:
            #     print("should be bold")
            #     textwidget.config(font=bFont)
            # else:
            #     textwidget.config(font=nFont)
            textwidget.insert(tk.END,dataLine)
        dataFrame.view_currLine()
        dataFrame.write_selectedLabel(cell)

    def initialize_respObjs(self):
        default_hue = 132
        responsesNames = self.get_reponseNames()
        simList = self.mapModel.get_simList()
        self.responses = []

        for index, name in enumerate(responsesNames):
            resp = Response()
            resp.find_respMax(simList, index)
            resp.find_respMin(simList, index)
            resp.hue = default_hue
            resp.type = "linear"
            self.responses.append(resp)

    def snapShot(self):

        virtFrame = MapParentFrame("virtMap", self.view)
        virtFrame.init_frames(None)
        self.config_widgets([virtFrame])
        controlFrame = virtFrame.get_controlFrame()
        plotFrame = virtFrame.get_mapFrame()
        responseNames = self.get_reponseNames()
        with open("snapshots.json", "r") as f:
            data = json.load(f)

            snapshots = data["snaps"]

        print(snapshots)
        cwd = os.getcwd()
        snapPath = os.path.join(cwd, "snaps")
        if not os.path.exists(snapPath):
            os.mkdir(snapPath)
        for snap in snapshots:
            name = snap["name"]
            simIndex = snap["simIndex"]
            response = str(snap["response"])
            times = snap["times"]
            hue = snap["hue"]
            zoom = snap["zoom"]
            respIndex = responseNames.index(response)
            controlFrame.set_respDropIndex(responseNames[respIndex])
            currResp = self.responses[respIndex]
            prevHue = currResp.hue
            currResp.hue = hue
            plotFrame.ax.set_ylim(zoom[1][0], zoom[1][1])
            plotFrame.ax.set_xlim(zoom[0][0], zoom[0][1])
            for time in times:
                controlFrame.timeSlider.set(time)
                self.update_map(controlFrame)
                imgName = os.path.join(snapPath, str(
                    name)+"_"+str(simIndex)+"_"+str(response)+"_"+str(time)+".png")
                plotFrame.fig.savefig(imgName)

        currResp.hue = prevHue

    def plot_cellPatches(self, frame):
        vorCells = self.mapModel.get_vorCells()
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
        return self.mapModel.get_responseNames()
