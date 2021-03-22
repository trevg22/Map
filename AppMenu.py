#Map Viewer
#AppMenu.py
#Main Window Dropdown Menus
import wx


class AppMenu():

    def __init__(self,parent,view):
        self.view=view
        menuBar=wx.MenuBar()
        fileMenu=wx.Menu()
        loadMav=fileMenu.Append(wx.ID_ANY,"Load Mav","Load the Mav file")
        spawnData=fileMenu.Append(wx.ID_ANY,"Spawn View","Spawn the data view")
        spawnMap=fileMenu.Append(wx.ID_ANY,"Spawn Map","Spawn a new map panel")
        menuBar.Append(fileMenu,'&File')

        parent.Bind(wx.EVT_MENU,lambda event:self.view.spinup_mapDataSet(event),loadMav)
        parent.Bind(wx.EVT_MENU,lambda event: self.view.spawn_dataPanel(event),spawnData)
        parent.Bind(wx.EVT_MENU,lambda event:self.view.spawn_mapPanel(event),spawnMap)

        parent.SetMenuBar(menuBar)
