# Map Viewer
# Polymap.py
# Contains classes to assist with plotting
# polygon objects
import colorsys

import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.path import Path
from numpy import asarray, concatenate, ones
from shapely.geometry import Point, Polygon

# function to take a "Shapely" polygon and convert to matplotlib patch


def PolygonPath(polygon):
    """Constructs a compound matplotlib path from a Shapely or GeoJSON-like
    geometric object"""
    this = Polygon(polygon)
    assert this.geom_type == "Polygon"

    def coding(ob):
        # The codes will be all "LINETO" commands, except for "MOVETO"s at the
        # beginning of each subpath
        n = len(getattr(ob, "coords", None) or ob)
        vals = ones(n, dtype=Path.code_type) * Path.LINETO
        vals[0] = Path.MOVETO
        return vals

    vertices = concatenate(
        [asarray(this.exterior)[:, :2]] + [asarray(r)[:, :2] for r in this.interiors]
    )
    codes = concatenate([coding(this.exterior)] + [coding(r) for r in this.interiors])
    return Path(vertices, codes)


# inherited Patch class to hold cell number and polygon information
class CellPatch(Patch):
    """
    A general polycurve path patch.
    """

    _edge_default = True

    def __str__(self):
        s = "PathPatch%d((%g, %g) ...)"
        return s % (len(self._path.vertices), *tuple(self._path.vertices[0]))

    def __init__(self, path, cell, **kwargs):
        """
        *path* is a :class:`matplotlib.path.Path` object.

        Valid kwargs are:
        %(Patch)s
        """
        Patch.__init__(self, **kwargs)
        self._path = path
        self.cell = cell

    def get_path(self):
        return self._path

    def get_cellNum(self):
        return self.cell.get_cellNum()

    def get_cellArea(self):
        return self.cell.get_cellArea()

    def get_cellType(self):
        return self.cell.type


# non matplotlib cell object used in model


class Cell:
    def __init__(self, inc_poly):
        self.cell = None
        self.alpha = None
        self.polygon = inc_poly
        self.type = None
        self.area = None
        self.neighbors=[]

    def set_alpha(self, inc_alpha):
        self.alpha = inc_alpha

    def set_cell(self, cell_num):
        self.cell = cell_num

    def get_cellNum(self):
        return int(self.cell)

    def get_polygon(self):
        return self.polygon

    def get_cellArea(self):
        return self.area
