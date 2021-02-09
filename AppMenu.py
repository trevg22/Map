import wx
class AppMenu():

    def __init__(self,parent,view):
        self.view=view
        menuBar=wx.MenuBar()
        fileMenu=wx.Menu()
        loadMav=fileMenu.Append(wx.ID_ANY,"Load Mav","blah")
        menuBar.Append(fileMenu,'&File')

        parent.Bind(wx.EVT_MENU,lambda event:self.view.spinup_mapDataSet(event),loadMav)

        parent.SetMenuBar(menuBar)
