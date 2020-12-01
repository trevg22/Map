import json
import timeit
from os import path

import numpy as np

from Response import Response

# from collections import namedtuple
# Stores list of responses at specific cell and time


class indepVar():

    def __init__(self, inc_name, inc_label):
        self.name = inc_name
        self.labels = inc_label


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
        self.responses = None

    def addElement(self, dataLine, cell, time, numCells):
        cell = int(cell)
        timeIndex = self.timeSteps.index(time)
        if self.simGrid[timeIndex] is None:
            cellArr = [None]*numCells
            self.simGrid[timeIndex] = cellArr
        self.simGrid[timeIndex][cell] = dataBy_cell_time(dataLine, cell, time)


    def set_responses(self, responses):
        self.responses = responses

    def get_simPrefix(self):
        return self.simPrefix
# Poplulats list of simInst objects from JSON


class Reader:

    def readMav_file(self, file):

        start = timeit.timeit()
        with open(file, 'r') as f:
            data = json.load(f)

        # self.readColorJson("colors.json")
        self.simList = []
        self.timeSteps = data["map-viewer"]["variables"]["Time"]
        self.coords = data["map-viewer"]["variables"]["Cells"]
        self.pathCells = data["map-viewer"]["variables"]["PathCells"]
        self.pathCells = [int(cell) for cell in self.pathCells]
        self.pathCells.sort()
        self.numCells = len(self.coords)
        # subtract 1 because time,cells is not part of "sim id"
        numVars = len(data["map-viewer"]["variables"]) - 3
        self.names = list(data["map-viewer"]["variables"].keys())[:numVars]
        self.labels = list(data["map-viewer"]["variables"].values())[:numVars]

#        numResponses = len(data["impact-viewer"]["groups"])
        self.responses = list(data["map-viewer"]["groups"].values())
        # print(self.responses)
        prevSim = None
        startIndex = numVars+2
        for dataLine in data["map-viewer"]["values"]:

            count = 0
            found = False

            simPrefix = dataLine[:numVars]
            # for x in range(numVars):
            # simPrefix+=str(dataLine[x])
            # Create new simInst if none exist
            if len(self.simList) == 0:

                self.simList.append(
                    simInst(simPrefix, self.numCells, self.timeSteps))
                prevSim = self.simList[0]
                self.simList[0].set_responses(self.responses)
                prevSim.addElement(
                    dataLine[startIndex:], dataLine[numVars + 1], dataLine[numVars], self.numCells)

            else:
                # if Incoming data belongs to same sim as previous data,
                # no need to loop
                if simPrefix == prevSim.simPrefix:
                    prevSim.addElement(
                        dataLine[startIndex:], dataLine[numVars + 1], dataLine[numVars], self.numCells)

                else:
                    # Locate simInst data belongs to, short circuit with found
                    while count < len(self.simList) and found is False:
                        if self.simList[count].simPrefix == simPrefix:
                            # this addElement will pass in dataLine as an int not a list
                            self.simList[count].addElement(
                                dataLine[startIndex:], dataLine[numVars + 1], dataLine[numVars], self.numCells)
                            prevSim = self.simList[count]
                            found = True
                        count = count + 1

                    if found is False:
                        self.simList.append(
                            simInst(simPrefix, self.numCells, self.timeSteps))
                        self.simList[-1].addElement(
                            dataLine[startIndex:], dataLine[numVars + 1], dataLine[numVars], self.numCells)
                        found = True

        self.print_SimInst(self.simList)
        self.validate_data()
        end = timeit.timeit()
        print("data read in", end-start, "seconds")
        return self.simList

    def validate_data(self):

        for sim in self.simList:
            self.validate_sinInst(sim)

    def validate_sinInst(self, simInst):
        for time in range(len(self.timeSteps)):
            for cell in range(self.numCells):

                if simInst.simGrid[time][cell] is None:
                    print("Sim with Prefix", simInst.simPrefix,
                          "missing", "time:", time, "cell", cell)

    def print_SimInst(self, simList):
        print("simulations")
        print("num Sims", len(self.simList))

        for sim in simList:
            print(sim.simPrefix)

    def get_timesteps(self):
        return self.timeSteps

    def get_responses(self):
        return self.responses

    def get_simList(self):
        return self.simList

    def get_simIdList(self):
        simIds = []
        for sim in self.simList:
            simIds.append(sim.get_simPrefix())
            print(sim.get_simPrefix())
        return simIds

    def get_cellCoords(self):
        vorCoords = [[coord[1], coord[0]] for coord in self.coords]
        return vorCoords

    def get_pathCells(self):
        return self.pathCells

    def get_IndVars(self):
        self.indVars = []
        if len(self.names) == len(self.labels):
            for x in range(len(self.names)):
                self.indVars.append(indepVar(self.names[x], self.labels[x]))
        else:
            print("Indep Var dimension mismatch")
            quit()

        return self.indVars
