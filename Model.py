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

class Model:
    def __init__(self):
        self.mavReader=None
        self.coords=None
        self.simList=None
        self.cellPatches=None
        self.fig=plt.Figure()
        self.ax=self.fig.add_subplot(111)
        self.debugcount=0
        self.num_cells=60
# start reader functions *********************************************************
    def read_coords(self,file):
        self.coords=self.mavReader.readCoordJson(file)

    def read_mav(self,file):
        self.simList=self.mavReader.readMav_file(file)
    def read_mav_coords(self,mavFile,coordFile):
        
        self.mavReader=Reader()
        self.read_mav(mavFile)
        self.read_coords(coordFile)

# start cellpatch/polygon functions********************************************
    def create_cellPatches(self):
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

    def update_cellPatches(self,simId,timeStep):
        
        currSim=self.simList[0]
        range,stepsPerday=self.get_timeParams()

        for i,patch in enumerate(self.cellPatches):
            if currSim.simGrid[int(timeStep)*stepsPerday][patch.cell] is not None:
                patch.data=currSim.simGrid[int(timeStep)*stepsPerday][patch.cell].dataLine
                print(patch.data," cell ", patch.cell," index ",i)
            else:
                print("simGrid at ",int(timeStep)*stepsPerday, " ",patch.cell,"is NoneType")
        
    
    def colorize_cellPatches(self,currResponse):
        max=self.max
        #Hue value from HSL color standard(0-360 degrees)
        hue=197
        hueFrac=197/360
        sat=1 # represents 100 percent
        threshold = .90 #maximum light value to avoid moving to black

        for i, patch in enumerate(self.cellPatches):
            respdata=float(patch.data[currResponse])
            lightness=(1-(respdata/max)*threshold)
            color=colorsys.hls_to_rgb(hueFrac,lightness,sat)

            patch.polygonPatch.set_facecolor(color) 
        
 
   



    # def colorize_cellPatches(self,currResponse):
        
    #     # print(len(self.cellPatches))
    #     max=self.max
           
    #     alpha=.8
    #     threshold1=max/3
    #     threshold2=threshold1*2
    #     delta=max/3
    #     for i, patch in enumerate(self.cellPatches):
    #         respdata=float(patch.data[currResponse])
    #         # print("data", respdata)
    #         if(respdata>0 and respdata<threshold1):
    #             relativeColor=respdata
    #             alpha=relativeColor/delta
    #             color=(0,0,1,alpha)
            
    #         elif(respdata>threshold1 and respdata<threshold2):
    #             relativeColor=respdata-threshold1
    #             alpha=relativeColor/delta
    #             color=(0,1,0,alpha) 

    #         elif(respdata>threshold2 and respdata <=max):
    #             relativeColor=respdata-threshold2
    #             alpha=relativeColor/delta
    #             color=(1,0,0,alpha)


    #         elif respdata==0:
    #             color=(0,0,0,0)

    #         else:
    #             color=(0,0,0,0)
    #             print("color is not in thresholds")            
    #         patch.polygonPatch.set_facecolor(color) 
        
 
   

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
        currSim=self.simList[0]
        max=0

        for time in range(len(currSim.simGrid)):
            for cell in range(len(currSim.simGrid[time])):
            
                value=currSim.simGrid[time][cell].dataLine[currResponse]

                if value>max:
                    max=value
        self.max = max

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
#end getter/setter methods *****************************************************
