# Map Viewer
# ColorFrame.py
from tkinter.ttk import LabelFrame

from Response import Response


class ColorParentFrame(LabelFrame):
    def __init__(self, label, view):
        self.label = label
        self.view = view

    def init_frames(self, master):
        super().__init__(master, text=self.label)

        self.respDropDown = ttk.Combobox(self)
        self.hueEntry = ttk.Entry(self)
        self.maxEntry = ttk.Entry(self)
        self.minEntry = ttk.Entry(self)
        self.saveButton = ttk.Button(self, text="Save")
        self.updateButton = ttk.Button(self, text="Update All")
        self.upperThreshEntry = ttk.Entry(self)
        self.lowerThreshEntry = ttk.Entry(self)
        self.smallValPercEntry = ttk.Entry(self)
        self.config_widgetDefaults()
        self.pack_children()

    def pack_children(self):
        respLabel = ttk.Label(self, text="Response")
        hueLabel = ttk.Label(self, text="Hue")
        maxLabel = ttk.Label(self, text="Max")
        minLabel = ttk.Label(self, text="Min")
        lowerThreshLabel = ttk.Label(self, text="Low Thresh 0<=x<=1")
        upperThreshLabel = ttk.Label(self, text="Upper Thresh 0<=x<=1")
        smallValLabel = ttk.Label(self, text="low val %")
        self.respDropDown.grid(row=0, column=1)
        respLabel.grid(row=0, column=0)
        self.hueEntry.grid(row=1, column=1)
        hueLabel.grid(row=1, column=0)
        self.maxEntry.grid(row=2, column=1)
        maxLabel.grid(row=2, column=0)
        self.minEntry.grid(row=3, column=1)
        minLabel.grid(row=3, column=0)
        self.saveButton.grid(row=4, column=1)
        self.updateButton.grid(row=4, column=0)

        self.upperThreshEntry.grid(row=1, column=3)
        upperThreshLabel.grid(row=1, column=4)
        self.lowerThreshEntry.grid(row=2, column=3)
        lowerThreshLabel.grid(row=2, column=4)
        self.smallValPercEntry.grid(row=3, column=3)
        smallValLabel.grid(row=3, column=4)

    def savePressed(self):
        args = {}
        responseI = int(self.respDropDown.current())
        args["responseIndex"] = responseI

        maxVal = self.maxEntry.get()
        minVal = self.minEntry.get()
        hue = self.hueEntry.get()
        upperThresh = self.upperThreshEntry.get()
        lowerThresh = self.lowerThreshEntry.get()
        smallValPerc = self.smallValPercEntry.get()
        try:
            float(maxVal)
            args["maxVal"] = float(maxVal)
        except ValueError:
            self.not_float("max val", maxVal)
        try:
            float(minVal)
            args["minVal"] = float(minVal)

        except ValueError:
            self.not_float("min val", minVal)

        try:
            float(hue)
            args["hue"] = float(hue)
        except ValueError:
            self.not_float("hue", hue)
        try:
            float(upperThresh)
            args["upperThresh"] = float(upperThresh)
        except ValueError:
            self.not_float("upper threshold", upperThresh)

        try:
            float(lowerThresh)
            args["lowerThresh"] = float(lowerThresh)
        except ValueError:
            self.not_float("lower threshold", lowerThresh)

        try:
            float(smallValPerc)
            args["smallValPerc"] = float(smallValPerc)
        except ValueError:
            self.not_float("small value %", smallValPerc)
        self.view.responsePropsChanged(args, self)

    def not_float(self, varName, entryVal):
        print(varName, "entry of", entryVal, "is not a float")

    def updateAll_pressed(self):
        self.savePressed()

        responseInd = int(self.respDropDown.current())
        self.view.updateAll_respProps(responseInd)

    def update_entrys(self, currResp: Response):

        self.maxEntry.delete(0, tk.END)
        self.minEntry.delete(0, tk.END)
        self.maxEntry.insert(0, str(currResp.max))
        self.minEntry.insert(0, str(currResp.min))
        self.hueEntry.delete(0, tk.END)
        self.hueEntry.insert(0, str(currResp.hue))
        self.upperThreshEntry.delete(0, tk.END)
        self.upperThreshEntry.insert(0, str(currResp.upperThresh))
        self.lowerThreshEntry.delete(0, tk.END)
        self.lowerThreshEntry.insert(0, str(currResp.lowerThresh))
        self.smallValPercEntry.delete(0, tk.END)
        self.smallValPercEntry.insert(0, str(currResp.smallValPerc))

    def config_widgetDefaults(self):
        self.saveButton.config(command=self.savePressed)
        self.updateButton.config(command=self.updateAll_pressed)
        self.respDropDown.bind(
            "<<ComboboxSelected>>",
            lambda event: self.view.colorResponseChanged(self, event),
        )

    def config_respDrop(self, *args, **kwargs):
        self.respDropDown.config(*args, **kwargs)

    def set_respDropIndex(self, index):
        self.respDropDown.set(index)

    def get_respDropIndex(self):
        return self.respDropDown.current()
