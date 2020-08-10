# Imapct Map Viewer
# View.py
# Class that contains all gui code, all gui objects access model through Controller object
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
import matplotlib.pyplot as plt
from mapModel import mapModel
from netModel import netModel
import os
from ttkthemes import ThemedStyle
from matplotlib.backend_bases import MouseButton
class View:

    def __init__(self,root,mapModel,netModel):
        # Class members
        self.root=root
        self.mapModel=mapModel
        self.netModel=netModel
        self.curr_cellPatch=None
        root.title("Impact Map Viewer 0.0.4")

        self.create_mapFrames(root)
        self.create_netFrames()
        self.mapFig,self.mapAx=self.mapModel.get_fig_ax()
        self.netFig,self.netAx=self.netModel.get_fig_ax()
        self.create_menuBar(root)
        self.create_mapControlWidgets(self.mapControlFrame)
        self.create_netControlWidgets(self.netControlFrame)
        self.create_mapDataView(self.mapDataFrame)
        self.mapCanvas=self.create_mapCavas(self.mapPlotFrame)
        self.netCanvas=self.create_netCanvas(self.netPlotFrame)
        self.netConfigure_widgets()
        self.pack_mapFramess()
        self.toggleMap='Map'
        self.netPointType='Voronoi'
#start gui objects***************************************************
    def create_mapFrames(self, root):
            self.mapPlotFrame = ttk.Frame(root)
            self.mapControlFrame = ttk.Frame(root)
            self.mapDataFrame=ttk.LabelFrame(root,text="Responses")
            root.columnconfigure(0, weight=1)
            root.rowconfigure(1, weight=1)

            self.mapPlotFrame.columnconfigure(0, weight=1)
            self.mapPlotFrame.rowconfigure(0, weight=1)
    
    def create_netFrames(self):
        self.netPlotFrame=ttk.Frame(self.root)
        self.netControlFrame=ttk.Frame(self.root)
        
    def create_menuBar(self, frame):
        menuBar = tk.Menu(frame)
        fileMenu = tk.Menu(menuBar, tearoff=0)
        fileMenu.add_command(label='Load Mav',command=self.spinup_mapDataSet)
        fileMenu.add_command(label='Network',command=self.create_network_hardcoded)
        fileMenu.add_command(label='toggle',command=self.toggle_GUI)
        fileMenu.add_command(label='load map')
        menuBar.add_cascade(label='File', menu=fileMenu)
        editMenu = tk.Menu(menuBar, tearoff=0)
        menuBar.add_cascade(label='Edit', menu=editMenu)
        viewMenu = tk.Menu(menuBar, tearoff=0)
        menuBar.add_cascade(label='View', menu=viewMenu)
        frame.config(menu=menuBar)

    def create_mapControlWidgets(self, frame):
        self.idDropDown=ttk.Combobox(frame,width=7,state='readonly')
        self.selectTime_slider = tk.Scale(
                          frame,orient=tk.HORIZONTAL)
        self.selectTime_slider.bind("<ButtonRelease-1>",self.mapTimeSlider_released)
        self.respDropdown=ttk.Combobox(frame,width=27,state="readonly")
        self.respDropdown.bind("<<ComboboxSelected>>",self.mapDropdown_changed)
        self.idDropDown.bind("<<ComboboxSelected>>",self.map_idDropDown_changed)
        self.idDropDown.grid(row=1,column=0)
        self.respDropdown.grid(row=1,column=2)       
        self.selectTime_slider.grid(row=1, column=1)
    
    def create_netControlWidgets(self,frame):
        pointTypeButton=ttk.Button(frame,text='toggle',command=self.toggle_pointType)
        pointTypeButton.grid(row=0,column=0)
        

    def create_mapDataView(self,frame):
        self.dataBox=tk.Text(frame)
        self.dataBox.grid(row=0,column=0)
        self.dataBox.config(state=tk.NORMAL)
        self.dataBox.delete('1.0')
    
    def create_mapCavas(self, frame):
        canvas = FigureCanvasTkAgg(self.mapFig, master=frame)
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH,
                                    expand=True)
        toolbar = NavigationToolbar2Tk(canvas, frame)
        toolbar.update()
        return canvas
        
    def create_netCanvas(self,frame):
        canvas = FigureCanvasTkAgg(self.netFig, master=frame)
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH,
                                    expand=True)
        toolbar = NavigationToolbar2Tk(canvas, frame)
        toolbar.update()
        return canvas 

    def pack_mapFramess(self):
            self.mapControlFrame.grid(row=0, column=0,sticky=tk.W + tk.E)
            self.mapPlotFrame.grid(row=1, column=0, columnspan=3,
                        sticky=tk.W + tk.E + tk.N + tk.S)
            self.mapDataFrame.grid(row=0,column=4,rowspan=3)
        
    def pack_netFrames(self):
        self.netControlFrame.grid(row=0,column=0)
        self.netPlotFrame.grid(row=1,column=0)



