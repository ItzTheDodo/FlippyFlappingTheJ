# FlippyFlappingTheJ
# ./src/utils/TkUtils/Tooltip.py

import tkinter as ttk


class ToolTip:
    """
    Custom tooltip object that can be bound to a tkinter widget

    ...


    Attributes
    ----------
    widget -> tkinter.Widget:
        The widget object to bind the tooltip to.
    offset -> tuple[int, int]:
        The x and y offset from the widget in tuple format (default: (60, 30)).
    kwargs -> dict:
        The standard Tkinter keyword arguments to format the tooltip (e.g., text, font).
    """

    def __init__(self, widget, offset, **kwargs):
        self.widget = widget
        self.tipwindow = None
        self.offset = offset
        self._kwargs = dict(kwargs)

        self.bind_tooltip()

    def setKwargs(self, val, key=None):
        if key:
            self._kwargs[key] = val
        else:
            self._kwargs = val

    def getKwargs(self, key=None):
        return self._kwargs[key] if key else self._kwargs

    def bind_tooltip(self, widget=None):
        if widget is not None:
            self.widget = widget
        self.widget.bind("<Enter>", self.showtip)
        self.widget.bind("<Leave>", self.hidetip)

    def unbind_tooltip(self, widget):
        if widget is not None:
            self.widget = widget
        self.widget.unbind("<Enter>")
        self.widget.unbind("<Leave>")

    def showtip(self, _):
        if self.tipwindow:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + self.offset[0]
        y += cy + self.widget.winfo_rooty() + self.offset[1]
        self.tipwindow = ttk.Toplevel(self.widget)
        self.tipwindow.wm_overrideredirect(True)
        self.tipwindow.wm_geometry("+%d+%d" % (x, y))
        label = ttk.Label(self.tipwindow, **self._kwargs)
        label.pack(ipadx=1)

    def hidetip(self, _):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()
