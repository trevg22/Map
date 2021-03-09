# Map Viewer
# App.py
# Main Appliction class

import wx

from WxView import View


def main():
    app = wx.App()
    view = View()
    view.init_mainWindow()

    app.MainLoop()


if __name__ == "__main__":
    main()
