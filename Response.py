# Map Viewer
# Classes to handle response functionality
import colorsys

# a cell response metric


class Response:

    def __init__(self):
        self.name = ""
        self.min=None
        self.max=0
        self.hue=None
        self.type=None
        self.upperThresh=.9# maximum light value to avoid moving to black
        self.lowerThresh=.2
        self.smallValPerc=.0001

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
        self.min=self.max

    def find_respMin(self, simList,response):

        for sim in simList:
            for timeSlice in sim.simGrid:
                for cell in timeSlice:
                    if cell is None:
                        print("simGrid is none")
                    else:
                        data = cell.dataLine[response]
                    if data is not None:
                        if data < self.min:
                            self.min = data


    def gen_colorLinear(self, data):
        # Hue value from HSL color standard(0-360 degrees)
        hueFrac = self.hue/360  # normalize hue
        sat = 1  # represents 100 percent
        if self.max > 0 and data is not None:
            # lightness = (1-(data/self.max)*threshold)
            
            if data >= self.max*self.smallValPerc and data <self.max:
                delta=self.upperThresh-self.lowerThresh
                lightness=(1-(data/self.max))*delta+self.lowerThresh
                color = colorsys.hls_to_rgb(hueFrac, lightness, sat)

                # print("data of",data,"produced lightness of",lightness)
            elif data <self.max*self.smallValPerc and data>self.min:
                color=[1,1,0]
            elif data <=self.min:
                color=[1,1,1]
            elif data >=self.max:
                color=colorsys.hls_to_rgb(hueFrac,self.lowerThresh,sat)
        else:
            color = [1, 0, 0]
        return color

    def gen_colorNorm(self,data,max,area):
        hueFrac = self.hue/360  # normalize hue
        sat = 1  # represents 100 percent
        threshold = .70  # maximum light value to avoid moving to black
        if self.max > 0 and data is not None:
            # lightness = (1-(data/self.max)*threshold)
            data=data/area
            lightness=1-(data/max)*threshold
            color = colorsys.hls_to_rgb(hueFrac, lightness, sat)
        else:
            color = [1, 0, 0]
        return color
 

    def gen_color(self,data):
        if self.type=="linear":
            return self.gen_colorLinear(data)

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
        self.min=self.max

    def find_respMin(self, simList,response):

        for sim in simList:
            for timeSlice in sim.simGrid:
                for cell in timeSlice:
                    if cell is None:
                        print("simGrid is none")
                    else:
                        data = cell.dataLine[response]
                    if data is not None:
                        if data < self.min:
                            self.min = data

    def gen_color(self,data):
        return self.gen_colorLinear(data)

    def gen_colorLinear(self, data):
        # Hue value from HSL color standard(0-360 degrees)
        hueFrac = self.hue/360  # normalize hue
        sat = 1  # represents 100 percent
        threshold = .70  # maximum light value to avoid moving to black

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
    