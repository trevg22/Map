# Map Viewer
# Class to interface directly with model
# and impliment some view functionality
import colorsys
import json
import os
import time
import tkinter as tk
from colorsys import rgb_to_hls
from tkinter import font, ttk
from typing import List

import cartopy.crs as ccrs
from cartopy.feature import BORDERS, COASTLINE, LAND, NaturalEarthFeature
from descartes import PolygonPatch
from matplotlib.image import imread
from matplotlib.patches import Patch

import settings
from ColorFrame import ColorParentFrame
from DataReader import Reader, indepVar,simInst
from MapFrame import MapControlFrame, MapParentFrame, MapPlotFrame
from MapModel import MapModel
from Polymap import CellPatch, PolygonPath
from Response import Response
from typing import List


class Controller:

    def __init__(self, view):
        self.MapModel = MapModel()
        self.currCell = None
        self.selected_cell = None
        self.view = view

    # read in data and config widgets based on data
    def map_spinupDataSet(self, frames, mavFile):
        self.MapModel.read_mav(mavFile)
        self.MapModel.read_colorJson('colors.json')
        self.initialize_respObjs()
        self.MapModel.create_cells()
        vorCells = self.MapModel.get_vorCells()
        self.create_cellPatches(vorCells)
        self.config_widgets(frames)
        

    # creat cellPatches from voronoi polygons
    def create_cellPatches(self, vorCells):
        cellPatches = []
        for cell in vorCells:
            path = PolygonPath(cell.polygon)
            cellPatch = CellPatch(path, cell, picker=True, alpha=.3)
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

            elif isinstance(frame,MapControlFrame):
                self.config_mapWidgets(frame) 

    def config_colorWidgets(self, frame):
        responsesNames = self.MapModel.get_responseNames()
        responses = self.responses
        frame.config_respDrop(values=responsesNames)
        frame.set_respDropIndex(responsesNames[0])
        curResp: Response = responses[0]
        frame.update_entrys(curResp)
        print("configuring colors")

    # config map widgets sliders/dropdowns
    def config_mapWidgets(self, frame):
        resp_targs = self.MapModel.get_responseNames()
        timeRange, stepsPerDay = self.MapModel.get_timeParams()
        timeSliderRes = 1/stepsPerDay
        frame.config_timeSlider(resolution=timeSliderRes, from_=timeRange[0],
                                to=timeRange[1], digits=4)
        frame.config_timeSpin(increment=timeSliderRes,
                              from_=timeRange[0], to=timeRange[1], format="%5.2f", width=7)
        # configure dropdowns
        targNamelen=0
        respNameLen=0
        
        respNames=[]
        targNames=[]
        for string in resp_targs:
            underInd=string.rfind('_')
            respName=string[:underInd]
            targName=string[underInd+1:]
            if len(targName) > targNamelen:
                targNamelen=len(targName)

            if len(respName) >respNameLen:
                respNameLen=len(respName)
            if targName not in targNames:
                targNames.append(targName)
            if respName not in respNames:
                respNames.append(respName)
        frame.config_respDrop(values=respNames,width=respNameLen)
        frame.targDropDown.config(width=targNamelen)
        frame.set_respDropIndex(respNames[0]) 
        self.view.filter_drop(frame,None)
        availableTargs=frame.targDropDown.cget('values')
        frame.targDropDown.set(list(availableTargs)[0])

        # Config ind var dropdowns
        indVars:List[indepVar]=self.MapModel.get_indepVars()
        print("there are",len(indVars),"indep vars")
        for var in indVars:
            drop=ttk.Combobox(frame)
            maxWidth=0
            for label in var.labels:
                if len(label) > maxWidth:
                    maxWidth=len(label)
            drop.config(values=var.labels,width=maxWidth)
            drop.set(var.labels[0])
            drop.bind("<<ComboboxSelected>>", lambda event: self.view.map_simIdDropdownChanged(frame, event))
            frame.simIdDrops.append(drop)
            frame.simIdLabels.append(var.name)
            print("children packed")
        frame.pack_children()
        frame.grid(row=0,column=0)

    # config matplotlib fig/plot cellpatches
    def config_mapPlot(self, frame):
        plotFrame = frame.get_plotFrame()
        cwd = os.getcwd()
        background = "natural-earth.png"
        backPath = os.path.join(cwd, background)
        if os.path.exists(backPath):
            plotFrame.ax.imshow(imread(backPath), origin='upper', transform=ccrs.PlateCarree(),
                                extent=[-180, 180, -90, 90])
        cellCenters = self.MapModel.get_cellCenters()
        xrange, yrange = self.get_vorPlotLim(cellCenters)
        self.plot_cellPatches(frame)
        frame.set_plotLims(xrange, yrange)
        states_provinces = NaturalEarthFeature(
            category='cultural',
            name='admin_1_states_provinces_lines',
            scale='50m',
            facecolor='none')

        plotFrame.ax.add_feature(LAND)
        plotFrame.ax.add_feature(COASTLINE)
        plotFrame.ax.add_feature(BORDERS)
        plotFrame.ax.add_feature(
            states_provinces, edgecolor='gray', facecolor='none')
        print("x range", xrange)
        print("y range", yrange)

    # update map based on control widget values

    def update_map(self, frame):

        if isinstance(frame, MapControlFrame):
            plotFrame:MapPlotFrame = frame.get_master().get_plotFrame()
            controlFrame:MapControlFrame=frame

        elif isinstance(frame,MapParentFrame):
            plotFrame:MapPlotFrame=frame.get_plotFrame()
            controlFrame:MapControlFrame=frame.get_controlFrame() 

        plotFrame.reset_patchAlphas(.3)

        vorCells = self.MapModel.get_vorCells()
        numCells = len(vorCells)
        responses = self.responses
        simIndex = self.find_currSimIndex(controlFrame) 
        print("sim Index is",simIndex)
        timeRange, stepsPerDay = self.MapModel.get_timeParams()
        timeStep = controlFrame.get_timeSliderVal()
        densityOn = controlFrame.get_densityToggle()
        timeIndex = round(timeStep*stepsPerDay)

        resp_targ=controlFrame.get_currResp_targ()
        resp_targs=self.MapModel.get_responseNames()
        
        responseIndex = resp_targs.index(resp_targ) 

        if densityOn:
            densityMax = self.MapModel.find_normalizedMax(responseIndex)

        for cell in range(numCells):
            data = self.MapModel.get_dataBySimTimeCellResp(
                simIndex, timeIndex, cell+1, responseIndex)
            if densityOn:
                area = vorCells[cell].area
                color = responses[responseIndex].gen_colorNorm(
                    data, densityMax, area)
            else:
                color = responses[responseIndex].gen_color(data)
            # update color on plot
            plotFrame.update_cellPatchColor(color, cell+1)
            if color != [1, 1, 1]:
                plotFrame.update_cellPatchAlpha(1, cell+1)
            else:
                pass
                # print("color is white in cell",cell)

        plotFrame.draw_canvas()

    # create/update legend based on param values
    def update_legend(self, numThresh, frame):
        if isinstance(frame,MapParentFrame):
            controlFrame:MapControlFrame=frame.get_controlFrame()
            plotFrame:MapPlotFrame=frame.get_plotFrame()

        elif isinstance(frame,MapControlFrame):
            controlFrame:MapControlFrame=frame
            plotFrame:MapPlotFrame=controlFrame.get_plotFrame()

        resp_targ=controlFrame.get_currResp_targ()
        resp_targs=self.MapModel.get_responseNames()
        responseIndex = resp_targs.index(resp_targ)
        responses = self.responses
        response = responses[responseIndex]
        max1 = response.max
        min1 = response.min
        lowThresh = .0001
        patches = []
        smallVal = max1*lowThresh

        lowLabel = '>' + "{:.2e}".format(smallVal)
        patches.append(Patch(facecolor=[1, 1, 0], label=lowLabel))
        for x in range(numThresh):
            colorThresh = ((x+1)*(max1-min1)/(numThresh))+min1
            color = response.gen_color(colorThresh)
            dataThresh = str("{:.2f}".format(colorThresh))
            patches.append(Patch(facecolor=color, label=dataThresh))

        location=plotFrame.legendLoc
        print("location",location)
        if location == 'none':
           plotFrame.ax.legend().set_visible(False)
        else:
            plotFrame.ax.legend(handles=patches,loc=location)
        plotFrame.draw_canvas()

    # generate a color based on linear scaled
    # hue currently hard coded

    def find_currSimIndex(self,frame:MapControlFrame):
        simId=frame.get_simId()
        simList:List[simInst]=self.MapModel.get_simList()

        for index,sim in enumerate(simList):
            print("comparing",sim.simPrefix,"with",simId)
            simPrefix=''.join([str(x) for x in sim.simPrefix]) 
            if simPrefix==simId:
                print("sim found index",index)
                return index

    # detect if the mouse has changed cell

    def mapDetect_cellChange(self, frame, event):
        if event.inaxes == frame.get_axes():
            # Check if mouse in is currCell
            mouse_in_cell = self.MapModel.is_point_in_cell(
                event.xdata, event.ydata, self.currCell)
            # print("Mouse in Cell", mouse_in_cell)
            if mouse_in_cell == False:
                # find what cell mouse is in
                self.currCell, found = self.MapModel.determine_cell_from_point(
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

        controlFrame: MapControlFrame = frame.get_controlFrame()

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

        responses = self.MapModel.get_responseNames()
        if isinstance(frame, MapPlotFrame):
            controlFrame = frame.get_controlFrame()
        currResponse = controlFrame.get_respDropIndex()
        dataFrame = frame.get_dataFrame()
        textwidget = dataFrame.textBox
        bFont = font.Font(textwidget, textwidget.cget("font"))
        bFont.config(weight="bold")
        nFont = font.Font(textwidget, textwidget.cget("font"))
        textwidget.tag_configure("bold", font=bFont)
        simIndex = self.find_currSimIndex(controlFrame)
        timeRange, stepsPerDay = self.MapModel.get_timeParams()
        timeStep = controlFrame.get_timeSliderVal()

        timeIndex = round(timeStep*stepsPerDay)
        #response = controlFrame.get_respDropDownIndex()
        vorCells = self.MapModel.get_vorCells()
        densityOn = controlFrame.get_densityToggle()
        scaleFac = controlFrame.get_densityScaleFac()
        cellNum = cell.get_cellNum()
        dataFrame.clear()
        for index, response in enumerate(responses):
            data = self.MapModel.get_dataBySimTimeCellResp(
                simIndex, timeIndex, cellNum, index)
            if densityOn:
                area = vorCells[cellNum-1].area
                data = (data*scaleFac)/area
            dataLine = response+": "+"{0:.2f}".format(data)+"\n"
            # if index==currResponse:
            #     print("should be bold")
            #     textwidget.config(font=bFont)
            # else:
            #     textwidget.config(font=nFont)
            textwidget.insert(tk.END, dataLine)
        dataFrame.view_currLine()
        dataFrame.write_selectedLabel(cell)

    def initialize_respObjs(self):
        default_hue = 185
        responsesNames = self.get_reponseNames()
        simList = self.MapModel.get_simList()
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
        plotFrame = virtFrame.get_plotFrame()
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
            simIndex = int(snap["simIndex"])
            response = str(snap["response"])
            times = snap["times"]
            hue = snap["hue"]
            if "zoom" in snap:
                zoom = snap["zoom"]
                plotFrame.ax.set_ylim(zoom[1][0], zoom[1][1])
                plotFrame.ax.set_xlim(zoom[0][0], zoom[0][1])

            if "legendLoc" in snap:
                plotFrame.legendLoc=str(snap["legendLoc"])
            controlFrame.set_runDropIndex(simIndex)
            respIndex = responseNames.index(response)
            controlFrame.set_respDropIndex(responseNames[respIndex])
            currResp = self.responses[respIndex]
            prevHue = currResp.hue
            currResp.hue = hue

            for time in times:
                self.update_legend(settings.numLegendEntries, controlFrame)
                controlFrame.timeSlider.set(time)
                self.update_map(controlFrame)
                imgName = os.path.join(snapPath, str(
                    name)+"_"+str(simIndex)+"_"+str(response)+"_"+str(time)+".png")
                plotFrame.fig.savefig(imgName, bbox_inches='tight')

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
