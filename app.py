from os import path
import sys  # these 2 are required to find the correct paths for pyinstaller
import tkinter as tk
from tkinter import ttk
from frames import Snake

DARK_BACKGROUND = '#0F0F0F'
LIGHT_TEXT = '#FFFFFF'

class Board(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title('Snake Game')
        self.geometry('600x620')
        self.resizable(False, False)
        # scale the widgets to better accommodate high DPI displays
        # more info: https://www.tcl.tk/man/tcl8.6/TkCmd/tk.htm#M10
        self.tk.call("tk", "scaling", 4.0)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        style = ttk.Style(self)
        style.theme_use('clam')

        style.configure(
            'MessageFrame.TFrame',
            background=DARK_BACKGROUND
        )

        style.configure(
            'MessageLabel.TLabel',
            background=DARK_BACKGROUND,
            foreground=LIGHT_TEXT,
            font='Arial 30'
        )

        # sys will tell the system where this bundle is
        # the 3rd element is for, when it failed to find the bundle, there's a default as an alternative
        # path.abspath: absolute path
        # __file__: the current file that we're running
        self.bundle_dir = getattr(sys, "_MEIPASS", path.abspath(path.dirname(__file__)))

        self.message = tk.StringVar(value='This is a snake game.\nPress ENTER to start.')

        self.message_frame = ttk.Frame(
            self,
            style='MessageFrame.TFrame'
        )

        self.message_label = ttk.Label(
            self.message_frame,
            textvariable=self.message,
            style='MessageLabel.TLabel'
        )
        self.message_label.pack(expand=True, fill='none')  # place label in the middle

        self.show_message()

    def show_message(self):
        self.message_frame.grid(row=0, column=0, sticky='NSEW')
        self.message_frame.focus()
        self.message_frame.bind("<Key>", self.start_game)

    def start_game(self, event):
        keyboard_input = event.keysym
        correct_input = ('Return', 'KP_Enter')
        if keyboard_input in correct_input:
            self.message_frame.unbind('<Key>')
            self.message_frame.grid_forget()
            self.snake_game = Snake(self)
            self.snake_game.grid(row=0, column=0, sticky='NSEW')

    def ask_restart(self, score):
        self.snake_game.grid_forget()
        self.message.set(f"Game over! You scored {score}!\nPress enter to try again.")
        self.show_message()


app = Board()

app.mainloop()
