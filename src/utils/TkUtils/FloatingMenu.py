# FlippyFlappingTheJ
# ./src/utils/TkUtils/FloatingMenu.py

import tkinter as ttk
from collections.abc import Callable


class CustomMenu(ttk.Widget):

    def __init__(self, master: ttk.Tk | ttk.Toplevel, *args, offset: tuple[int, int] = (-5, -5),
                 rel: ttk.Widget | None = None, spacing: int = 5, padding: int = 25, **kwargs):
        super().__init__(master, "menu")

        self._master = master

        self._menu_args = args
        self._menu_kwargs = kwargs

        self._rel = rel
        self._offset = offset
        self._spacing = spacing
        self._padding = padding

        self._assets: list[list[Callable[..., ttk.Widget] | tuple | dict]] = []
        self._menu_window: ttk.Toplevel | None = None
        self._menu_screen: ttk.Canvas | None = None

        self._on_render_events: list[Callable[..., None]] = []

    def add_widget(self, widget: Callable[..., ttk.Widget], order: int = 0, *args, **kwargs):
        self._assets.insert(order, [widget, args, kwargs])

    def bind_on_render(self, cmd: Callable[..., None]):
        self._on_render_events.append(cmd)

    def show_menu(self, e: ttk.Event):
        if self._menu_window is not None:
            return

        win_x_pos = e.x_root + self._offset[0]
        win_y_pos = e.y_root + self._offset[1]

        self._menu_window = ttk.Toplevel(self._master)
        self._menu_window.wm_overrideredirect(True)
        self._menu_screen = ttk.Canvas(self._menu_window, *self._menu_args, width=50, height=50, **self._menu_kwargs)
        self._menu_screen.pack(side='top', fill='both', expand=1)

        current_y: int = self._padding - self._spacing
        current_x: int = 0
        asset_ids: list[int] = []
        for asset in self._assets:
            asset_obj: ttk.Widget = asset[0](self._menu_window, *asset[1], **asset[2])
            cur_widget = self._menu_screen.create_window((0, 0), window=asset_obj, anchor=ttk.NW)
            cur_widget_bbox = self._menu_screen.bbox(cur_widget)
            cur_widget_width = cur_widget_bbox[2] - cur_widget_bbox[0]
            cur_widget_height = cur_widget_bbox[3] - cur_widget_bbox[1]

            # cur_widget_x = max(self._padding, int((current_x - cur_widget_width) / 2) - self._padding)
            current_x = max(current_x, cur_widget_width + 2 * self._padding)

            cur_widget_y = current_y + self._spacing
            current_y += self._spacing + cur_widget_height

            self._menu_screen.moveto(cur_widget, 0, cur_widget_y)
            asset_ids.append(cur_widget)

        current_y += self._padding

        for asset_id in asset_ids:
            cur_widget_bbox = self._menu_screen.bbox(asset_id)
            cur_widget_width = cur_widget_bbox[2] - cur_widget_bbox[0]
            self._menu_screen.moveto(asset_id, (current_x - cur_widget_width) / 2, cur_widget_bbox[1])

        for cmd in self._on_render_events:
            cmd(self._menu_screen)

        self._menu_window.wm_geometry("%sx%s+%d+%d" % (current_x, current_y, win_x_pos, win_y_pos))
        self._menu_window.focus()
        self._menu_window.bind("<FocusOut>", self.hide_window)

    def hide_window(self, _):
        if self._menu_window is None:
            return
        self._menu_window.destroy()

        self._menu_window = None
        self._menu_screen = None

    @property
    def menu_args(self) -> tuple:
        return self._menu_args

    @property
    def menu_kwargs(self) -> dict:
        return self._menu_kwargs

    @property
    def rel(self) -> ttk.Widget | None:
        return self._rel

    @property
    def offset(self) -> tuple[int, int]:
        return self._offset

    @property
    def spacing(self) -> int:
        return self._spacing

    @property
    def padding(self) -> int:
        return self._padding

    @property
    def assets(self) -> list[list[Callable[..., ttk.Widget] | tuple | dict]]:
        return self._assets

    @property
    def menu_window(self) -> ttk.Toplevel | None:
        return self._menu_window

    @property
    def menu_screen(self) -> ttk.Canvas | None:
        return self._menu_screen

    @property
    def on_render_events(self) -> list[Callable[..., None]]:
        return self._on_render_events
