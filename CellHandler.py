from helpers import get_vorPolys
from shapely.geometry import Polygon, Point
from Polymap import Cell
import colorsys


class CellHandler:

    def ___init__(self):

        self.respGroup = None

    # def create_cellPolys(self, vorCoords, boundCoords):

    #     polygons, boundPoly = get_vorPolys(vorCoords, boundCoords)
    #     polyList = list(polygons)
    #     vorCoords_list = [Point(coord[0], coord[1]) for coord in vorCoords]
    #     cells = []
    #     for poly in polyList:
    #         cells.append(Cell(poly))

    #     for i, poly in enumerate(polyList):

    #         for x, point in enumerate(vorCoords_list):

    #             if poly.contains(point):

    #                 cells[i].set_cell(x+1)
    #                 print("Setting",i,x+1)

    #     boundCell = Cell(boundPoly)
    #     return cells, boundCell

    

    


