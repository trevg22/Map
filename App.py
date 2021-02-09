# Map Viewer
# App.py
# Main Appliction class
import tkinter as tk
from tkinter import ttk
import wx
from MapFrame import MapParentFrame
from WxView import View
from WindowManger import WindowManager


def main():
    app = wx.App()
    view = View()
    view.init_mainWindow()

    app.MainLoop()


if __name__ == "__main__":
    main()
