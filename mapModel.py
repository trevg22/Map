# Impact Map viewer 
# Model.py
# Model class to process data and handle voronoi tesselation and cell data
import matplotlib.pyplot as plt
from data_reader import Reader
from Polymap import cellPatch
from shapely.ops import polygonize
from scipy.spatial import Voronoi
from descartes import PolygonPatch
import shapely
from matplotlib.patches import Patch
from shapely.geometry import Point
from fractions import Fraction
import colorsys
from helpers import get_vorPolys


class mapModel:
    def __init__(self):
        self.mavReader=None
        self.coords=None
        self.simList=None
        self.cellPatches=None
        self.fig=plt.Figure()
        self.ax=self.fig.add_subplot(111)
        self.debugcount=0
        self.num_cells=60
        self.currSim=None
# start reader functions *********************************************************
    def read_coords(self,file):
        #self.coords=self.mavReader.readCoordJson(file)
        self.coords=self.mavReader.get_cellCoords()

    def read_mav(self,file):
        self.simList=self.mavReader.readMav_file(file)
    def read_mav_coords(self,mavFile,coordFile):
        
        self.mavReader=Reader()
        self.read_mav(mavFile)
        self.read_coords(coordFile)

# start cellpatch/polygon functions********************************************
    def create_cellPatches(self):

        self.vorCoords=[[coord[1],coord[0]] for coord in self.coords]
        
        polygons,boundPoly=get_vorPolys(self.vorCoords,[])
        polyList = list(polygons)
        vorCoords_list=[Point(coord[0],coord[1]) for coord in self.vorCoords]
        cellPatches = []
        
        for poly in polyList:
            cellPatches.append(cellPatch(PolygonPatch(poly,fc='white'),poly))
            print(poly)

        for i, poly in enumerate(polyList):

            for x, point in enumerate(vorCoords_list):

                if poly.contains(point):

                    cellPatches[i].set_cell(x)
                
        self.cellPatches= cellPatches        

    def create_cellPatches_old(self):
        num_cells=60
        vor = Voronoi(self.coords)
        finiteSegments = [
            shapely.geometry.LineString(vor.vertices[line])
            for line in vor.ridge_vertices
            if -1 not in line
        ]
        polygons = polygonize(finiteSegments)
        polyList = list(polygons)
        coord_pointList=[Point(coord[0],coord[1]) for coord in self.coords]
        cellPatches = []
        
        for poly in polyList:
            cellPatches.append(cellPatch(PolygonPatch(poly,fc='white'),poly))

        for i, poly in enumerate(polyList):

            for x, point in enumerate(coord_pointList):

                if poly.contains(point):

                    cellPatches[i].set_cell(x)
                
        self.cellPatches= cellPatches        

    def update_cellPatches(self,timeStep):
        currSim=self.currSim
    
        range,stepsPerday=self.get_timeParams()
        self.stepsPerday=stepsPerday
        #print("TimeStep",timeStep)
        #print("StepsPerDay",stepsPerday)
        #print("sim Grid len ", len(currSim.simGrid))
        for i,patch in enumerate(self.cellPatches):
            if currSim.simGrid[round(timeStep*stepsPerday)][patch.cell] is not None:
                patch.data=currSim.simGrid[round(timeStep*stepsPerday)][patch.cell].dataLine
                #print(patch.data," cell ", patch.cell," index ",i)
            else:
                #print("simGrid at ",int(timeStep)*stepsPerday, " ",patch.cell,"is NoneType")
                pass
        
    
    def colorize_cellPatches(self,currResponse):
        max=self.max
        #Hue value from HSL color standard(0-360 degrees)
        hue=197
        hueFrac=hue/360
        sat=1 # represents 100 percent
        threshold = .90 #maximum light value to avoid moving to black

        for i, patch in enumerate(self.cellPatches):
            #print("Patch data for cell num",patch.cell," ", patch.data)
            if max>0 and patch.data[currResponse] is not None:
                respdata=float(patch.data[currResponse])
                lightness=(1-(respdata/max)*threshold)
                color=colorsys.hls_to_rgb(hueFrac,lightness,sat)
                patch.polygonPatch.set_facecolor(color) 
            else:
                color=[0,0,0]
        #print("colorized!")    

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
    def is_point_in_cell(self,x_coord,y_coord,cellPatch):
            
            if cellPatch is None:
                return False
            elif cellPatch.polygon.contains(Point(x_coord,y_coord)):
                return True
            else: 
                return False


    def determine_cell_from_point(self,x_coord,y_coord):
        found =False
        currPatch=None
        for patch in self.cellPatches:
            if patch.polygon.contains(Point(x_coord,y_coord)):
                currPatch=patch
                found=True
        
        
        return currPatch,found

    def find_max(self,currResponse):
        print("find max called")
        currSim=self.simList[0]
        max=0

        for time in range(len(currSim.simGrid)):
            for cell in range(len(currSim.simGrid[time])):
            
                #print("time ",time," cell ",cell)
                
                value=currSim.simGrid[time][cell].dataLine[currResponse]

                if value>max:
                    max=value
        self.max = max

    def print_SimInst(self,timeSteps,startCell,endCell):
        currSim=self.simList[0]

        for time in timeSteps:
            print("time: ", time)
            for i in range(endCell-startCell):
                value=currSim.simGrid[round(time*self.stepsPerday)][startCell+i].dataLine
                print("cell ", startCell+i," ", value)

# end helper functions ********************************************************

# start getter/setter methods *************************************************
    def get_fig_ax(self):
        return self.fig,self.ax

    def get_simDataSet(self,simId):
        return self.mavReader.get_simInst(simId)

    def get_timeSteps(self):
        return self.mavReader.get_timesteps()
    
    def get_responses(self):
        return self.mavReader.get_responses()

    def get_timeParams(self):
        timesteps=self.get_timeSteps()
        increment=float(timesteps[1])-float(timesteps[0])
        increment_fraction=Fraction(increment)
        stepsPerday=increment_fraction.denominator
        
        rangeMin=min(timesteps)
        rangeMax=max(timesteps) 
        range=[rangeMin,rangeMax]
        return range,stepsPerday

    def get_simIdList(self):
        return self.mavReader.get_simIdList()

    def set_currSim(self,index):
        self.currSim=self.simList[index]
        print("setting sim to ", index)
    def get_vorPlotLim(self):
        
        coordsInv=zip(*self.vorCoords)
        coordsInv=list(coordsInv)
        print(*coordsInv)
        min_x=min(coordsInv[0])
        max_x=max(coordsInv[0])
        min_y=min(coordsInv[1])
        max_y=max(coordsInv[1])
        return [[min_x,max_x],[min_y,max_y]]
#end getter/setter methods *****************************************************