# end gui objects************************************************************
# start gui object direct calls(one per)
    def spinup_mapDataSet(self):
        cwd=os.getcwd()
        dataFile=tk.filedialog.askopenfilename(initialdir=cwd)
        
        self.mapModel.read_mav_coords(dataFile,'coords.json')
        self.responses=self.mapModel.get_responses()
        self.mapModel.create_cellPatches()
        
        self.mapModel.plot_cellPatches()
        self.mapConfigure_plot()
        self.mapModel.create_legend()
        self.mapConfigure_widgets()
        self.dropdownIndex=int(self.respDropdown.current())
        self.mapModel.find_max(self.dropdownIndex) # replace with process data or something
        print("dataSet up")
        time=self.selectTime_slider.get()
        self.mapModel.set_currSim(0)
        self.mapModel.update_cellPatches(time)
        self.mapModel.print_SimInst([0,.5,1],1,5)
        print("Print ran")
        self.mapModel.colorize_cellPatches(self.dropdownIndex)
        self.mapCanvas.draw()
         
    def import_data(self):
        pass
    def mapTimeSlider_released(self,event):  
        time=self.selectTime_slider.get()
        self.mapModel.update_cellPatches(time)
        self.mapModel.colorize_cellPatches(self.dropdownIndex)
        self.mapCanvas.draw()
        print("called")
    
    def mapDropdown_changed(self,event):
        #print("changed to ", self.respDropdown.current())
        
        self.dropdownIndex=int(self.respDropdown.current())
        self.mapModel.find_max(self.dropdownIndex)
        self.mapModel.colorize_cellPatches(self.dropdownIndex)
        self.mapCanvas.draw()

    def map_idDropDown_changed(self,event):
        time=self.selectTime_slider.get()
        index=int(self.idDropDown.current())
        self.mapModel.set_currSim(index)
        self.mapModel.update_cellPatches(time)
        self.mapModel.find_max(self.dropdownIndex)
        self.mapModel.colorize_cellPatches(self.dropdownIndex)
        self.mapCanvas.draw()

    def mapMouse_moved(self,event):
       self.mapDetect_cellChange(event)
    
    def netMouse_clicked(self,event):
        if event.mouseevent.button==MouseButton.LEFT:
            mouseEvent=event.mouseevent
            self.netModel.append_points(mouseEvent.xdata,mouseEvent.ydata,self.netPointType)
