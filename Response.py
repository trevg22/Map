# Map Viewer
# Classes to handle response functionality
import colorsys

# a cell response metric


class Response:

    def __init__(self):
        self.name = ""

    def gen_color(self,data):
        return self.respGroup.gen_color(data)
    def set_respGroup(self, inc_respGroup):
        self.respGroup = inc_respGroup

    def set_name(self, inc_name):
        self.name = inc_name

    def get_respGroup(self):
        return self.respGroup

    
# a group of responses that need to be treated similarly


class ResponseGroup:
    def __init__(self):
        self.group = ""
        self.hue = 0
        self.responseIndexes = []
        self.type = ""
        self.responseNames = []
        self.max = 0

    def find_groupMax(self,simList):
        for resp in self.responseIndexes:
            self.find_respMax(simList,resp)

    def find_respMax(self, simList,response):

        for sim in simList:
            for timeSlice in sim.simGrid:
                for cell in timeSlice:
                    if cell is None:
                        print("simGrid is none")
                    else:
                        data = cell.dataLine[response]
                    if data is not None:
                        if data > self.max:
                            self.max = data

    def gen_color(self,data):
        return self.gen_colorLinear(data)

    def gen_colorLinear(self, data):
        # Hue value from HSL color standard(0-360 degrees)
        print("using hue:",self.hue)
        hueFrac = self.hue/360  # normalize hue
        sat = 1  # represents 100 percent
        threshold = .90  # maximum light value to avoid moving to black

        if self.max > 0 and data is not None:
            lightness = (1-(data/self.max)*threshold)
            color = colorsys.hls_to_rgb(hueFrac, lightness, sat)
        else:
            color = [1, 0, 0]
        return color
    

    def genColor_log(self, respdata):
        pass

    def map_toColorFunc(self):
        if self.type == "linear" or self.type == "default":
            self.colorFunc = self.gen_colorLinear
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
        self.responseNames = inc_responses

    def set_max(self, inc_max):
        self.max = inc_max

    def append_responseIndex(self, inc_index):
        self.responseIndexes.append(inc_index)

    def get_responseIndexes(self):
        return self.responseIndexes

    def get_responseNames(self):
        return self.responseNames

    def get_group(self):
        return self.group

    def get_max(self):
        return self.max
    
    def get_hue(self):
        return self.hue
    