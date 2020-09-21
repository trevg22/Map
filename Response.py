# Map Viewer
# Classes to handle response functionality
import colorsys

# a cell response metric


class response:

    def __init__(self):
        self.name = ""

    def set_respGroup(self, inc_respGroup):
        self.respGroup = inc_respGroup

    def set_name(self, inc_name):
        self.name = inc_name

# a group of responses that need to be treated similarly


class responseGroup:
    def __init__(self):
        self.group = ""
        self.hue = 0
        self.responseIndexes = []
        self.type = ""
        self.responseNames = []
        self.max = 0

    def find_max(self, currSim):

        for resp in self.responseIndexes:
            for time in range(len(currSim.simGrid)):
                for cell in range(len(currSim.simGrid[time])):
                    value = currSim.simGrid[time][cell].dataLine[resp]

                    if value is not None and value > self.max:
                        self.max = value

    def genColor_linear(self, respdata):
        hueFrac = self.hue/360
        sat = 1  # represents 100 percent
        threshold = .90  # maximum light value to avoid moving to black

        #print("Patch data for cell num",patch.cell," ", patch.data)
        lightness = (1-(respdata/max)*threshold)
        return colorsys.hls_to_rgb(hueFrac, lightness, sat)

    def genColor_log(self, respdata):
        pass

    def map_toColorFunc(self):
        if self.type == "linear" or self.type == "default":
            self.colorFunc = self.genColor_linear
        elif self.type == "log":
            self.colorFunc = self.genColor_log
        else:
            print("invalid response group type", self.type)
            quit()

    def set_type(self, inc_type):
        self.type = inc_type

    def set_group(self, inc_group):
        self.group = inc_group

    def set_hue(self, inc_hue):
        self.hue = inc_hue

    def set_responses(self, inc_responses):
        self.responses = inc_responses

    def set_max(self, inc_max):
        self.max = inc_max

    def append_responseIndex(self, inc_index):
        self.responseIndexes.append(inc_index)
