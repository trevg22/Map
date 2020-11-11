# Map Viewer
# MapFrame.py
# Contains ttk.frame classes that handle different MapViewer functionality
import tkinter as tk
from tkinter import ttk
from tkinter.ttk import Frame, LabelFrame

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)

import settings


def pack_frame(frame, row, col, sticky=False):
    if sticky == False:
        frame.grid(row=row, column=col)
    else:
        frame.grid(row=row, column=col, sticky=tk.N+tk.E+tk.W+tk.S)


# Parent frame that contains a MapControlFrame and MapPlotFrame


class MapParentFrame(LabelFrame):

    def __init__(self, label, view):
        self.view = view
        self.label = label

    def init_frames(self, master):
        super().__init__(master, text=self.label)
        self.controlFrame = MapControlFrame(
            self.view, master=self, parent=self)
        self.mapFrame = MapPlotFrame(
            self.view, master=self, controlFrame=self.controlFrame)
        self.controlFrame.set_plotFrame(self.mapFrame)
        self.pack_children()

    def set_master(self, inc_frame):
        self.master = inc_frame

    def pack_children(self):
        pack_frame(self.controlFrame, 0, 0)
        pack_frame(self.mapFrame, 1, 0, sticky=True)

    def plot_cellPatches(self, cellPatches):
        self.mapFrame.plot_cellPatches(cellPatches)

    def set_plotLims(self, xrange, yrange):
        self.mapFrame.set_plotLims(xrange, yrange)

    def get_timeSliderVal(self):
        pass

    def get_controlFrame(self):
        return self.controlFrame

    def get_plotFrame(self):
        return self.mapFrame

# Frame that contains sliders and dropdowns to control map
# May contain a reference to mapPlotFrame if self is member of MapParentFrame


