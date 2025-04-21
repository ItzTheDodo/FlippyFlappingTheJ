# FlippyFlappingTheJ
# ./src/utils/TkUtils/RoundedButton.py

import tkinter as ttk
from tkinter import font as ttk_font
from typing import Callable, Optional, Self


class RBTagCounter:  # Singleton counter for round button tags

    _instance: Optional[Self] = None
    _count: int = -1

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def next_tag(self):
        self._count += 1
        return self._count


class RoundedButton(ttk.Widget):
    """
    Widget used to create a rounded button in a tk window

    ...


    Attributes
    ----------
    master -> ttk.Tk | ttk.Toplevel:
        The parent Tkinter window.
    canvas -> ttk.Canvas:
        The canvas where the button will be drawn.
    x -> int:
        The x-coordinate of the button.
    y -> int:
        The y-coordinate of the button.
    text -> str:
        The text displayed on the button.
    command -> Callable[..., None]:
        The function to be executed when the button is clicked.
    radius -> int:
        The radius of the button's rounded corners (default: 25).
    padding -> int:
        Padding around the text inside the button (default: 25).
    text_font -> ttk_font.Font:
        The font of the button text (default: None).
    fill -> str:
        The background color of the button (default: "grey").
    outline -> str:
        The outline color of the button (default: "").
    outline_width -> int:
        The width of the button's outline (default: 1).
    text_colour -> str:
        The color of the button text (default: "#fff").
    hover_colour -> str:
        the colour of the button when hovered over (default: None).
    click_colour -> str:
        the colour of the button when clicked (default: None).
    width -> int:
        defines a preset width (default: None).
    """

    def __init__(self, master: ttk.Tk | ttk.Toplevel, canvas: ttk.Canvas, x: int, y: int, text: str,
                 command: Callable[..., None],
                 radius: int = 25, padding: int = 25, text_font: ttk_font.Font = None, fill: str = "grey",
                 outline: str = "", outline_width: int = 1, text_colour: str = "#fff",
                 hover_colour: None | str = None, click_colour: None | str = None, width: None | int = None,
                 *args, **kwargs):
        super().__init__(master, "button", *args, **kwargs)

        self._master_root = master
        self._cv = canvas
        self._x = x
        self._y = y
        self._radius = radius
        self._text = text
        self._command = command
        self._padding = padding
        self._font = text_font
        self._fill = fill
        self._outline = outline
        self._text_colour = text_colour
        self._outline_width = outline_width
        self._hover_colour = hover_colour
        self._click_colour = click_colour
        self._width = width

        self._tag = f"round_button_uuid_{RBTagCounter().next_tag()}"
        self.render()

    def render(self):
        self._cv.delete(self._tag)
        text = self._cv.create_text(self._x + self._padding, self._y + self._padding, text=self._text, font=self._font,
                                    anchor=ttk.NW, fill=self._text_colour, tags=(self._tag, self._tag + "_text"))
        text_bbox = self._cv.bbox(text)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        if self._width:
            self.round_rectangle(self._cv, self._x, self._y,
                                 self._x + self._width,
                                 self._y + text_height + self._padding * 2, self._radius, fill=self._fill,
                                 outline=self._outline, tags=(self._tag, self._tag + "_bg"), width=self._outline_width)
            self._cv.moveto(text, self._x + ((self._width - text_width) / 2), self._y + self._padding)
        else:
            self.round_rectangle(self._cv, self._x, self._y,
                                 self._x + text_width + self._padding * 2,
                                 self._y + text_height + self._padding * 2, self._radius, fill=self._fill,
                                 outline=self._outline, tags=(self._tag, self._tag + "_bg"), width=self._outline_width)
        self._cv.tag_raise(self._tag + "_text")

        self._cv.tag_bind(self._tag, "<Button-1>", self._on_click)
        self._cv.tag_bind(self._tag, "<ButtonRelease>", self._on_release)
        self._cv.tag_bind(self._tag, "<Enter>", lambda e: self._on_hover())
        self._cv.tag_bind(self._tag, "<Leave>", lambda e: self._on_no_hover())

    def _on_hover(self):
        self._cv.config(cursor="hand2")
        if self._hover_colour:
            self._cv.itemconfigure(self._tag + "_bg", fill=self._hover_colour)

    def _on_no_hover(self):
        self._cv.config(cursor=self._master_root["cursor"])
        self._cv.itemconfigure(self._tag + "_bg", fill=self._fill)

    def _on_click(self, e):
        if self._click_colour:
            self._cv.itemconfigure(self._tag + "_bg", fill=self._click_colour)
        self._command(e)

    def _on_release(self, _):
        self._cv.itemconfigure(self._tag + "_bg", fill=self._fill)

    @staticmethod
    def round_rectangle(cv, x1, y1, x2, y2, radius=25, **kwargs):
        """
        Renders a rectangle with rounded corners on a tk canvas
        """
        points = [x1 + radius, y1,
                  x1 + radius, y1,
                  x2 - radius, y1,
                  x2 - radius, y1,
                  x2, y1,
                  x2, y1 + radius,
                  x2, y1 + radius,
                  x2, y2 - radius,
                  x2, y2 - radius,
                  x2, y2,
                  x2 - radius, y2,
                  x2 - radius, y2,
                  x1 + radius, y2,
                  x1 + radius, y2,
                  x1, y2,
                  x1, y2 - radius,
                  x1, y2 - radius,
                  x1, y1 + radius,
                  x1, y1 + radius,
                  x1, y1]
        return cv.create_polygon(points, **kwargs, smooth=True)

    @property
    def master_root(self) -> ttk.Tk | ttk.Toplevel:
        return self._master_root

    @property
    def master_canvas(self) -> ttk.Canvas:
        return self._cv

    @property
    def x(self) -> int:
        return self._x

    @x.setter
    def x(self, value: int):
        self._x = value
        self.render()

    @property
    def y(self) -> int:
        return self._y

    @y.setter
    def y(self, value: int):
        self._y = value
        self.render()

    @property
    def radius(self) -> int:
        return self._radius

    @radius.setter
    def radius(self, value: int):
        self._radius = value
        self.render()

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, text: str):
        self._text = text
        self.render()

    @property
    def command(self) -> Callable[..., None]:
        return self._command

    @command.setter
    def command(self, command: Callable[..., None]):
        self._command = command
        self.render()

    @property
    def padding(self) -> int:
        return self._padding

    @padding.setter
    def padding(self, value: int):
        self._padding = value
        self.render()

    @property
    def font(self) -> ttk_font.Font:
        return self._font

    @font.setter
    def font(self, value: ttk_font.Font):
        self._font = value
        self.render()

    @property
    def fill(self) -> str:
        return self._fill

    @fill.setter
    def fill(self, value: str):
        self._fill = value

    @property
    def outline(self) -> str:
        return self._outline

    @outline.setter
    def outline(self, value: str):
        self._outline = value
        self.render()

    @property
    def text_colour(self) -> str:
        return self._text_colour

    @text_colour.setter
    def text_colour(self, value: str):
        self._text_colour = value
        self.render()

    @property
    def outline_width(self) -> int:
        return self._outline_width

    @outline_width.setter
    def outline_width(self, value: int):
        self._outline_width = value

    @property
    def tag(self) -> str:
        return self._tag

    @property
    def hover_colour(self) -> str:
        return self._hover_colour

    @hover_colour.setter
    def hover_colour(self, value: str):
        self._hover_colour = value

    @property
    def click_colour(self) -> str:
        return self._click_colour

    @click_colour.setter
    def click_colour(self, value: str):
        self._click_colour = value

    @property
    def width(self) -> int:
        return self._width

    @width.setter
    def width(self, value: int):
        self._width = value
