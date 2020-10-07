# Map Viewer
# ColorFrame.py
from tkinter.ttk import LabelFrame
from tkinter import ttk
import tkinter as tk


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
        self.config_widgetDefaults()
        self.pack_children()

    def pack_children(self):
        respLabel = ttk.Label(self, text="Response")
        hueLabel = ttk.Label(self, text="Hue")
        maxLabel = ttk.Label(self, text="Max")
        minLabel = ttk.Label(self, text="Min")
        self.respDropDown.grid(row=0, column=1)
        respLabel.grid(row=0, column=0)
        self.hueEntry.grid(row=1, column=1)
        hueLabel.grid(row=1, column=0)
        self.maxEntry.grid(row=2, column=1)
        maxLabel.grid(row=2, column=0)
        self.minEntry.grid(row=3, column=1)
        minLabel.grid(row=3, column=0)
        self.saveButton.grid(row=4, column=1)

    def savePressed(self):
        args = {}
        responseI = int(self.respDropDown.current())
        args["responseIndex"] = responseI

        maxVal = self.maxEntry.get()
        minVal = self.minEntry.get()
        hue = self.hueEntry.get()
        try:
            float(maxVal)
            args["maxVal"] = float(maxVal)
        except ValueError:
            print("Not a float")

        try:
            float(minVal)
            args["minVal"] = float(minVal)

        except ValueError:
            print("minVal is not a float")

        try:
            float(hue)
            args["hue"] = float(hue)
        except ValueError:
            print("hue is not a float")

        self.view.responsePropsChanged(args, self)

    def update_entrys(self, minVal, maxVal, hue):
        self.maxEntry.delete(0, tk.END)
        self.minEntry.delete(0, tk.END)
        self.maxEntry.insert(0, str(maxVal))
        self.minEntry.insert(0, str(minVal))
        self.hueEntry.delete(0, tk.END)
        self.hueEntry.insert(0, str(hue))

    def config_widgetDefaults(self):
        self.saveButton.config(command=self.savePressed)
        self.respDropDown.bind(
            "<<ComboboxSelected>>", lambda event: self.view.colorResponseChanged(self, event))

    def config_respDrop(self, *args, **kwargs):
        self.respDropDown.config(*args, **kwargs)

    def config_maxEntry(self, *args, **kwargs):
        self.maxEntry.config(*args, **kwargs)

    def config_minValEntry(self, *args, **kwargs):
        self.minEntry.config(*args, **kwargs)

    def config_saveButton(self, *args, **kwargs):
        self.saveButton.config(*args, **kwargs)

    def set_respDropIndex(self, index):
        self.respDropDown.set(index)

    def get_respDropIndex(self):
        return self.respDropDown.current()