class MapControlFrame(Frame):

    def __init__(self, view, master=None, default=True, parent=None, plotFrame=None):
        self.view = view
        self.master = master
        self.plotFrame = plotFrame
        self.parent = parent
        if master is not None:
            super().__init__(master)
        else:
            self.frame = ttk.Frame()

        if default == True:
            self.checkVar = tk.IntVar()
            self.respDropDown = ttk.Combobox(self)
            self.simIdDropDown = ttk.Combobox(self, width=3)
            self.timeSlider = tk.Scale(self, orient=tk.HORIZONTAL, showvalue=0)
            self.scaleFacDrop = ttk.Combobox(self)
            self.toggleDensityCheck = ttk.Checkbutton(self, var=self.checkVar)
            self.timeSpin = ttk.Spinbox(self)
            self.settingsButton = ttk.Button(self, width=4,text="\u2699")
            self.config_widgetDefaults()
            self.pack_children()
        else:
            self.respDropDown = None
            self.simIdDropDown = None
            self.timeSlider = None

    # Bind widget events to View functions
    def config_widgetDefaults(self):
        self.timeSlider.bind(
            "<ButtonRelease-1>", lambda event: self.timeSliderChanged(event))
        self.simIdDropDown.bind(
            "<<ComboboxSelected>>", lambda event: self.view.map_simIdDropdownChanged(self, event))
        self.respDropDown.bind(
            "<<ComboboxSelected>>", lambda event: self.view.map_responseDropDownChanged(self, event))

        self.toggleDensityCheck.config(
            command=lambda: self.view.densityToggled(self))
        self.scaleFacDrop.bind(
            "<<ComboboxSelected>>", lambda event: self.view.scaleFacChanged(self, event))
        self.timeSpin.config(command=self.timeSpinChanged)
        self.timeSpin.set('0.00')
        scaleFactors = [10, 100, 1000, 10000, 100000]
        scaleFactors.sort()
        factorPad = len(str(scaleFactors[-1]))

        self.scaleFacDrop.config(values=scaleFactors, width=factorPad)
        self.scaleFacDrop.set(scaleFactors[0])
        self.settingsButton.config(
            command=lambda: self.view.spawn_plotSettings(self.parent))

    def pack_children(self):
        idLabel = ttk.Label(self, text="Run")
        timeLabel = ttk.Label(self, text="Time")
        respLabel = ttk.Label(self, text="Response")
        scaleFacLabel = ttk.Label(self, text="Scale Factor")
        toggleDensityLabel = ttk.Label(self, text='Toggle Density')
        settingsLabel = ttk.Label(self, text='Settings')
        idLabel.grid(row=0, column=0)
        self.simIdDropDown.grid(row=1, column=0)
        timeLabel.grid(row=0, column=2)
        self.timeSlider.grid(row=1, column=2)
        respLabel.grid(row=0, column=3)
        self.respDropDown.grid(row=1, column=3)
        scaleFacLabel.grid(row=0, column=4)
        self.scaleFacDrop.grid(row=1, column=4)
        toggleDensityLabel.grid(row=0, column=5)
        self.toggleDensityCheck.grid(row=1, column=5)
        settingsLabel.grid(row=0,column=6)
        self.settingsButton.grid(row=1, column=6)
        self.timeSpin.grid(row=1, column=1)

        self.grid(row=1, column=0)

    def timeSpinChanged(self):
        value = self.timeSpin.get()
        self.timeSlider.set(value)
        self.view.map_timeSliderReleased(self, None)

    def timeSliderChanged(self, event):
        value = self.timeSlider.get()
        self.timeSpin.set(value)
        self.view.map_timeSliderReleased(self, event)

    def set_master(self, inc_frame):
        self.master = inc_frame

    def get_timeSliderVal(self):
        return float(self.timeSlider.get())

    def get_respDropIndex(self):
        return int(self.respDropDown.current())

    def get_simIdDropIndex(self):
        return int(self.simIdDropDown.current())

    def get_simIdDropVal(self):
        return str(self.simIdDropDown.get())

    def get_respDropDownVal(self):
        return str(self.respDropDown.get())

    def config_simIdDrop(self, *arg, **kwargs):
        self.simIdDropDown.config(*arg, **kwargs)

    def config_timeSlider(self, *arg, **kwargs):
        self.timeSlider.config(*arg, **kwargs)

    def config_respDrop(self, *arg, **kwargs):
        self.respDropDown.config(*arg, **kwargs)

    def config_timeSpin(self, *arg, **kwargs):
        self.timeSpin.config(*arg, **kwargs)

    def set_timeSliderIndex(self, index):
        self.timeSlider.set(index)

    def set_simIdDropIndex(self, index):
        self.simIdDropDown.set(index)

    def set_respDropIndex(self, index):
        self.respDropDown.set(index)

    def set_runDropIndex(self, index):
        self.simIdDropDown.set(index)

    def set_plotFrame(self, frame):
        self.plotFrame = frame

    def get_master(self):
        return self.master

    def get_plotFrame(self):
        return self.plotFrame

    def get_densityToggle(self):
        return int(self.checkVar.get())

    def get_densityScaleFac(self):
        return int(self.scaleFacDrop.get())
# Frame to hold map plot
# May contain reference to dataFrame


class MapPlotFrame(Frame):
    def __init__(self, view, master=None, default=True, controlFrame=None, dataBox=None):
        self.view = view
        self.hoverCell = None
        self.currCell = None

        self.controlFrame = controlFrame
        self.dataFrame = None
        self.legendLoc = settings.defLegendLoc
        self.showLegend = True

        if master is not None:
            super().__init__(master)
        else:
            self.frame = ttk.Frame()
        self.fig = plt.Figure()
        self.fig.subplots_adjust(
            left=None, bottom=None, right=None, top=None, wspace=None, hspace=None)
        self.ax = self.fig.add_subplot(111, projection=ccrs.PlateCarree())
        self.ax.set_global()
    # Put a background image on for nice sea rendering.
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        toolbar = NavigationToolbar2Tk(self.canvas, self)
        toolbar.update()
        if default:
            self.config_widgetDefaults()

    def config_widgetDefaults(self):
        self.fig.canvas.mpl_connect(
            "motion_notify_event", lambda event: self.view.map_mouseMoved(self, event))

        self.fig.canvas.mpl_connect(
            'pick_event', lambda event: self.view.map_mouseClicked(self, event))

    def plot_cellPatches(self, cellPatches):
        self.cellPatches = cellPatches
        for index, patch in enumerate(cellPatches):
            patch.set_facecolor([1, 1, 1])
            # if index ==14:
            #     self.ax.add_patch(patch)
            self.ax.add_patch(patch)
        self.canvas.draw()

    def update_cellPatchColor(self, color, cell):
        self.cellPatches[cell-1].set_facecolor(color)

    def update_cellPatchAlpha(self, alpha, cell):
        self.cellPatches[cell-1].set_alpha(alpha)

    def draw_canvas(self):
        self.canvas.draw()

    def reset_patchAlphas(self, alpha):
        for patch in self.cellPatches:
            patch.set_alpha(alpha)

    def set_plotLims(self, xrange, yrange):

        self.ax.set_xlim(xrange[0], xrange[1])
        self.ax.set_ylim(yrange[0], yrange[1])
        self.canvas.draw()

    def set_dataFrame(self, frame):
        self.dataFrame = frame

    def get_cellPatches(self):
        pass

    def set_hoverCell(self, cellNum):
        self.hoverCell = cellNum

    def set_currCell(self, cellNum):
        self.currCell = cellNum

    def set_legend(self, handles):
        print("legend set")
        self.ax.legend(handles=handles, loc='upper left')
        self.draw_canvas()

    def get_currCell(self):
        return self.currCell

    def get_hoverCell(self):

        return self.hoverCell

    def get_axes(self):
        return self.ax

    def get_controlFrame(self):
        return self.controlFrame

    def get_dataFrame(self):
        return self.dataFrame

        # self.resize()
    # def resize(self):
    #     self.frame.config(height=50,width=50)
    #     self.fig.set_figheight(3)
    #     self.fig.set_figwidth(3)

