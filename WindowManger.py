from tkinter import ttk
import tkinter as tk
# Grid window manager
# Accepts ttk.frame child objects with init_frames method


class WindowManager:
    def __init__(self, inc_frame, view):
        self.parentFrame = inc_frame
        self.frameList = []
        self.maxRows = 2
        self.maxCols = 2
        self.numFrames = 0
        self.view = view
        self.parentFrame.rowconfigure(0, weight=1)
        self.parentFrame.columnconfigure(0, weight=1)

    # Add frame to the windowmanager and grid
    def add_frame(self, frame):

        wmFrame = ttk.Frame(self.parentFrame)
        wmFrame.rowconfigure(0, weight=1)
        wmFrame.columnconfigure(0, weight=1)
        # Add 'x' button to outer frame owned by manager
        button = ttk.Button(wmFrame, text='x', width=3,
                            command=lambda: self.delete_frame(wmFrame))
        self.frameList.append(wmFrame)
        self.place_frame(wmFrame)
        button.grid(row=0, column=1, sticky=tk.N+tk.E)
        frame.init_frames(wmFrame)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
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
        print("frame deleted")
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

    # print widgets located inside manager parent frame
    def print_parentInfor(self):

        print("widgets in parent frame")
        for widget in self.parentFrame.winfo_children():
            print(widget)
            print(widget.winfo_x(), widget.winfo_y())
            print("parent", widget.winfo_parent())
