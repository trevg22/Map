from helpers import get_vorPolys
from shapely.geometry import Polygon, Point
from Polymap import Cell
import colorsys


class CellHandler:

    def ___init__(self):

        self.respGroup = None

    def create_cellPolys(self, vorCoords, boundCoords):

        polygons, boundPoly = get_vorPolys(vorCoords, boundCoords)
        polyList = list(polygons)
        vorCoords_list = [Point(coord[0], coord[1]) for coord in vorCoords]
        cells = []
        for poly in polyList:
            cells.append(Cell(poly))

        for i, poly in enumerate(polyList):

            for x, point in enumerate(vorCoords_list):

                if poly.contains(point):

                    cells[i].set_cell(x+1)

        boundCell = Cell(boundPoly)
        return cells, boundCell

    def update_cellPatches(self, currSim, timeIndex):

        # print("TimeStep",timeStep)
        # print("StepsPerDay",stepsPerday)
        #print("sim Grid len ", len(currSim.simGrid))
        for i, patch in enumerate(self.cells):
            if currSim.simGrid[timeIndex][patch.cell] is not None:
                patch.data = currSim.simGrid[timeIndex][patch.cell].dataLine
                #print(patch.data," cell ", patch.cell," index ",i)
            else:
                #print("simGrid at ",int(timeStep)*stepsPerday, " ",patch.cell,"is NoneType")
                pass

    def colorize_cellPatches(self, currResponse):
        max = self.max
        # Hue value from HSL color standard(0-360 degrees)
        hue = 197
        hueFrac = hue/360
        sat = 1  # represents 100 percent
        threshold = .90  # maximum light value to avoid moving to black

        for i, patch in enumerate(self.cellPatches):
            #print("Patch data for cell num",patch.cell," ", patch.data)
            if max > 0 and patch.data[currResponse] is not None:
                respdata = float(patch.data[currResponse])
                lightness = (1-(respdata/max)*threshold)
                color = colorsys.hls_to_rgb(hueFrac, lightness, sat)
                patch.polygonPatch.set_facecolor(color)
            else:
                color = [0, 0, 0]