# Frame that contains text widet


class TextFrame(LabelFrame):

    def __init__(self, label, view, master=None, parent=None):
        self.label = label
        self.parent = parent
        self.view = view
        if master is not None:
            pass
            #super().__init__(master, text=label)

    def init_frames(self, master):
        super().__init__(master, text=self.label)
        self.textBox = tk.Text(self, width=30)
        self.selLabel = ttk.Label(self, text="Selected:")
        self.hovLabel = ttk.Label(self, text="Hovered: ")
        self.cellEntry = ttk.Entry(self)
        self.pack_children()

    def pack_children(self):
        self.textBox.grid(row=2, column=0)
        self.hovLabel.grid(row=0, column=0)
        self.selLabel.grid(row=1, column=0)

    def change_cell(self):
        self.view.cell_changed(self.get_parent(), 5)

    # append line to end of text box
    def write_line(self, line):
        self.textBox.insert(tk.END, line)
    # clear text box

    def clear(self):
        self.textBox.delete('1.0', tk.END)

    # scroll to bring line into view
    def view_line(self, line):
        ind = self.textBox.search(str(line), 1.0, stopindex=tk.END)
        if ind:
            self.textBox.see(ind)

    def view_currLine(self):
        self.view_line(self.currLine)

    def set_currLine(self, line):
        self.currLine = line

    # Write cell number that is currently being hovered over
    def write_hoverLabel(self, line):
        self.hovLabel.config(text="Hover Cell:"+str(line))

    # Write cell number that is selected
    def write_selectedLabel(self, cell):
        area = cell.get_cellArea()
        ctype = cell.get_cellType()
        cellNum = cell.get_cellNum()
        text = "Selected Cell: " + \
            str(cellNum)+"\n Type: " + str(ctype) + \
            "\n Area " + "{0:.2f}".format(area)+" km^2"

        self.selLabel.config(text=text)

    def set_parent(self, parent):
        self.parent = parent

    def get_parent(self):
        return self.parent


class MapSettingsFrame(LabelFrame):

    def __init__(self, label, view, master=None, parent=None):
        self.view = view
        self.master = master
        self.parent = parent
        self.label = label

    def init_frames(self, master):
        self.master = master
        super().__init__(self.master, text=self.label)
        self.legendLocDrop = ttk.Combobox(self)
        self.configWidget_defaults()
        self.pack_children()

    def pack_children(self):
        self.legendLocDrop.grid(row=0, column=0)

    def configWidget_defaults(self):
        values = ['upper left', 'upper right', 'lower left', 'lower right']
        self.legendLocDrop.config(values=values)
        self.legendLocDrop.set(settings.defLegendLoc)
        self.legendLocDrop.bind(
            "<<ComboboxSelected>>", self.legendLoc_changed)

    def legendLoc_changed(self, event):
        args = {}
        args["legendLoc"] = str(self.legendLocDrop.get())
        self.view.plotSettings_changed(args, self.parent)
