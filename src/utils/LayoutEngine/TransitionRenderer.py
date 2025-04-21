# FlippyFlappingTheJ
# ./src/utils/LayoutEngine/TransitionRenderer.py

from __future__ import annotations

import tkinter as ttk
from tkinter import messagebox
from typing import Optional, Self
from functools import cache
from copy import deepcopy
import math

from src.utils.Automata.AutomataLink import AutomataLink
from src.utils.DataStruct.PriorityQueue import PriorityQueue
from src.utils.TkUtils.DragAndDrop import DropZone
from src.utils.TkUtils.TransparentButton import TransparentButton


class TDMTagCounter:  # Singleton counter for transition manager tags

    _instance: Optional[Self] = None
    _count: int = -1

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def next_tag(self):
        self._count += 1
        return self._count


class TransitionManager:

    def __init__(self, root, master: ttk.Canvas):

        self._root = root
        self._master = master
        self._in_use: bool = False
        self._drop_tag: str = f"is_dragging_{TDMTagCounter().next_tag()}"
        self._get_link_by_value: None | str = None

        self._registered_widgets: list[TransparentButton] = []
        self._registered_rendered_transitions: list[RenderedTransition] = []

    def clear(self):
        for transition in self._registered_rendered_transitions:
            transition.delete()
        self._registered_rendered_transitions = []
        self._registered_widgets = []

    @property
    def registered_rendered_transitions(self) -> list[RenderedTransition]:
        return self._registered_rendered_transitions

    def remove_drag(self, widget: TransparentButton):
        self._registered_widgets.remove(widget)
        new_transitions: list[RenderedTransition] = []
        for transition in self._registered_rendered_transitions:
            if transition.widget_from.text == widget.text or transition.widget_to.text == widget.text:
                transition.delete()
                continue
            new_transitions.append(transition)
        self._registered_rendered_transitions = new_transitions[:]

    def delete_transition(self, transition: RenderedTransition):
        delete_confirm = messagebox.askokcancel("Delete transition", "Are you sure you want to delete this transition?")
        if not delete_confirm:
            return
        transition.delete()
        self._registered_rendered_transitions.remove(transition)
        success, err_msg = self._root.current_automata.remove_transition(transition.link.id)
        if not success:
            messagebox.showerror("Internal Error occurred.", err_msg)
            raise Exception(f"Error removing transition: {err_msg}")

    def attach_drag(self, widget: TransparentButton, centre_offset_x: int = 0, centre_offset_y: int = 0,
                    radius: int = 50):
        self._master.tag_bind(widget.tag, "<Button-1>", self.on_drag, add="+")
        self._master.tag_bind(widget.tag, "<B1-Motion>", lambda e: self.dragging(e, widget, centre_offset_x, centre_offset_y, radius), add="+")
        self._master.tag_bind(widget.tag, "<ButtonRelease-1>", lambda e: self.on_drop(e, widget), add="+")
        self._master.bind("<Leave>", lambda e: self.on_drop(e, widget), add="+")
        self._master.bind("<MouseWheel>", lambda e: self.on_drop(e, widget), add="+")

        self._registered_widgets.append(widget)

    def on_drag(self, _):
        if not self._root.is_mouse_transition_mode():
            return
        if self._in_use:
            self._master.delete(self._drop_tag)
        self._in_use = True

    def dragging(self, event: ttk.Event, widget: TransparentButton, centre_offset_x: int, centre_offset_y: int,
                 radius: int):
        self._master.delete(self._drop_tag + "_line")
        if not self._root.is_mouse_transition_mode():
            return
        if not self._in_use:
            return
        mouse_x = event.x
        mouse_y = event.y

        bbox = widget.bbox
        widget_width = bbox[2] - bbox[0]
        widget_height = bbox[3] - bbox[1]

        centre_x = bbox[0] + (widget_width / 2) + centre_offset_x
        centre_y = bbox[1] + (widget_height / 2) + centre_offset_y

        dx = mouse_x - centre_x
        dy = centre_y - mouse_y

        distance = math.sqrt(dx ** 2 + dy ** 2)
        zoom_scaler = (self._root.drop_zone_zoom - 10) / (self._root.drop_zone_zoom - 12)
        radius *= zoom_scaler
        start_x = radius * (dx / distance) + centre_x
        start_y = radius * (-dy / distance) + centre_y

        self._master.create_line((start_x, start_y), (mouse_x, mouse_y), tags=self._drop_tag + "_line",
                                 arrow=ttk.LAST)

    def _get_button_under_point(self, x, y):
        for button in self._registered_widgets:
            bbox = button.bbox
            if bbox[0] <= x <= bbox[2] and bbox[1] <= y <= bbox[3]:
                return button
        return None

    def on_drop(self, event: ttk.Event, widget: TransparentButton):
        if not self._root.is_mouse_transition_mode():
            return
        if not self._in_use:
            return
        self._master.delete(self._drop_tag + "_line")
        x, y = event.widget.winfo_pointerxy()
        self._in_use = False
        target = event.widget.winfo_containing(x, y)
        if not isinstance(target, DropZone):
            return
        target_button = self._get_button_under_point(event.x, event.y)
        if target_button is None:
            return

        from_state_id = int(widget.text)
        to_state_id = int(target_button.text)
        if self._root.current_automata.exists_transition(from_state_id, to_state_id) is not None:
            messagebox.showerror("Existing transition", "There is already a transition there.")
            return

        # Calculate the midpoint between widget and target_button
        from_bbox = widget.bbox
        to_bbox = target_button.bbox

        from_x = (from_bbox[0] + from_bbox[2]) / 2
        from_y = (from_bbox[1] + from_bbox[3]) / 2
        to_x = (to_bbox[0] + to_bbox[2]) / 2
        to_y = (to_bbox[1] + to_bbox[3]) / 2

        mid_x = (from_x + to_x) / 2
        mid_y = (from_y + to_y) / 2

        link_by = self.get_link_by(mid_x, mid_y)
        success, transition = self._root.create_transition(from_state_id, to_state_id, link_by)
        if not success:
            return
        rendered_link = RenderedTransition(self._root, self._master, widget_from=widget, widget_to=target_button,
                                           transition=transition, radius1=50, radius2=50, manager=self)
        self._registered_rendered_transitions.append(rendered_link)
        self.update_transitions_for_state(from_state_id, widget)
        self.update_transitions_for_state(to_state_id, target_button)

    def _set_link_by(self, _, value: str | None, inp: ttk.Text = None):
        if value is not None:
            self._get_link_by_value = value
            return
        self._get_link_by_value = inp.get("1.0", ttk.END)

    def get_link_by(self, x: float, y: float, placeholder: str = "") -> list[str] | None:
        inp = ttk.Text(self._root, width=5, height=1)
        self._master.create_window(x, y, window=inp, anchor=ttk.CENTER, tags="link_by_enter")
        inp.insert("1.0", placeholder)
        inp.focus_set()
        inp.bind("<Return>", lambda e: self._set_link_by(e, None, inp=inp))
        mw_func_id = self._master.bind("<MouseWheel>", lambda e: self._set_link_by(e, None, inp=inp), add="+")
        b1_func_id = self._root.bind("<Button-1>", lambda e: self._set_link_by(e, None, inp=inp), add="+")
        while self._get_link_by_value is None:
            if not self._root.running:
                return
            self._root.update()
        link_by: str = self._get_link_by_value[:-1]
        self._get_link_by_value = None
        self._master.delete("link_by_enter")
        self._master.unbind("<MouseWheel>", mw_func_id)
        self._root.unbind("<Button-1>", b1_func_id)
        if link_by.isspace() or not link_by:
            return None
        links = list(map(str.strip, link_by.split(",")))
        for char in links:
            if len(char) > 1:
                messagebox.showerror("Argument Error.", f"Invalid character {char}")
                return None
        return links

    def create_new_transition(self, widget_from: TransparentButton, widget_to: TransparentButton,
                              link_by: str | list[str] | None = None) -> tuple[bool, str]:
        if widget_from not in self._registered_widgets:
            self._registered_widgets.append(widget_from)
        if widget_to not in self._registered_widgets:
            self._registered_widgets.append(widget_to)
        from_state_id = int(widget_from.text)
        to_state_id = int(widget_to.text)
        if self._root.current_automata.exists_transition(from_state_id, to_state_id) is not None:
            messagebox.showerror("Existing transition", "Error rendering automaton.")
            return False, "Error rendering automaton."
        success, transition = self._root.create_transition(from_state_id, to_state_id, link_by)
        if not success:
            return False, "Error creating transition."
        rendered_link = RenderedTransition(self._root, self._master, widget_from=widget_from, widget_to=widget_to,
                                           transition=transition, radius1=50, radius2=50, manager=self)
        self._registered_rendered_transitions.append(rendered_link)
        self.update_transitions_for_state(from_state_id, widget_from)
        self.update_transitions_for_state(to_state_id, widget_to)
        return True, ""

    def update_transitions_for_state(self, state_id: int, state_widget: TransparentButton):
        is_initial = self._root.current_automata.is_initial(state_id)
        for transition in self.registered_rendered_transitions:
            if transition.widget_from.text == state_widget.text:
                if is_initial:
                    transition.from_centre_offset_x = 12.5
                else:
                    transition.from_centre_offset_x = 0
            if transition.widget_to.text == state_widget.text:
                if is_initial:
                    transition.to_centre_offset_x = 12.5
                else:
                    transition.to_centre_offset_x = 0
            transition.render()

    def replace(self, widget1: TransparentButton, widget2: TransparentButton):
        for c, widget in enumerate(self._registered_widgets):
            if not widget == widget1:
                continue
            self._registered_widgets.pop(c)
            self._registered_widgets.insert(c, widget2)

        for transition in self._registered_rendered_transitions:
            if transition.widget_from.text == widget2.text:
                transition.widget_from = widget2
            if transition.widget_to.text == widget2.text:
                transition.widget_to = widget2

    def is_reverse_transition(self, transition: RenderedTransition) -> bool:
        from_state = transition.widget_from.text
        to_state = transition.widget_to.text

        for existing_transition in self._registered_rendered_transitions:
            if existing_transition == transition:
                break
            if (existing_transition.widget_from.text == to_state and
                    existing_transition.widget_to.text == from_state):
                return True
        return False


