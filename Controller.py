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


class Controller:

    def __init__(self):
        self.mapModel = mapModel()
        self.currCell = None
        self.selected_cell = None

    # read in data and config widgets based on data
    def map_spinupDataSet(self, frames, mavFile):

        self.mapModel.read_mav(mavFile)                                
        self.mapModel.read_colorJson('colors.json')
        self.mapModel.initialize_respObjs()
        # self.mapModel.print_respObjs()
        cellCenters = self.mapModel.get_cellCenters()
        self.vorCells, boundCell = self.mapModel.create_cells(cellCenters, [])
        self.create_cellPatches(self.vorCells)
        self.config_widgets(frames)

    # creat cellPatches from voronoi polygons
    def create_cellPatches(self, vorCells):
        cellPatches = []
        for cell in vorCells:
            path = PolygonPath(cell.polygon)
            cellPatch = CellPatch(path, cell.get_cellNum(), picker=True)
            cellPatches.append(cellPatch)
        return cellPatches

    # config widgets based on data input
    def config_widgets(self, frames):
        for frame in frames:
            if isinstance(frame, MapParentFrame):
                self.config_mapPlot(frame)
                self.config_mapWidgets(frame.controlFrame)

    # config map widgets sliders/dropdowns
    def config_mapWidgets(self, frame):
        simIds = self.mapModel.get_simIdList()
        responses = self.mapModel.get_responseNames()
        timeRange, stepsPerDay = self.mapModel.get_timeParams()
        timeSliderRes = 1/stepsPerDay
        frame.config_timeSlider(resolution=timeSliderRes, from_=timeRange[0],
                                to=timeRange[1], digits=4)
        frame.config_respDrop(values=responses)
        frame.config_simIdDrop(values=simIds)
        frame.set_simIdDropIndex(simIds[0])
        frame.set_respDropIndex(responses[0])

    # config matplotlib fig/plot cellpatches
    def config_mapPlot(self, frame):
        cellCenters = self.mapModel.get_cellCenters()
        xrange, yrange = self.get_vorPlotLim(cellCenters)
        self.plot_cellPatches(frame)
        frame.set_plotLims(xrange, yrange)

    # update map based on control widget values
    def update_map(self, frame):
        if isinstance(frame, MapControlFrame):
            plotFrame = frame.get_master().get_mapFrame()

        responses=self.mapModel.get_responses()
        simIndex = frame.get_simIdDropIndex()
        timeRange, stepsPerDay = self.mapModel.get_timeParams()
        timeStep = frame.get_timeSliderVal()

        timeIndex = round(timeStep*stepsPerDay)
        response = frame.get_respDropIndex()

        numCells = len(self.vorCells)

        for cell in range(numCells):
            data = self.mapModel.get_dataBySimTimeCellResp(
                simIndex, timeIndex, cell+1, response)
            # generate color for a cell based on data
            color = responses[response].gen_color(data)
            # print("Color changed to", color)
            # update color on plot
            plotFrame.update_cellPatch(color, cell+1)
        plotFrame.draw_canvas()

    # create/update legend based on param values
    def update_legend(self, numThresh, frame):
        response = frame.get_respDropIndex()
        responses=self.mapModel.get_responses()
        respGroup=responses[response].get_respGroup()
        max=respGroup.get_max()
        patches = []
        for x in range(numThresh):
            colorThresh = max/(x+1)
            color = respGroup.gen_color(colorThresh)
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
                print("same cell")

    # if cell is selected highlight cell and write databox
    def cell_selected(self, frame, event):
        artist = event.artist
        if self.selected_cell is not None:
            self.selected_cell.set_linewidth(1.0)
        artist.set_linewidth(3.0)

        self.selected_cell = artist
        frame.set_currCell(artist.get_cellNum())

        if frame.get_dataFrame() is not None:
            self.write_cellData(frame, artist.get_cellNum())
        frame.draw_canvas()

    # write data box if cell is selected
    def write_cellData(self, frame, cell):

        responses = self.mapModel.get_responseNames()
        if isinstance(frame, MapPlotFrame):
            controlFrame = frame.get_controlFrame()

        simIndex = controlFrame.get_simIdDropIndex()
        timeRange, stepsPerDay = self.mapModel.get_timeParams()
        timeStep = controlFrame.get_timeSliderVal()

        timeIndex = round(timeStep*stepsPerDay)
        #response = controlFrame.get_respDropDownIndex()

        dataFrame = frame.get_dataFrame()
        dataFrame.clear()
        for index, response in enumerate(responses):
            data = self.mapModel.get_dataBySimTimeCellResp(
                simIndex, timeIndex, cell, index)
            dataLine = response+": "+str(data)+"\n"
            dataFrame.write_line(dataLine)
        dataFrame.view_currLine()
        dataFrame.write_selectedLabel("Selected Cell " + str(cell))

    def plot_cellPatches(self, frame):
        frame.plot_cellPatches(self.create_cellPatches(self.vorCells))

    def get_vorPlotLim(self, cellCenters):

        coordsInv = zip(*cellCenters)
        coordsInv = list(coordsInv)
        min_x = min(coordsInv[0])
        max_x = max(coordsInv[0])
        min_y = min(coordsInv[1])
        max_y = max(coordsInv[1])
        return [[min_x, max_x], [min_y, max_y]]
