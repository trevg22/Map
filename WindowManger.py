import tkinter as tk
from tkinter import ttk

# Grid window manager
# Accepts ttk.frame child objects with init_frames method


class WindowManager:
    def __init__(self, inc_frame, view):
        self.parentFrame = inc_frame
        self.frameList = []
        self.maxCols = 3
        self.numFrames = 0
        self.view = view
        # self.parentFrame.rowconfigure(0, weight=1)
        # self.parentFrame.columnconfigure(0, weight=1)

    # Add frame to the windowmanager and grid
    def add_frame(self, frame, mode=None, init=True):

        if mode is None or mode is "grid":
            wmFrame = ttk.Frame(self.parentFrame)
            # style=ttk.Style()
            # style.configure('TFrame',background='green')
            wmFrame.rowconfigure(0, weight=1)
            wmFrame.columnconfigure(0, weight=1)
            self.place_frame(wmFrame)
            quitButton = ttk.Button(wmFrame, text='x', width=3,
                            command=lambda: self.delete_frame(wmFrame))
            quitButton.grid(row=0, column=1, sticky=tk.N+tk.E)

        elif mode is "floating":
            wmFrame = tk.Toplevel(self.parentFrame)
        self.frameList.append(wmFrame)
        if init == True:
            frame.init_frames(wmFrame)
        # frame.columnconfigure(0, weight=1)
        # frame.rowconfigure(0, weight=1)
        frame.grid(row=0, column=0, sticky=tk.N+tk.E+tk.W+tk.S)

       # Place frame in the grid

    def place_frame(self, frame):
        self.numFrames += 1
        frameRow = int((self.numFrames-1)/self.maxCols)
        frameCol = (self.numFrames-1) % self.maxCols
        frame.grid(row=frameRow, column=frameCol, sticky=tk.N+tk.E+tk.S+tk.W)

    # destroy frame and remove frame
    # repack remaining frames
    def delete_frame(self, frame):
        self.frameList.remove(frame)
        self.view.remove_frame(frame)
        frame.destroy()
        self.repack_frames()

    # place frames still in self.frameList into grid
    def repack_frames(self):
        self.numFrames = 0
        for frame in self.frameList:
            frame.grid_forget()

        for frame in self.frameList:
            self.place_frame(frame)
