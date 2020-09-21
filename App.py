import tkinter as tk
from tkinter import ttk

from mapFrame import MapParentFrame
from View import View
from WindowManger import WindowManager


def main():
    parent = tk.Tk()
    parent.title("Impact Map Viewer 0.0.8")
    view = View()
    view.init_mainWindow(parent)

    parent.mainloop()


if __name__ == "__main__":
    main()
