# FlippyFlappingTheJ
# ./src/utils/TkUtils/TransparentButton.py

import tkinter as ttk
from tkinter import font as ttk_font
from typing import Optional, Self, Callable
from PIL import Image, ImageTk


class TBTagCounter:  # Singleton counter for transparent button tags

    _instance: Optional[Self] = None
    _count: int = -1

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def next_tag(self):
        self._count += 1
        return self._count


class TBCompound:  # Enum for compound setting of TransparentButton
    LEFT, RIGHT, ABOVE, BELOW, CENTER = range(5)


class TransparentButton(ttk.Widget):
    """
    Widget used to create a transparent button in a tk window

    the TransparentButton class leverages the flexibility of the Canvas widget and the PIL library
    to create customizable buttons with transparent backgrounds,
    supporting various text and image configurations and interactive behaviors.

    ...

    Attributes
    ----------


    """

    TRANSPARENT_IMAGES: dict[str: ImageTk.PhotoImage] = {}  # to avoid garbage collection

    def __init__(self, master: ttk.Tk | ttk.Toplevel, canvas: ttk.Canvas, x: int, y: int, command: Callable[..., None],
                 text: str = "", image: ttk.PhotoImage | None = None,
                 padding: int = 25, text_font: ttk_font.Font | tuple = None,
                 outline: str = "", outline_width: int = 1, text_colour: str = "#fff",
                 hover_colour: None | str = None, click_colour: None | str = None,
                 compound: TBCompound = 0, sep: int = 5, centre_offset: int = 0, *args, **kwargs):
        super().__init__(master, "button", *args, **kwargs)

        self._master_root = master
        self._cv = canvas
        self._x = x
        self._y = y
        self._image = image
        self._text = str(text)
        self._command = command
        self._padding = padding
        self._font = text_font
        self._outline = outline
        self._text_colour = text_colour
        self._outline_width = outline_width
        self._hover_colour = hover_colour
        self._click_colour = click_colour
        self._compound = compound
        self._sep = sep
        self._centre_offset = centre_offset

        self._bbox: tuple[int, int, int, int] = (0, 0, 0, 0)

        self._tag = f"transparent_button_uuid_{TBTagCounter().next_tag()}"
        self.render()

    def transparent_rectangle(self, cv: ttk.Canvas, x: int, y: int, a: int, b: int, alpha: int = 0, fill: str = "#fff",
                              tags: tuple | None = None, **options) -> tuple:
        alpha_channel = int(alpha * 255)
        fill_channel = cv.winfo_rgb(fill) + (alpha_channel,)

        image = Image.new("RGBA", (a, b), fill_channel)
        TransparentButton.TRANSPARENT_IMAGES[self.tag] = ImageTk.PhotoImage(image)
        return (cv.create_image(x, y, image=TransparentButton.TRANSPARENT_IMAGES[self.tag], anchor=ttk.NW),
                cv.create_rectangle(x, y, a + x, b + y, tags=tags, **options))

    def delete(self):
        del TransparentButton.TRANSPARENT_IMAGES[self.tag]
        self._cv.delete(self.tag)
        del self

    def render(self):
        self._cv.delete(self._tag)

        text = self._cv.create_text(0, 0, text=self._text, font=self._font, anchor=ttk.NW, fill=self._text_colour,
                                    tags=(self._tag, self._tag + "_text"))
        text_bbox = self._cv.bbox(text)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        image = self._cv.create_image(0, 0, anchor=ttk.NW, image=self._image,
                                      tags=(self._tag, self._tag + "_image"))
        image_bbox = self._cv.bbox(image)
        image_width = image_bbox[2] - image_bbox[0]
        image_height = image_bbox[3] - image_bbox[1]

        button_width: int = max(text_width, image_width) + 2 * self._padding + self._sep
        button_height: int = max(text_height, image_height) + 2 * self._padding + self._sep

        if self._compound == TBCompound.LEFT:
            self._cv.moveto(text, self._x + self._padding, self._y + ((button_height - text_height) / 2))
            self._cv.moveto(image, self._x + self._padding + text_width + self._sep,
                            self._y + ((button_height - image_height) / 2))
            button_width = self._sep + 2 * self._padding + text_width + image_width
        elif self._compound == TBCompound.RIGHT:
            self._cv.moveto(text, self._x + self._padding + image_width + self._sep,
                            self._y + ((button_height - text_height) / 2))
            self._cv.moveto(image, self._x + self._padding,
                            self._y + ((button_height - image_height) / 2))
            button_width = self._sep + 2 * self._padding + text_width + image_width
        elif self._compound == TBCompound.ABOVE:
            self._cv.moveto(text, self._x + ((button_width - text_width) / 2), self._y + self._padding)
            self._cv.moveto(image, self._x + ((button_width - image_width) / 2),
                            self._y + self._padding + text_height + self._sep)
            button_height = self._sep + 2 * self._padding + image_height + text_height
        elif self._compound == TBCompound.BELOW:
            self._cv.moveto(text, self._x + ((button_width - text_width) / 2),
                            self._y + self._padding + image_height + self._sep)
            self._cv.moveto(image, self._x + ((button_width - image_width) / 2),
                            self._y + self._padding)
            button_height = self._sep + 2 * self._padding + image_height + text_height
        elif self._compound == TBCompound.CENTER:
            self._cv.moveto(text, self._x + ((button_width - text_width) / 2) + self._centre_offset,
                            self._y + ((button_height - text_height) / 2))
            self._cv.moveto(image, self._x + ((button_width - image_width) / 2),
                            self._y + ((button_height - image_height) / 2))
        else:
            raise ValueError(f"Compound argument invalid: {self._compound}")

        self.transparent_rectangle(self._cv, self._x, self._y, button_width, button_height, alpha=0,
                                   tags=(self._tag, self._tag + "_bg"), outline=self._outline,
                                   width=self._outline_width)

        self._bbox = (self._x, self._y, self._x + button_width, self._y + button_height)

        self._cv.tag_raise(self._tag + "_text")
        self._cv.tag_raise(self._tag + "_image")

        self._cv.tag_bind(self._tag, "<Button-1>", self._on_click)
        self._cv.tag_bind(self._tag, "<ButtonRelease>", self._on_release)
        self._cv.tag_bind(self._tag, "<Enter>", lambda e: self._on_hover())
        self._cv.tag_bind(self._tag, "<Leave>", lambda e: self._on_no_hover())

    def _on_hover(self):
        self._cv.config(cursor="hand2")
        if self._hover_colour:
            self._cv.itemconfigure(self._tag + "_bg", outline=self._hover_colour)

    def _on_no_hover(self):
        self._cv.config(cursor=self._master_root["cursor"])
        self._cv.itemconfigure(self._tag + "_bg", outline=self._outline)

    def _on_click(self, e):
        if self._click_colour:
            self._cv.itemconfigure(self._tag + "_bg", outline=self._click_colour)
        self._command(e)

    def _on_release(self, _):
        self._cv.itemconfigure(self._tag + "_bg", outline=self._outline)

    def moveto(self, x: int, y: int):
        self._x = x
        self._y = y
        self.render()

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
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, text: str):
        self._text = text
        self.render()

    @property
    def image(self) -> ttk.PhotoImage:
        return self._image

    @image.setter
    def image(self, image: ttk.PhotoImage):
        self._image = image
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
    def compound(self) -> TBCompound:
        return self._compound

    @compound.setter
    def compound(self, comp: TBCompound):
        self._compound = comp
        self.render()

    @property
    def sep(self) -> int:
        return self._sep

    @sep.setter
    def sep(self, sep: int):
        self._sep = sep
        self.render()

    @property
    def centre_offset(self) -> int:
        return self._centre_offset

    @centre_offset.setter
    def centre_offset(self, co: int):
        self._centre_offset = co
        self.render()

    @property
    def bbox(self) -> tuple[int, int, int, int]:
        return self._bbox
