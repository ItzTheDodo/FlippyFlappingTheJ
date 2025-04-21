# FlippyFlappingTheJ
# ./src/utils/TkUtils/PlaceholderEntry.py

import tkinter as ttk


class PlaceholderEntry(ttk.Entry):
    """
    Custom tkinter Entry object

    @params container = master, placeholder = "example", args = tkinter object args, kwargs = tkinter object kwargs

    - container: the main tkinter window object that the Entry will be on

    - placeholder: the string placeholder that will be placed in the Entry on initialisation

    - args: the normal tkinter Entry args

    - kwargs: the normal tkinter Entry key-word-args

    # note: this object supports custom styles ((in kwargs) style="TEntry", placeholder_style="Placeholder.TEntry"
    """

    def __init__(self, container, placeholder, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.placeholder = placeholder

        self.insert("0", self.placeholder)
        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._add_placeholder)

    def _clear_placeholder(self, e):
        self.delete("0", "end")

    def _add_placeholder(self, e):
        if not self.get():
            self.insert("0", self.placeholder)
