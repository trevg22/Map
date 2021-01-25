# Map Viewer
# Classes to handle response functionality
import colorsys

# a cell response metric


class Response:

    def __init__(self):
        self.name = ""
        self.min = None
        self.max = 0
        self.hue = None
        self.type = None
        self.upperThresh = .9  # maximum light value to avoid moving to black
        self.lowerThresh = .2
        self.smallValPerc = .0001

    def find_respMax(self, simList, response):

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
        self.min = self.max

    def find_respMin(self, simList, response):

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

            if data >= self.max*self.smallValPerc and data < self.max:
                delta = self.upperThresh-self.lowerThresh
                lightness = (1-(data/self.max))*delta+self.lowerThresh
                color = colorsys.hls_to_rgb(hueFrac, lightness, sat)
            elif data < self.max*self.smallValPerc:
                color = [1, 1, 1]
            elif data >= self.max:
                color = colorsys.hls_to_rgb(hueFrac, self.lowerThresh, sat)
        else:
            color = [1, 0, 0]
        return color

    # def gen_colorLinear_smallVal(self, data):
    #         # Hue value from HSL color standard(0-360 degrees)
    #         hueFrac = self.hue/360  # normalize hue
    #         sat = 1  # represents 100 percent
    #         if self.max > 0 and data is not None:
    #             # lightness = (1-(data/self.max)*threshold)

    #             if data >= self.max*self.smallValPerc and data <self.max:
    #                 delta=self.upperThresh-self.lowerThresh
    #                 lightness=(1-(data/self.max))*delta+self.lowerThresh
    #                 color = colorsys.hls_to_rgb(hueFrac, lightness, sat)

    #                 # print("data of",data,"produced lightness of",lightness)
    #             elif data <self.max*self.smallValPerc and data>self.min:
    #                 color=[1,1,0]
    #             elif data <=self.min:
    #                 color=[1,1,1]
    #             elif data >=self.max:
    #                 color=colorsys.hls_to_rgb(hueFrac,self.lowerThresh,sat)
    #         else:
    #             color = [1, 0, 0]
    #         return color

    def gen_colorNorm(self, data, max, area):
        hueFrac = self.hue/360  # normalize hue
        sat = 1  # represents 100 percent
        threshold = .70  # maximum light value to avoid moving to black
        if self.max > 0 and data is not None:
            # lightness = (1-(data/self.max)*threshold)
            data = data/area
            lightness = 1-(data/max)*threshold
            color = colorsys.hls_to_rgb(hueFrac, lightness, sat)
        else:
            color = [1, 0, 0]
        return color

    def gen_color(self, data):
        if self.type == "linear":
            return self.gen_colorLinear(data)

