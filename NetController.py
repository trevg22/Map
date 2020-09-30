#Map Viewer
#NetController.py
#Controller class for the network tool

from netModel import NetModel
class NetController:

    def __init__(self):
        self.model=NetModel()

    def point_clicked(self,frame,event):
      
        if event.name is "pick_event":
            pass
    
        else:
            x=event.xdata
            y=event.ydata

            frame.plot_point(x,y,marker='.')
            frame.draw_canvas()
        
