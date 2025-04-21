# FlippyFlappingTheJ
# ./src/utils/TkUtils/DragAndDrop.py

import tkinter as ttk
from typing import Callable, Literal, Optional, Self

from src.utils.TkUtils.RoundedButton import RoundedButton
from src.utils.TkUtils.TransparentButton import TransparentButton


class DDRenderable:
    """
    Class used as primitive type of renderable drag and drop object for encapsulation
    (Note: see implementation in DragAndDropWidget or DragAndDropRoundedButton for more docs on custom ddrenderable)
    """

    def __init__(self, render_command: Callable[..., None], final_render_command: Callable[..., None]):
        self._render_command = render_command
        self._final_render_command = final_render_command

    @property
    def dd_render(self) -> Callable[..., None]:
        return self._render_command

    @property
    def final_render(self) -> Callable[..., None]:
        return self._final_render_command


class DragAndDropWidget(ttk.Widget, DDRenderable):  # Primitive type should not be used
    """
    Class used as primitive type for DragAndDrop* (e.g. DragAndDropButton)
    (Note: should not be used directly reference implementation of DragAndDropRoundedButton)
    """

    def __init__(self, parent: ttk.Canvas, wn: str, render_command: Callable[..., None],
                 final_render_command: Callable[..., None],
                 *args, **kwargs):
        ttk.Widget.__init__(self, parent, wn, *args, **kwargs)
        DDRenderable.__init__(self, render_command, final_render_command)


class DragAndDropRoundedButton(RoundedButton, DDRenderable):

    def __init__(self, root: ttk.Tk | ttk.Toplevel, parent: ttk.Canvas, final_render_command: Callable[..., None],
                 *args, drag_text: str = "", drag_image: ttk.PhotoImage = None, **kwargs):
        RoundedButton.__init__(self, root, parent, *args, **kwargs)
        DDRenderable.__init__(self, lambda c, n1, n2, s, *a: None, final_render_command)

        self._drag_text = drag_text
        self._drag_image = drag_image

        self._cur_obj: ttk.Widget | None = None

    @property
    def dd_render(self) -> Callable[..., None]:
        return lambda c, n1, n2, _, dropped, *args, **kwargs: self._render_abs(c, n1, n2, dropped, *args, **kwargs)

    def _render_abs(self, _, x: int, y: int, dropped: bool, *args, **kwargs):
        if self._cur_obj:
            self._cur_obj.destroy()
        if dropped:
            self._cur_obj = None
            return
        if self._drag_image:
            self._cur_obj = ttk.Label(self.master_root, image=self._drag_image, *args, **kwargs)
        else:
            self._cur_obj = ttk.Label(self.master_root, text=self._drag_text, *args, **kwargs)
        self._cur_obj.place(x=x, y=y, anchor=ttk.CENTER)

    def bind(self, sequence: str | None = None,
             func: Callable[[ttk.Event], object] | None = None,
             add: Literal["", "+"] | bool | None = None) -> str:  # Bind function proxy since manager will call bind directly
        return self.master_canvas.tag_bind(self.tag, sequence, func, add)