#            self.netModel.coords.append((mouseEvent.xdata,mouseEvent.ydata))
            if self.netPointType=='Voronoi':
                self.netAx.plot(mouseEvent.xdata,mouseEvent.ydata,marker='.',picker=5)
            elif self.netPointType=='Boundary':
                self.netAx.plot(mouseEvent.xdata,mouseEvent.ydata,marker='*',picker=5)
            print("mouse clicked")
        else: 
            print('pick event')
            point =event.artist
            x=point.get_xdata()
            y=point.get_ydata()
            self.netModel.coords.remove((x,y))
            point.remove()
        self.netCanvas.draw()        
   
    
    def toggle_GUI(self):

        if self.toggleMap=="Map":
           self.mapPlotFrame.grid_forget()
           self.mapControlFrame.grid_forget()
           self.mapDataFrame.grid_forget()
           self.pack_netFrames()
           self.toggleMap="Net"
        elif self.toggleMap=="Net":
            self.netPlotFrame.grid_forget()
            self.netControlFrame.grid_forget()
            self.pack_mapFramess()
            self.toggleMap="Map"
        else:
            print("Toggle has invalid value")
    
    def toggle_pointType(self):
        if self.netPointType=='Voronoi':
            self.netPointType='Boundary'
        elif self.netPointType=='Boundary':
            self.netPointType='Voronoi'

        print("point toggled")
    def create_network(self):
        self.netModel.create_network()
        self.netCanvas.draw()

    def create_network_hardcoded(self):
        self.netModel.create_network_hardcoded()
        self.netCanvas.draw()
# end gui object direct calls(one per)**********************************************

# start supporting functions************************************************
    def mapDetect_cellChange(self,event):
        if event.inaxes==self.mapAx:
            mouse_in_cell=self.mapModel.is_point_in_cell(event.xdata,event.ydata,self.curr_cellPatch)
            if mouse_in_cell==False:
                self.curr_cellPatch,found=self.mapModel.determine_cell_from_point(event.xdata,event.ydata)

                if found:
                    #print("changed to cell : ", self.curr_cellPatch.get_cell())
                    self.mapWrite_dataBox()

                else:
                    pass
                    # return 0;
                    #print("outside grid")
            else:
                pass
                # return -1                
                #print("same cell")

    def mapWrite_dataBox(self):
        self.dataBox.delete('1.0',tk.END)
        header="Cell " + str(self.curr_cellPatch.get_cell()) + "\n"
        self.dataBox.insert(tk.END,header)
        
        for x in range(len(self.respList)):

            responseData=self.curr_cellPatch.get_data()
            responseName = str(self.respList[x]) +": " 
            self.dataBox.insert(tk.END,responseName)
            if x<=len(responseData):
                dataLine=str(responseData[x]) +"\n"
            else:
                dataLine ="No data available"
                
            if x==self.dropdownIndex:
                self.dataBox.insert(tk.END,dataLine)
            else:
                self.dataBox.insert(tk.END,dataLine)
    
# end supporting functions ******************************************

# start widget/plotconfigure methods**************************************************
    def mapConfigure_plot(self):
        limits=self.mapModel.get_vorPlotLim()
        self.mapAx.set_xlim(limits[0][0],limits[0][1])
        self.mapAx.set_ylim(limits[1][0],limits[1][1])

    def mapConfigure_widgets(self):
        # configure timeSlider passed on input data
        range,stepsPerday=self.mapModel.get_timeParams()
        timeSliderRes=1/stepsPerday
        self.selectTime_slider.config(resolution=timeSliderRes,from_=range[0],to=range[1],digits=4)
        simIds=self.mapModel.get_simIdList()
        self.idDropDown.config(values=simIds)
        self.idDropDown.set(simIds[0])
        print("sim Ids",simIds)
        # configure target/response dropdown
        responses=self.responses
        self.respList=list(responses[0])
        print(responses)
        self.respDropdown.config(values=self.respList)
        self.respDropdown.set(self.respList[0])
        # configure databox widget
        self.dataBox.config(width=35) 
        self.mapFig.canvas.mpl_connect("motion_notify_event",self.mapMouse_moved)
    def netConfigure_widgets(self):
        self.netAx.set_picker(picker=True)
        self.netClickCid=self.netFig.canvas.mpl_connect('pick_event',self.netMouse_clicked)
# end widget/plotconfigure methods******************************************************
# start main
def main():
    root = tk.Tk()
    style = ThemedStyle(root)
    style.theme_use("arc")
    guiMapModel=mapModel()
    guiNetModel=netModel()
    maingui=View(root,guiMapModel,guiNetModel)
    root.mainloop()
    #root.protocol("WM_DELETE_WINDOW", destroyer)
    root.destroy()


if __name__ == "__main__":
    main()
