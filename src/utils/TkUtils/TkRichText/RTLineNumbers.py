# FlippyFlappingTheJ
# ./src/utils/TkUtils/TkRichText/RTLineNumbers.py

import tkinter as ttk

from src.utils.TkUtils.TkRichText.RichText import TkRichText


class TkTextLineNumbers(ttk.Canvas):

    def __init__(self, *args, textwidget=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.textwidget = textwidget
        if self.textwidget:
            self.attach(self.textwidget)

    def attach(self, text_widget):
        self.textwidget = text_widget
        if isinstance(self.textwidget, TkRichText):
            self.textwidget.register_on_change_callback(self.redraw)
            self.textwidget.register_on_scroll_callback(self.redraw)

    def redraw(self, *_):
        self.delete("all")

        if self.textwidget["state"] == "disabled":
            return

        i = self.textwidget.index("@0,0")
        while True:
            dline = self.textwidget.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.create_text(7, y, anchor="nw", text=linenum,
                             fill="white" if linenum == self.textwidget.index(ttk.INSERT).split(".")[0] else "#000",
                             font=("Bahnschrift", 9))
            i = self.textwidget.index("%s+1line" % i)
