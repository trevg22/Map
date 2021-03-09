# Map Viewer
# Classes to handle response functionality
import colorsys

from matplotlib import cm, colors

# a cell response metric


class Response:
    def __init__(self):
        self.name = ""
        self.min = None
        self.max = 0
        self.hue = None
        self.type = None
        self.upperThresh = 0.9  # maximum light value to avoid moving to black
        self.lowerThresh = 0.2
        self.smallValPerc = 0.0001
        self.index = 0

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
        hueFrac = self.hue / 360  # normalize hue
        sat = 1  # represents 100 percent
        if self.max > 0 and data is not None:
            # lightness = (1-(data/self.max)*threshold)

            if data >= self.max * self.smallValPerc and data < self.max:
                delta = self.upperThresh - self.lowerThresh
                lightness = (1 - (data / self.max)) * delta + self.lowerThresh
                color = colorsys.hls_to_rgb(hueFrac, lightness, sat)
            elif data < self.max * self.smallValPerc:
                color = [1, 1, 1]
            elif data >= self.max:
                color = colorsys.hls_to_rgb(hueFrac, self.lowerThresh, sat)
        else:
            color = [1, 0, 0]
        return color

    def gen_cmap(self, cmapStr):
        self._cmapStr = cmapStr
        self.cmap = cm.get_cmap(self._cmapStr, 100)
        self.normalizer = colors.Normalize(vmin=self.min, vmax=self.max)

    def gen_cmapColor(self, data):
        if self.max > 0 and data is not None:
            if data > self.max * self.smallValPerc:
                normData = self.normalizer(data)
                color = self.cmap(normData)
            else:
                color = [1, 1, 1]
        else:
            color = [1, 0, 0]
        return color

    def gen_color(self, data):
        if self.type == "linear":
            return self.gen_colorLinear(data)

    @property
    def cmapStr(self):
        return self._cmapStr

    @cmapStr.setter
    def cmapStr(self, cmap):
        self._cmapStr = cmap
        self.gen_cmap(cmap)
        print("cmap changed")
