# Map Viewer
# Model.py
# Model class to process data and handle voronoi tesselation and cell data
import colorsys
import math
import os
from fractions import Fraction

from shapely.geometry import Point, Polygon

from DataReader import Reader
from helpers import (
    get_area_wgs84,
    get_vorPolys,
    wgs84_toMercater_poly,
    wgs84_toMercator,
)
from Polymap import Cell
from Response import Response


class MapModel:
    def __init__(self):
        self.coords = None
        self.simList = None
        self.cellPatches = None

        self.reader = Reader()

    # start reader functions *********************************************************

    def read_mav(self, file):
        self.simList = self.reader.readMav_file(file)
        self.cellCenters = self.reader.get_cellCoords()
        self.timeSteps = self.reader.get_timesteps()
        self.pathCells = self.reader.get_pathCells()

    # start helper functions******************************************************

    def is_point_in_cell(self, x_coord, y_coord, cellNum):

        if cellNum is None or x_coord is None or y_coord is None:
            return False
        else:
            cell = self.cells[cellNum - 1]
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

    def create_cells(self):
        pathCells = self.get_pathCells()
        pathCells.reverse()
        cellCenters = self.get_cellCenters()
        vorCoords = list(cellCenters)
        for index in pathCells:
            del vorCoords[index - 1]

        cells = len(cellCenters) * [None]
        polygons, self.boundPoly = get_vorPolys(vorCoords, [])

        vorPolys = list(polygons)
        for index in range(len(pathCells)):
            cellIndex = pathCells[index] - 1
            dist = 2
            lat = float(cellCenters[cellIndex][1])
            lon = float(cellCenters[cellIndex][0])
            p1 = Point(lon - dist / 2, lat - dist / 2)
            p2 = Point(lon + dist / 2, lat - dist / 2)
            p3 = Point(lon + dist / 2, lat + dist / 2)
            p4 = Point(lon - dist / 2, lat + dist / 2)
            poly = Polygon([p1, p2, p3, p4])
            area = get_area_wgs84(poly)
            # mercPoly = wgs84_toMercater_poly(poly)
            cells[cellIndex] = Cell(poly)
            cells[cellIndex].type = "Path"
            cells[cellIndex].set_cell(cellIndex + 1)
            cells[cellIndex].area = area

        for index, cell in enumerate(cells):
            if cell is None:
                poly = vorPolys.pop(0)
                # mercPoly=wgs84_toMercater_poly(poly)
                area = get_area_wgs84(poly)
                cells[index] = Cell(poly)
                cells[index].type = "Grid"
                cells[index].set_cell(index + 1)
                cells[index].area = area
        self.cells = cells

    def find_normalizedMax(self, response):
        max = 0
        numCells = len(self.cells)
        timeSteps = len(self.timeSteps)
        for sim in self.simList:

            for cell in range(numCells):
                for time in range(timeSteps):
                    if sim.simGrid[time][cell] is None:
                        pass
                    else:
                        data = (
                            sim.simGrid[time][cell].dataLine[response]
                            / self.cells[cell].area
                        )
                    if data is not None:
                        if data > max:
                            max = data
        return max

    # end helper functions ********************************************************

    # start getter/setter methods *************************************************

    def get_timeSteps(self):

        return self.timeSteps

    def get_responseNames(self):
        return self.reader.get_responses()[0]

    def get_timeParams(self):
        timesteps = self.get_timeSteps()
        increment = float(timesteps[1]) - float(timesteps[0])
        increment_fraction = Fraction(increment)
        stepsPerday = increment_fraction.denominator

        rangeMin = min(timesteps)
        rangeMax = max(timesteps)
        range = [rangeMin, rangeMax]
        return range, stepsPerday

    def get_cellCenters(self):
        return self.cellCenters

    # def get_cellCenters_merc(self):
    # return self.convert_wgs84ToMercator(self.cellCenters)

    def get_simIdList(self):
        return self.reader.get_simIdList()

    # takes vornonoi coords and determines min size of plot

    def get_simList(self):
        return self.simList

    def get_indepVars(self):
        return self.reader.get_IndVars()

    def get_dataBySimTimeCellResp(self, simIndex, timeIndex, cell, response):
        return self.simList[simIndex].simGrid[timeIndex][cell - 1].dataLine[response]

    def getTpamByTimeSideTarget(self, fileName, simId, time, side, target):
        return self.reader.query_tpamforSlice(fileName, simId, time, side, target)

    def get_pathCells(self):
        return self.pathCells

    def get_vorCells(self):
        return self.cells


# end getter/setter methods *****************************************************
