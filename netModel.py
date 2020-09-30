# Impact Map Tool
# netModel.py
# Class to handle all network tool logic

from scipy.spatial import Voronoi
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, LineString,MultiLineString,Point,MultiPoint
from shapely.geometry.polygon import orient
from shapely.ops import polygonize
import numpy as np
import random
from matplotlib.collections import LineCollection
from descartes import PolygonPatch
from helpers import get_vorPolys
class NetModel:
    
    def __init__(self):
        self.vorPoints=[]
        self.boundPoints=[]
        self.fig=plt.Figure()
        self.ax=self.fig.add_subplot(111)
        self.ax.set_ylim(-10,10)
        self.ax.set_xlim(-10,10)
        # Start geometry functions *********************************************
    
# End geometry functions *************************************************

# Start event driven methods *********************************************
    def create_network_hardcoded(self):
        
        npVorPoints=np.array(self.vorPoints)
        npBoundPoints=np.array(self.boundPoints)
        npVorPoints=np.array([[3.41,5.123],[2.34353,0],[-1,1],[-3,3]]) 
        vor=Voronoi(npVorPoints)
        min_x = vor.min_bound[0] - 0.1
        max_x = vor.max_bound[0] + 0.1
        min_y = vor.min_bound[1] - 0.1
        max_y = vor.max_bound[1] + 0.1
        npBoundPoints = [[min_x-3, min_y], [min_x-3, max_y+1], [max_x+1, max_y+1], [max_x+2, min_y-1],[-3.5,-3.5]]


        polygons,boundPoly=get_vorPolys(npVorPoints,npBoundPoints)
        self.ax.add_patch(PolygonPatch(boundPoly))
        for poly in polygons:
            print("Polygon")
            print(poly)
            self.ax.add_patch(PolygonPatch(poly,facecolor=self.random_color()))
        print("network created")

    def create_network(self):
        
        npVorPoints=np.array(self.vorPoints)
        npBoundPoints=np.array(self.boundPoints)
        print("Boundary: ",npBoundPoints)
        print("Voronoi: ",npVorPoints)

        codedPoints=np.array([[1,1],[1,0],[-1,1],[-3,3]]) 
        print(codedPoints)
        vor=Voronoi(npVorPoints)
        min_x = vor.min_bound[0] - 0.1
        max_x = vor.max_bound[0] + 0.1
        min_y = vor.min_bound[1] - 0.1
        max_y = vor.max_bound[1] + 0.1

        polygons,boundPoly=get_vorPolys(npVorPoints,npBoundPoints)
        self.ax.add_patch(PolygonPatch(boundPoly))
        for poly in polygons:
            print("Polygon")
            print(poly)
            self.ax.add_patch(PolygonPatch(poly,facecolor=self.random_color()))
        
# End event driven methods
# Start helper functions *********************************************
    def random_color(self,as_str=False, alpha=0.5):
        rgb = [random.randint(0,255),
        random.randint(0,255),
        random.randint(0,255)]
        if as_str:
            return "rgba"+str(tuple(rgb+[alpha]))
        else:
        # Normalize & listify
            return list(np.array(rgb)/255) + [alpha]
       
    def plot_network(self,finite,infinite):
        pass
    def append_points(self,x,y,pointType):

        if pointType=='Voronoi':
            self.vorPoints.append([x, y])
        elif pointType=='Boundary':
            self.boundPoints.append([x, y])
            
# End helper functions **********************************************

# Start getter/setter functions ******************************************

# End getter/setter methods *********************************************

    def get_fig_ax(self):
        return self.fig,self.ax



