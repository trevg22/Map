# Imapct Map Viewer
# View.py
# Class that contains all gui code, all gui objects access model through Controller object
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
import matplotlib.pyplot as plt
from Model import Model
import os
from ttkthemes import ThemedStyle

class View:

    def __init__(self,root,model):
        # Class members
        self.model=model
        self.curr_cellPatch=None
        root.title("Impact Map Viewer 0.0.2")

        plotFrame,controlFrame,dataFrame=self.create_frames(root)
        self.fig,self.ax=self.model.get_fig_ax()
        self.create_menuBar(root)
        self.create_mapControlWidgets(controlFrame)
        self.create_mapDataView(dataFrame)
        self.canvas=self.create_mapCavas(plotFrame)
        self.place_frames(plotFrame,controlFrame,dataFrame)

#start gui objects***************************************************
    def create_frames(self, root):
            plotFrame = ttk.Frame(root)
            controlFrame = ttk.Frame(root)
            dataFrame=ttk.LabelFrame(root,text="Responses")
            root.columnconfigure(0, weight=1)
            root.rowconfigure(1, weight=1)

            plotFrame.columnconfigure(0, weight=1)
            plotFrame.rowconfigure(0, weight=1)
            return plotFrame, controlFrame,dataFrame

    def create_menuBar(self, frame):
        menuBar = tk.Menu(frame)
        fileMenu = tk.Menu(menuBar, tearoff=0)
        fileMenu.add_command(label='Load Mav',command=self.spinup_mapDataSet)
        fileMenu.add_command(label='load map')
        menuBar.add_cascade(label='File', menu=fileMenu)
        editMenu = tk.Menu(menuBar, tearoff=0)
        menuBar.add_cascade(label='Edit', menu=editMenu)
        viewMenu = tk.Menu(menuBar, tearoff=0)
        menuBar.add_cascade(label='View', menu=viewMenu)
        frame.config(menu=menuBar)

    def create_mapControlWidgets(self, frame):
            
        self.selectTime_slider = tk.Scale(
                          frame,orient=tk.HORIZONTAL,command=self.mapTimeSlider_released)
        self.respDropdown=ttk.Combobox(frame,width=27,state="readonly")
        self.respDropdown.bind("<<ComboboxSelected>>",self.mapDropdown_changed)
        self.respDropdown.grid(row=1,column=2)       
        self.selectTime_slider.grid(row=1, column=1)
        
    def create_mapDataView(self,frame):
        self.dataBox=tk.Text(frame)
        self.dataBox.grid(row=0,column=0)
        self.dataBox.config(state=tk.NORMAL)
        self.dataBox.delete('1.0')
    
    def create_mapCavas(self, frame):
        canvas = FigureCanvasTkAgg(self.fig, master=frame)
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH,
                                    expand=True)
        toolbar = NavigationToolbar2Tk(canvas, frame)
        toolbar.update()
        return canvas

    def place_frames(self, plotFrame, controlFrame,dataFrame):
            controlFrame.grid(row=0, column=0,sticky=tk.W + tk.E)
            plotFrame.grid(row=1, column=0, columnspan=3,
                        sticky=tk.W + tk.E + tk.N + tk.S)
            dataFrame.grid(row=0,column=4,rowspan=3)



# end gui objects************************************************************
# start gui object direct calls(one per)
    def spinup_mapDataSet(self):
        cwd=os.getcwd()
        dataFile=tk.filedialog.askopenfilename(initialdir=cwd)
        
        self.model.read_mav_coords(dataFile,'coords.json')
        self.responses=self.model.get_responses()
        self.model.create_cellPatches()
        
        self.model.plot_cellPatches()
        self.mapConfigure_plot()
        self.model.create_legend()
        self.mapConfigure_widgets()
        
        self.dropdownIndex=int(self.respDropdown.current())
        self.model.find_max(self.dropdownIndex) # replace with process data or something
        time=self.selectTime_slider.get()
        self.model.update_cellPatches(0,time)
        self.model.colorize_cellPatches(self.dropdownIndex)
        self.canvas.draw()
         
    def import_data(self):
        pass
    def mapTimeSlider_released(self,event):  
        time=self.selectTime_slider.get()
        self.model.update_cellPatches(0,time)
        self.model.colorize_cellPatches(self.dropdownIndex)
        self.canvas.draw()
    
    def mapDropdown_changed(self,event):
        #print("changed to ", self.respDropdown.current())
        
        self.dropdownIndex=int(self.respDropdown.current())
        self.model.colorize_cellPatches(self.dropdownIndex)
        self.canvas.draw()

    def mapMouse_moved(self,event):
       self.mapDetect_cellChange(event)
# end gui object direct calls(one per)**********************************************

# start supporting functions************************************************
    def mapDetect_cellChange(self,event):
        if event.inaxes==self.ax:
            mouse_in_cell=self.model.is_point_in_cell(event.xdata,event.ydata,self.curr_cellPatch)
            if mouse_in_cell==False:
                self.curr_cellPatch,found=self.model.determine_cell_from_point(event.xdata,event.ydata)

                if found:
                    print("changed to cell : ", self.curr_cellPatch.get_cell())
                    self.mapWrite_dataBox()

                else:
                    # return 0;
                    print("outside grid")
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
        self.ax.set_xlim(110,122)
        self.ax.set_ylim(20,27.5)

    def mapConfigure_widgets(self):
        # configure timeSlider passed on input data
        range,stepsPerday=self.model.get_timeParams()
        timeSliderRes=1/stepsPerday
        self.selectTime_slider.config(resolution=timeSliderRes,from_=range[0],to=range[1],digits=4)

        # configure target/response dropdown
        responses=self.responses
        self.respList=list(responses[0])
        print(responses)
        self.respDropdown.config(values=self.respList)
        self.respDropdown.set(self.respList[0])
        # configure databox widget
        self.dataBox.config(width=35) 
        self.fig.canvas.mpl_connect("motion_notify_event",self.mapMouse_moved)

        

# end widget/plotconfigure methods******************************************************
# start main
def main():
    root = tk.Tk()
    style = ThemedStyle(root)
    style.theme_use("arc")
    model=Model()
    maingui=View(root,model)
    root.mainloop()
    #root.protocol("WM_DELETE_WINDOW", destroyer)
    root.destroy()


if __name__ == "__main__":
    main()
