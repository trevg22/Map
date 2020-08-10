import json
import numpy as np
# from collections import namedtuple
# Stores list of responses at specific cell and time


class dataBy_cell_time():

    def __init__(self, inc_dataLine, inc_cell, inc_time):
        self.dataLine = inc_dataLine
        self.cell = inc_cell
        self.time = inc_time

# namedtuple('dataBy_cell_time', 'dataLine cell time')
# Stores a grid of dataBy_cell_time that is timesteps x numCells


class simInst():

    def __init__(self, inc_simPrefix, inc_numCells, inc_timesteps):

        self.numCells = inc_numCells
        self.timeSteps = inc_timesteps
        self.simPrefix = inc_simPrefix
        self.simGrid = [None] * len(self.timeSteps)
        self.responses=None
    def processSimvars(self, simvars):
        pass
    # Adds dataBy_cell_time instance to correct location in grid

    # def addElement(self, dataLine, cell, time):
    #     cell = int(cell)
    #     if self.simGrid[cell] is None:
    #         timeArr = [None] * len(self.timeSteps)
    #         self.simGrid[cell] = timeArr

    #     timeIndex = self.timeSteps.index(time)
    #     self.simGrid[cell][timeIndex] = dataBy_cell_time(dataLine, cell, time)

    
    def addElement(self, dataLine, cell, time,numCells):
        cell =int(cell)
        timeIndex = self.timeSteps.index(time)
        if self.simGrid[timeIndex] is None:
            cellArr=[None]*numCells
            self.simGrid[timeIndex]=cellArr
        self.simGrid[timeIndex][cell] = dataBy_cell_time(dataLine, cell, time)

        if isinstance(dataLine,int):
            print("blah")
    def set_simPrefix(self, inc_simPrefix):
        self.simPrefix = inc_simPrefix
    
    def set_responses(self,responses):
        self.responses=responses

    def get_simPrefix(self):
        return self.simPrefix
# Poplulats list of simInst objects from JSON


class Reader:

    def readCoordJson(self,file):
        with open(file, 'r') as f:
            data = json.load(f)
            coords = np.array(list(data.values()), dtype=np.float32)

        for x in range(len(coords)):
            temp = coords[x][0]
            coords[x][0] = coords[x][1]
            coords[x][1] = temp
            return coords

    def readMav_file(self, file):
        with open(file, 'r') as f:
            data = json.load(f)

        self.simList = []
        self.timeSteps = data["map-viewer"]["variables"]["Time"]
        self.coords=data["map-viewer"]["variables"]["Cells"]
        self.numCells=len(self.coords)
        print(self.coords)
        numVars=len(data["map-viewer"]["variables"]) -2 # subtract 1 because time,cells is not part of "sim id"
#        numResponses = len(data["impact-viewer"]["groups"])
        self.responses = list(data["map-viewer"]["groups"].values())
        print("mav ran")
        # print(self.responses)
        prevSim = None
        startIndex=numVars+2
        for dataLine in data["map-viewer"]["values"]:
            
            simPrefix=''
            count = 0
            found = False
            for x in range(numVars):
                simPrefix+=str(dataLine[x])
            # Create new simInst if none exist
            if len(self.simList) == 0:
                
                self.simList.append(simInst(simPrefix, self.numCells, self.timeSteps))
                prevSim = self.simList[0]
                self.simList[0].set_responses(self.responses)
                prevSim.addElement(
                        dataLine[startIndex:], dataLine[numVars + 1], dataLine[numVars],self.numCells) 
                prevSim.set_simPrefix(simPrefix)
            else:
                # if Incoming data belongs to same sim as previous data,
                # no need to loop
                if simPrefix == prevSim.simPrefix:
                    prevSim.addElement(
                        dataLine[startIndex:], dataLine[numVars + 1], dataLine[numVars],self.numCells)

                else:
                    # Locate simInst data belongs to, short circuit with found
                    while count < len(self.simList) and found is False:
                        if self.simList[count].simPrefix == simPrefix:
                            # this addElement will pass in dataLine as an int not a list
                            self.simList[count].addElement(
                                dataLine[startIndex:], dataLine[numVars + 1], dataLine[numVars],self.numCells)
                            prevSim = self.simList[count]
                            found = True
                        count = count + 1

                    if found is False:
                        self.simList.append(
                            simInst(simPrefix, self.numCells, self.timeSteps))
                        found = True
        
        self.print_SimInst(self.simList)
        return self.simList

    
    def print_SimInst(self,simList):
        print("simulations")

        for sim in simList:
            print(sim.simPrefix)
        
    def get_timesteps(self):
        return self.timeSteps
        

    def get_responses(self):
        return self.responses

    def get_simList(self):
        return self.simList
    
    def get_simInst(self,simId):
        return self.simList[simId]
        
    def get_simIdList(self):
       simIds=[]
       for sim in self.simList:
           simIds.append(sim.get_simPrefix())
           print(sim.get_simPrefix()) 
       return simIds
    def get_cellCoords(self):
       return self.coords
    

