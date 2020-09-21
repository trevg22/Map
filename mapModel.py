# Map Viewer
# Model.py
# Model class to process data and handle voronoi tesselation and cell data
import colorsys
import os
from fractions import Fraction

import matplotlib.pyplot as plt
import shapely
from shapely.geometry import Point
from shapely.ops import polygonize

from CellHandler import CellHandler
from data_reader import Reader
from helpers import get_vorPolys
from Response import Response


class mapModel:
    def __init__(self):
        self.coords = None
        self.simList = None
        self.cellPatches = None
        self.debugcount = 0
        self.currSim = None
        self.cellhandler = CellHandler()
        self.reader = Reader()
# start reader functions *********************************************************

    def read_mav(self, file):
        self.simList = self.reader.readMav_file(file)
        self.cellCenters = self.reader.get_cellCoords()
        self.timeSteps = self.reader.get_timesteps()

# start cellpatch/polygon functions********************************************
    def create_cells(self, vorCoords, boundCoords):
        self.cells, boundCell = self.cellhandler.create_cellPolys(
            vorCoords, boundCoords)

        return self.cells, boundCell

# end cellpatch/polygon functions**********************************************

# start plotting funcionts ******************************************************
    def plot_mapBackground(self):
        pass

    def plot_cellPatches(self):
        for patch in self.cellPatches:
            self.ax.add_patch(patch.polygonPatch)

    def create_legend(self):
        pass
# end plotting functions *******************************************************

# start helper functions******************************************************
    def is_point_in_cell(self, x_coord, y_coord, cellNum):

        if cellNum is None or x_coord is None or y_coord is None:
            return False
        else:
            cell = self.cells[cellNum-1]
            if cell.polygon.contains(Point(x_coord, y_coord)):
                return True
            else:
                return False

    def determine_cell_from_point(self, x_coord, y_coord):
        found = False
        for cell in self.cells:
            if cell.get_polygon().contains(Point(x_coord, y_coord)):
                currCell = cell.get_cellNum()
                found = True

        if not found:
            currCell = 0
        return currCell, found

    def print_SimInst(self, timeSteps, startCell, endCell):

        for time in timeSteps:
            print("time: ", time)
            for i in range(endCell-startCell):
                value = self.currSim.simGrid[round(
                    time*self.stepsPerday)][startCell+i].dataLine
                print("cell ", startCell+i, " ", value)

    def initialize_respObjs(self):
        responses = []
        responsesNames = self.get_responseNames()
        self.respGroups = self.mavReader.get_respGroups()
        for x, name in enumerate(responsesNames):
            responses.append(response())
            responses[x].set_name(name)

            for group in self.respGroups:
                if name in self.respGroups[group].responses:
                    responses[x].set_respGroup(self.respGroups[group])
                    self.respGroups[group].append_responseIndex(x)
                    print(name, "is in", group)

    def print_respObjs(self):
        responses = self.get_responseNames()
        print("response groups")
        for group in self.respGroups:
            respNames = [responses[x] for x in group.append_responseIndexes]
            print("names:", respNames)

            print("group: ", group.group)
            print("hue: ", group.hue)

        os.system("pause")

    def find_respMax(self, response):
        max = 0
        numCells = len(self.cellCenters)
        timeSteps = len(self.timeSteps)

        for sim in self.simList:

            for cell in range(numCells):
                for time in range(timeSteps):
                    if sim.simGrid[time][cell] is None:
                        print("simGrid", "time", time, "Cell", cell, "is None")
                    else:
                        data = sim.simGrid[time][cell].dataLine[response]
                    if data is not None:
                        if data > max:
                            max = data
        return max

# end helper functions ********************************************************

# start getter/setter methods *************************************************

    def set_simInst(self, simInst):
        self.simInst = simInst

    def get_timeSteps(self):

        return self.timeSteps

    def get_responseNames(self):
        return self.reader.get_responses()[0]

    def get_timeParams(self):
        timesteps = self.get_timeSteps()
        increment = float(timesteps[1])-float(timesteps[0])
        increment_fraction = Fraction(increment)
        stepsPerday = increment_fraction.denominator

        rangeMin = min(timesteps)
        rangeMax = max(timesteps)
        range = [rangeMin, rangeMax]
        return range, stepsPerday

    def get_cellCenters(self):
        return self.cellCenters

    def get_simIdList(self):
        return self.reader.get_simIdList()

    def set_currSim(self, simId):
        for sim in self.simList:
            print(sim)
        for sim in self.simList:
            if sim.simPrefix == simId:
                self.currSim = sim
                print("setting sim to ", simId)
                break

    # takes vornonoi coords and determines min size of plot
    def get_vorPlotLim(self):

        coordsInv = zip(*self.vorCoords)
        coordsInv = list(coordsInv)
        print(*coordsInv)
        min_x = min(coordsInv[0])
        max_x = max(coordsInv[0])
        min_y = min(coordsInv[1])
        max_y = max(coordsInv[1])
        return [[min_x, max_x], [min_y, max_y]]

    def get_indepVars(self):
        return self.reader.get_IndVars()

    def get_dataBySimTimeCellResp(self, simIndex, timeIndex, cell, response):
        return self.simList[simIndex].simGrid[timeIndex][cell-1].dataLine[response]
# end getter/setter methods *****************************************************