class RenderedTransitionTagCounter:  # Singleton counter for transition drag manager tags

    _instance: Optional[Self] = None
    _count: int = -1

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def next_tag(self):
        self._count += 1
        return self._count


class RenderedTransition:

    def __init__(self, master, canvas: ttk.Canvas, widget_from: tuple[int, int] | TransparentButton,
                 widget_to: tuple[int, int] | TransparentButton, transition: AutomataLink, manager: TransitionManager,
                 colour: str = "#000", directed: bool = True, from_centre_offset_x: float = 0, from_centre_offset_y: float = 0,
                 to_centre_offset_x: float = 0,  to_centre_offset_y: float = 0, radius1: int | None = None,
                 radius2: int | None = None, do_jump: bool = True, width: int = 2):

        self._master = master
        self._cv = canvas
        self._link = transition
        self._manager = manager
        self._widget_from = widget_from
        self._widget_to = widget_to
        self._colour = colour
        self._directed = directed
        self._from_centre_offset_x = from_centre_offset_x
        self._from_centre_offset_y = from_centre_offset_y
        self._to_centre_offset_x = to_centre_offset_x
        self._to_centre_offset_y = to_centre_offset_y
        self._radius1 = radius1
        self._radius2 = radius2
        self._do_jump = do_jump
        self._tag = f"rendered_transition_uuid_{RenderedTransitionTagCounter().next_tag()}"
        self._width = width

        self._from_xy: tuple[int, int] = (0, 0)
        self._to_xy: tuple[int, int] = (0, 0)

        self._is_straight: bool = True

        self.render()

    @property
    def is_straight(self) -> bool:
        return self._is_straight

    @property
    def widget_from(self) -> TransparentButton:
        return self._widget_from

    @widget_from.setter
    def widget_from(self, widget: TransparentButton):
        self._widget_from = widget

    @property
    def widget_to(self) -> TransparentButton:
        return self._widget_to

    @widget_to.setter
    def widget_to(self, widget: TransparentButton):
        self._widget_to = widget

    @property
    def from_xy(self) -> tuple[int, int]:
        return self._from_xy

    @property
    def to_xy(self) -> tuple[int, int]:
        return self._to_xy

    @property
    def colour(self) -> str:
        return self._colour

    @property
    def directed(self) -> bool:
        return self._directed

    @property
    def from_centre_offset_x(self) -> float:
        return self._from_centre_offset_x

    @from_centre_offset_x.setter
    def from_centre_offset_x(self, value: float):
        self._from_centre_offset_x = value

    @property
    def from_centre_offset_y(self) -> float:
        return self._from_centre_offset_y

    @from_centre_offset_y.setter
    def from_centre_offset_y(self, value: float):
        self._from_centre_offset_y = value

    @property
    def to_centre_offset_x(self) -> float:
        return self._to_centre_offset_x

    @to_centre_offset_x.setter
    def to_centre_offset_x(self, value: float):
        self._to_centre_offset_x = value

    @property
    def to_centre_offset_y(self) -> float:
        return self._to_centre_offset_y

    @to_centre_offset_y.setter
    def to_centre_offset_y(self, value: float):
        self._to_centre_offset_y = value

    @property
    def radius1(self) -> int | None:
        return self._radius1

    @property
    def radius2(self) -> int | None:
        return self._radius2

    @property
    def do_jump(self) -> bool:
        return self._do_jump

    @property
    def width(self) -> int:
        return self._width

    @property
    def link(self) -> AutomataLink:
        return self._link

    def get_xy_from_2_buttons(self):
        from_bbox = self._widget_from.bbox
        to_bbox = self._widget_to.bbox

        from_width = from_bbox[2] - from_bbox[0]
        from_height = from_bbox[3] - from_bbox[1]

        to_width = to_bbox[2] - to_bbox[0]
        to_height = to_bbox[3] - to_bbox[1]

        from_x = from_bbox[0] + (from_width / 2) + self._from_centre_offset_x
        from_y = from_bbox[1] + (from_height / 2) + self._from_centre_offset_y

        to_x = to_bbox[0] + (to_width / 2) + self._to_centre_offset_x
        to_y = to_bbox[1] + (to_height / 2) + self._to_centre_offset_y

        zoom_scaler = (self._master.drop_zone_zoom - 10) / (self._master.drop_zone_zoom - 12)
        radius1 = self._radius1 * zoom_scaler
        radius2 = self._radius2 * zoom_scaler

        if radius1 is not None:
            dx = to_x - from_x
            dy = to_y - from_y
            distance = math.sqrt(dx ** 2 + dy ** 2)
            from_x += radius1 * (dx / distance)
            from_y += radius1 * (dy / distance)

        if radius2 is not None:
            dx = to_x - from_x
            dy = to_y - from_y
            distance = math.sqrt(dx ** 2 + dy ** 2)
            to_x -= radius2 * (dx / distance)
            to_y -= radius2* (dy / distance)

        return (from_x, from_y), (to_x, to_y)

    def get_xy_from_start_button(self):
        from_bbox = self._widget_from.bbox
        from_width = from_bbox[2] - from_bbox[0]
        from_height = from_bbox[3] - from_bbox[1]

        from_x = from_bbox[0] + (from_width / 2) + self._from_centre_offset_x
        from_y = from_bbox[1] + (from_height / 2) + self._from_centre_offset_y

        zoom_scaler = (self._master.drop_zone_zoom - 10) / (self._master.drop_zone_zoom - 12)
        radius1 = self._radius1 * zoom_scaler

        if radius1 is not None:
            dx = self._widget_to[0] - from_x
            dy = self._widget_to[1] - from_y
            distance = math.sqrt(dx ** 2 + dy ** 2)
            from_x += radius1 * (dx / distance)
            from_y += radius1 * (dy / distance)

        return from_x, from_y

    def get_xy_from_final_button(self):
        to_bbox = self._widget_to.bbox
        to_width = to_bbox[2] - to_bbox[0]
        to_height = to_bbox[3] - to_bbox[1]

        to_x = to_bbox[0] + (to_width / 2) + self._to_centre_offset_x
        to_y = to_bbox[1] + (to_height / 2) + self._to_centre_offset_y

        zoom_scaler = (self._master.drop_zone_zoom - 10) / (self._master.drop_zone_zoom - 12)
        radius2 = self._radius2 * zoom_scaler

        if radius2:
            dx = to_x - self._widget_from[0]
            dy = to_y - self._widget_from[1]
            distance = math.sqrt(dx ** 2 + dy ** 2)
            to_x -= radius2 * (dx / distance)
            to_y -= radius2 * (dy / distance)

        return to_x, to_y

    @staticmethod
    @cache
    def det(a: tuple[int, int], b: tuple[int, int]) -> int:
        return a[0] * b[1] - a[1] * b[0]

    @staticmethod
    @cache
    def line_intersection(line1: tuple[tuple[int, int], tuple[int, int]],
                          line2: tuple[tuple[int, int], tuple[int, int]]) -> tuple[int, int] | None:
        dx = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
        dy = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

        div = RenderedTransition.det(dx, dy)
        if div == 0:
            return None

        d = (RenderedTransition.det(*line1), RenderedTransition.det(*line2))
        x = RenderedTransition.det(d, dx) / div
        y = RenderedTransition.det(d, dy) / div

        return x, y

    @staticmethod
    @cache
    def distance_between_points(p1: tuple[int, int], p2: tuple[int, int]) -> float:
        return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)

    def _distance_compare(self, p1: tuple[int, int], p2: tuple[int, int]) -> bool:
        dist_p1 = RenderedTransition.distance_between_points(self.from_xy, p1)
        dist_p2 = RenderedTransition.distance_between_points(self.from_xy, p2)
        return dist_p1 < dist_p2

    @staticmethod
    @cache
    def is_point_on_segment(point, start, end):
        cross_product = (point[1] - start[1]) * (end[0] - start[0]) - (point[0] - start[0]) * (end[1] - start[1])

        if abs(cross_product) > 1e-6:  # account for floating point error
            return False

        dot_product = (point[0] - start[0]) * (end[0] - start[0]) + (point[1] - start[1]) * (end[1] - start[1])
        if dot_product < 0:
            return False

        squared_length = (end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2
        if dot_product > squared_length:
            return False

        return True

    def remove_close_intersections(self, intersection_points: PriorityQueue, radius: int = 10):
        filtered_points = PriorityQueue(compare=self._distance_compare)
        while not intersection_points.is_empty():
            point = intersection_points.delete()
            if all(RenderedTransition.distance_between_points(point, other_point) > radius for other_point in
                   filtered_points):
                filtered_points.insert(point)
        return filtered_points

    def _edit_link_by(self, _):
        self._cv.delete(self._tag)

        from_bbox = self.widget_from.bbox
        to_bbox = self.widget_to.bbox

        from_x = (from_bbox[0] + from_bbox[2]) / 2
        from_y = (from_bbox[1] + from_bbox[3]) / 2
        to_x = (to_bbox[0] + to_bbox[2]) / 2
        to_y = (to_bbox[1] + to_bbox[3]) / 2

        mid_x = (from_x + to_x) / 2
        mid_y = (from_y + to_y) / 2

        link_by = self._manager.get_link_by(mid_x, mid_y, placeholder=",".join(self._link.link_by) if self._link.link_by else "")

        self._master.current_automata.remove_transition(self._link.id)

        success, link_id = self._master.current_automata.add_transition(self._link.state_from.id, self._link.state_to.id, link_by)
        if not success:
            messagebox.showerror("Internal Error.", "There was an error when changing link value.")
            raise Exception(f"There was an error when changing link value: {str(link_id)}")
        link_obj = self._master.current_automata.get_transition(int(link_id))
        self._link = link_obj

        self.render()

    def render(self):
        self._cv.delete(self._tag)

        self._from_xy = (0, 0)
        self._to_xy = (0, 0)

        zoom_scaler = (self._master.drop_zone_zoom - 10) / (self._master.drop_zone_zoom - 12)
        radius1 = self._radius1 * zoom_scaler

        if self._widget_from == self._widget_to:
            bbox = self._widget_from.bbox
            width = bbox[2] - bbox[0]
            height = bbox[3] - bbox[1]
            x = bbox[0] + (width / 2) + self._from_centre_offset_x
            y = bbox[1] + (height / 2) + self._to_centre_offset_y
            self._from_xy = (x + radius1, y)

            traverse_angle = math.radians(45)
            self._to_xy = (x + radius1 * math.cos(traverse_angle),
                           y + radius1 * math.sin(traverse_angle))

            self._is_straight = False

            dy = self._to_xy[1] - self._from_xy[1]
            arc_bbox = (self._from_xy[0] - 20, self._from_xy[1] + (dy / 2) - 20,
                        self._from_xy[0] + 20, self._from_xy[1] + (dy / 2) + 20)
            self._cv.create_arc(arc_bbox, start=90, extent=-215, style=ttk.ARC, outline=self._colour,
                                width=self._width, tags=self._tag)

            # Add text to display the link_by
            if self._link.link_by is None:
                link = ["λ"]
            else:
                link = self._link.link_by[:]
            mid_x = (self._from_xy[0] + self._to_xy[0]) / 2
            mid_y = (self._from_xy[1] + self._to_xy[1]) / 2
            self._cv.create_text(mid_x, mid_y, text=",".join(link), fill="#fff",
                                 font=("Bahnschrift", 25, "bold"),
                                 tags=self._tag)

            self._cv.tag_bind(self._tag, "<Double-Button-1>", self._edit_link_by)
            return

        elif isinstance(self._widget_from, TransparentButton) and isinstance(self._widget_to, TransparentButton):
            self._from_xy, self._to_xy = self.get_xy_from_2_buttons()
        elif isinstance(self._widget_from, TransparentButton):
            self._from_xy = self.get_xy_from_start_button()
            self._to_xy = deepcopy(self._widget_to)
        elif isinstance(self._widget_to, TransparentButton):
            self._to_xy = self.get_xy_from_final_button()
            self._from_xy = deepcopy(self._widget_from)
        else:
            self._from_xy = deepcopy(self._widget_from)
            self._to_xy = deepcopy(self._widget_to)

        intersection_points: PriorityQueue = PriorityQueue(compare=self._distance_compare)
        for transition in self._manager.registered_rendered_transitions:
            if transition == self:
                break
            if not transition.is_straight:
                continue
            intersection_point = RenderedTransition.line_intersection((self._from_xy, self._to_xy),
                                                                      (transition.from_xy, transition.to_xy))
            if (intersection_point is not None
                    and RenderedTransition.is_point_on_segment(intersection_point, self._from_xy, self._to_xy) and
                    RenderedTransition.is_point_on_segment(intersection_point, transition.from_xy, transition.to_xy)):
                # print(intersection_point, self._from_xy, self._to_xy, self._widget_from.text, self._widget_to.text)
                intersection_points.insert(intersection_point)

        # intersection_points = self.remove_close_intersections(intersection_points, 3)

        previous_point: tuple[float, float] = self._from_xy
        for point in intersection_points:
            arc_radius = 6 * zoom_scaler

            dx = point[0] - previous_point[0]
            dy = point[1] - previous_point[1]
            distance = math.sqrt(dx ** 2 + dy ** 2)
            mx = arc_radius * (dx / distance)
            my = arc_radius * (dy / distance)
            short_point = (point[0] - mx, point[1] - my)
            self._cv.create_line(previous_point, short_point, fill=self._colour, width=self._width, tags=self._tag)
            previous_point = (point[0] + mx, point[1] + my)

            # Calculate the angle of the line segment
            angle = math.degrees(math.atan2(dy, dx))

            # Calculate the bounding box for the arc
            if angle > 0:
                arc_bbox = (short_point[0] - arc_radius, short_point[1] - arc_radius,
                            short_point[0] + 2*arc_radius, short_point[1] + 2*arc_radius)
            else:
                arc_bbox = (short_point[0] - arc_radius, short_point[1] - 2 * arc_radius,
                            short_point[0] + 2*arc_radius, short_point[1] + arc_radius)

            # self._cv.create_rectangle(arc_bbox, outline="yellow")
            self._cv.create_arc(arc_bbox, start=-angle, extent=180, style=ttk.ARC, outline=self._colour,
                                width=self._width, tags=self._tag)

        self._cv.create_line(previous_point, self._to_xy, fill=self._colour, width=self._width, arrow=ttk.LAST,
                             tags=self._tag)

        # Add text to display the link_by
        if self._link.link_by is None:
            link = ["λ"]
        else:
            link = self._link.link_by[:]
        mid_x = (self._from_xy[0] + self._to_xy[0]) / 2
        mid_y = (self._from_xy[1] + self._to_xy[1]) / 2
        self._cv.create_text(mid_x, mid_y, text=",".join(link), fill="#fff",
                             font=("Bahnschrift", 25, "bold"),
                             tags=self._tag)

        self._cv.tag_bind(self._tag, "<Double-Button-1>", self._edit_link_by)
        self._cv.tag_bind(self._tag, "<Button-3>", lambda _: self._manager.delete_transition(self))

    def delete(self):
        self._cv.delete(self._tag)