class DragAndDropTransparentButton(TransparentButton, DDRenderable):

    def __init__(self, root: ttk.Tk | ttk.Toplevel, parent: ttk.Canvas, final_render_command: Callable[..., None],
                 *args, drag_text: str = "", drag_image: ttk.PhotoImage = None, disabled_func: Callable[..., bool] = None,
                 **kwargs):
        TransparentButton.__init__(self, root, parent, *args, **kwargs)
        DDRenderable.__init__(self, lambda c, n1, n2, s, *a: None, final_render_command)

        self._drag_text = drag_text
        self._drag_image = drag_image

        self._condition_func = disabled_func

        self._cur_obj: ttk.Widget | None = None

    @property
    def dd_render(self) -> Callable[..., None]:
        return lambda c, n1, n2, _, dropped, *args, **kwargs: self._render_abs(c, n1, n2, dropped, *args, **kwargs)

    def _render_abs(self, _, x: int, y: int, dropped: bool, *args, **kwargs):
        if self._condition_func is not None and not self._condition_func():
            return
        if self._cur_obj:
            self._cur_obj.destroy()
        if dropped:
            self._cur_obj = None
            return
        if self._drag_image:
            self._cur_obj = ttk.Label(self.master_root, image=self._drag_image, *args, **kwargs)
        else:
            self._cur_obj = ttk.Label(self.master_root, text=self._drag_text, *args, **kwargs)
        self._cur_obj.place(x=x, y=y, anchor=ttk.CENTER)

    def bind(self, sequence: str | None = None,
             func: Callable[[ttk.Event], object] | None = None,
             add: Literal[
                      "", "+"] | bool | None = None) -> str:  # Bind function proxy since manager will call bind directly
        return self.master_canvas.tag_bind(self.tag, sequence, func, add)


class DropZone(ttk.Canvas):
    """
    Class as extension of tkinter Canvas where items can be dropped
    (Note: see tkinter Canvas docs for canvas implementation)
    https://docs.python.org/3.12/library/tkinter.html#tkinter.Canvas

    Methods
    -------
    has_dropped(e: tkinter.Event, widget_dropped: type[DDRenderable, ttk.Widget]) -> None
        is called by the drag and drop manager with the drop event and widget being dropped, this method renders the
        widget as described in the DDRenderable final render callable
    """

    def __init__(self, parent: ttk.Widget, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

    def has_dropped(self, event: ttk.Event, widget_dropped: type[DDRenderable, ttk.Widget]):
        widget_dropped.final_render(event, self, widget_dropped)


class DMTagCounter:  # Singleton counter for drag manager tags

    _instance: Optional[Self] = None
    _count: int = -1

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def next_tag(self):
        self._count += 1
        return self._count


class DragManager:

    def __init__(self, root: ttk.Tk | ttk.Toplevel, master: ttk.Canvas):

        self._root = root
        self._master = master
        self._in_use: bool = False
        self._drop_tag: str = f"is_dragging_{DMTagCounter().next_tag()}"

    @property
    def root(self) -> ttk.Tk | ttk.Toplevel:
        return self._root

    @property
    def master(self) -> ttk.Canvas:
        return self._master

    @property
    def in_use(self) -> bool:
        return self._in_use

    @property
    def manager_tag(self) -> str:
        return self._drop_tag

    def attach_drag(self, widget: type[DDRenderable, ttk.Widget], *args, **kwargs):
        widget.bind("<Button-1>", self.on_drag, add="+")
        widget.bind("<B1-Motion>", lambda e: self.dragging(e, widget, *args, **kwargs), add="+")
        widget.bind("<ButtonRelease-1>", lambda e: self.on_drop(e, widget), add="+")
        widget.configure(cursor="hand1")

    def on_drag(self, _):
        if self._in_use:
            self._master.delete(self._drop_tag)
        self._in_use = True

    def dragging(self, event: ttk.Event, bound_widget: DDRenderable, *args, **kwargs):
        bound_widget.dd_render(self.master, event.x_root - self.root.winfo_x() - 10,
                               event.y_root - self.root.winfo_y() - 40, self.manager_tag, False, *args, **kwargs)

    def on_drop(self, event: ttk.Event, bound_widget: DDRenderable):
        x, y = event.widget.winfo_pointerxy()
        bound_widget.dd_render(self.master, event.x_root - self.root.winfo_x() - 10,
                               event.y_root - self.root.winfo_y() - 40, self.manager_tag, True)
        self._master.delete(self._drop_tag)
        self._in_use = False
        target = event.widget.winfo_containing(x, y)
        if not isinstance(target, DropZone):
            return
        target.has_dropped(event, bound_widget)
