# FlippyFlappingTheJ
# ./src/utils/TkUtils/RealTimeUpdateManager.py

from collections.abc import Callable
import tkinter as ttk
import time
import math
from functools import cache


class UpdateJob:
    """
    Job object for this tkinter update manager


    ...


    Attributes
    ----------
    duration -> int:
        The duration of the job on nanoseconds
    update_tag -> str:
        a tag given to the job to prevent the same job being run concurrently
    init_exec_cmd -> Callable[..., None]:
        a command to be called when the job is initialised (to be left as None if not used)
    final_exec_cmd -> Callable[..., None]:
        a command to be called when the job is closed (to be left as None if not used)
    update_exec_cmd -> Callable[..., None]:
        a command to be called on every frame while the job is running (to be left as None if not used)

    (protected) start_time -> int:
        used by the update manager to save the start time of the job
    """

    def __init__(self, duration: int, update_tag: str,
                 init_exec_cmd: Callable[..., None] = None,
                 final_exec_cmd: Callable[..., None] = None,
                 update_exec_cmd: Callable[..., None] = None):

        self._duration = duration
        self._init_exec_cmd = init_exec_cmd
        self._final_exec_cmd = final_exec_cmd
        self._update_exec_cmd = update_exec_cmd
        self._update_tag = update_tag

        self._start_time: int = 0

    @property
    def duration(self) -> int:
        return self._duration

    @property
    def init_exec(self) -> Callable[..., None]:
        return self._init_exec_cmd

    @property
    def final_exec(self) -> Callable[..., None]:
        return self._final_exec_cmd

    @property
    def update_exec(self) -> Callable[..., None]:
        return self._update_exec_cmd

    @property
    def start_time(self) -> int:
        return self._start_time

    @start_time.setter
    def start_time(self, ti: int):
        self._start_time = ti

    @property
    def update_tag(self) -> str:
        return self._update_tag


class PulseColour(UpdateJob):
    """
    A possible job for this tkinter update manager to pulse the colour of a canvas widget
    (Note: uses fill attribute for canvas widget)


    ...


    Attributes
    ----------
    duration -> int:
        The duration of the pulse on nanoseconds
    master -> tkinter.Canvas:
        the canvas object that the widget(s) is/are attached to
    tag_bind_id -> str:
        the canvas tag attached to target widget(s)
    pulse_colour -> str:
        hex colour of the pulse (i.e. #ff0000 (red))
    """

    def __init__(self, duration: int, master: ttk.Canvas, tag_bind_id: str, pulse_colour: str):
        UpdateJob.__init__(self, duration, "pulse_" + tag_bind_id, update_exec_cmd=self._blend_colour,
                           final_exec_cmd=self._return_colour, init_exec_cmd=self._set_item_colour)

        self._master = master
        self._tag_bind_id = tag_bind_id
        self._colour = pulse_colour

        self._item_colour: str = ""

    @staticmethod
    @cache
    def combine_hex_values(**d: dict[str: int]) -> str:
        """
        Combines a number of weighted hex colour values into one colour
        (function is cached to improve performance)

        Attributes
        ----------
        d -> dict[str: int]:
            a dictionary containing a colour hex value as a string referencing the weight of the colour in the output
            e.g. {'ee847c': 0.87, 'a09b92': 0.13}
        """
        d_items = sorted(d.items())
        tot_weight = sum(d.values())
        red = int(sum([int(k[:2], 16) * v for k, v in d_items]) / tot_weight)
        green = int(sum([int(k[2:4], 16) * v for k, v in d_items]) / tot_weight)
        blue = int(sum([int(k[4:6], 16) * v for k, v in d_items]) / tot_weight)
        return "#" + hex(red)[2:].zfill(2) + hex(green)[2:].zfill(2) + hex(blue)[2:].zfill(2)

    @property
    def colour(self) -> str:
        return self._colour

    def _set_item_colour(self):
        self._item_colour = self._master.itemcget(self._tag_bind_id, "fill")

    def _blend_colour(self):
        amount_through = min((time.time_ns() - self.start_time) / self.duration, 1)
        amount_new_col = math.sin(amount_through * math.pi)
        new_col = self.combine_hex_values(**{self._colour[1:]: amount_new_col, self._item_colour[1:]: 1 - amount_new_col})
        self._master.itemconfigure(self._tag_bind_id, fill=new_col)

    def _return_colour(self):
        self._master.itemconfigure(self._tag_bind_id, fill=self._item_colour)


class RealTimeUpdateManager:
    """
    An update manager for tkinter interfaces to control real time changes
    (Note: update function must be manually called in an update loop)


    ...


    Attributes
    ----------
    master -> tkinter.Canvas | tkinter.Tk | tkinter.Toplevel:
        The master that the update manager is attached to

    Methods
    -------
    exists_job_with_tag(tag: str) -> bool
        checks if there is a job with a specified tag
    register_job(job: UpdateJob) -> bool
        registers a job with the update manager and returns a boolean status
    update()
        to be called in an update loop, will update all jobs in queue
    """

    def __init__(self, master: ttk.Canvas | ttk.Tk | ttk.Toplevel):

        self._master = master
        self._todo: list[UpdateJob] = []

    @property
    def master(self) -> ttk.Canvas | ttk.Tk | ttk.Toplevel:
        return self._master

    @staticmethod
    def seconds_to_ns(seconds: float) -> float:
        return int(seconds * 1e+9)

    def exists_job_with_tag(self, tag: str) -> bool:
        for job in self._todo:
            if job.update_tag == tag:
                return True
        return False

    def register_job(self, job: UpdateJob) -> bool:
        if not isinstance(job, UpdateJob):
            return False
        if self.exists_job_with_tag(job.update_tag) and not job.update_tag == "":
            return False
        self._todo.append(job)
        return True

    def update(self):
        new_todo: list[UpdateJob] = []
        for job in self._todo:
            if not job.start_time == 0:
                time_elapsed = time.time_ns() - job.start_time
                if time_elapsed > job.duration:
                    if job.final_exec:
                        job.final_exec()
                    continue
                if job.update_exec:
                    job.update_exec()
                new_todo.append(job)
                continue
            job.start_time = time.time_ns()
            if job.init_exec:
                job.init_exec()
            new_todo.append(job)
        self._todo = new_todo[:]
