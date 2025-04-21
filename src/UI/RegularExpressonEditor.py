# FlippyFlappingTheJ
# ./src/UI/RegularExpressionEditor.py

import os
from tkinter import *
from tkinter import messagebox

from src.utils.TkUtils.RoundedButton import RoundedButton
from src.utils.TkUtils.TkRichText.RTLineNumbers import TkTextLineNumbers
from src.utils.TkUtils.TkRichText.RichText import TkRichText


class RegexEditorUI(Toplevel):

    WIN_WIDTH: int = 750
    WIN_HEIGHT: int = 600

    TEXT_HEIGHT: int = 30

    COLOUR_PALLET: list[str] = ["#cfcec7", "#c2bcb5", "#c0bbb2", "#a09b92", "#807b72", "#605b52"]

    def __init__(self, master: Tk, runtime):
        super().__init__(master)

        self._master_window = master
        self._runtime = runtime

        self.title("Regular Expression Editor")
        offset_x = self._master_window.winfo_x() + ((self._master_window.winfo_width() - self.WIN_WIDTH) / 2)
        offset_y = self._master_window.winfo_y() + ((self._master_window.winfo_height() - self.WIN_HEIGHT) / 2)
        self.geometry("%sx%s+%s+%s" % (self.WIN_WIDTH, self.WIN_HEIGHT, int(offset_x), int(offset_y)))
        self.resizable(False, False)

        self.screen = Canvas(self, width=self.WIN_WIDTH, height=self.WIN_HEIGHT, background=self.COLOUR_PALLET[0], bd=0)
        self.screen.pack(side='top', fill='both', expand=1)

        # output
        self._regex: str = ""

        # monitoring vars
        self._running: bool = True
        self._update_line: bool = False
        self._main_text_box: TkRichText | None = None

        # Draw text input
        self._draw_text_input()
        self._draw_buttons()

        self.protocol("WM_DELETE_WINDOW", self.close)
        try:
            self.update_loop()
        except TclError:
            pass

    def update_loop(self):
        while self._running:
            self.update()
            if not self._update_line:
                continue
            self._main_text_box.tag_remove("grey_highlight", "1.0", "end")
            current_line = self._main_text_box.index(INSERT).split(".")[0]
            self._main_text_box.tag_add("grey_highlight", f"{current_line}.0", f"{current_line}.0+1lines")
            self._update_line = False

    def close(self, *_):
        self._running = False
        self._regex = self._main_text_box.get("1.0", END)
        self.destroy()

    @property
    def regex(self) -> str:
        return self._regex

    def _draw_text_input(self):
        self._main_text_box = TkRichText(self, width=83, height=self.TEXT_HEIGHT, undo=True)

        vsb = Scrollbar(self, orient="vertical", command=self._main_text_box.yview)
        self._main_text_box["yscrollcommand"] = vsb.set

        line_numbers = TkTextLineNumbers(self, textwidget=self._main_text_box, width=25,
                                         height=self.TEXT_HEIGHT * (16 + (1/9)), background=self.COLOUR_PALLET[1], bd=0,
                                         highlightthickness=0, relief='ridge')

        self.screen.create_window(20, 20, window=line_numbers, anchor=NW)
        self.screen.create_window(45, 20, window=self._main_text_box, anchor=NW)
        vsb.place(in_=self._main_text_box, relx=1.0, relheight=1.0, bordermode="outside")

        self._main_text_box.bind("<Button-1>", self._on_line_change)
        self._main_text_box.bind("<KeyPress>", self._on_line_change)

        line_numbers.redraw()
        self._on_line_change("")
        self._main_text_box.focus()

    def _on_line_change(self, _):
        # This looks stupid to use the mainloop but line highlighting doesn't update properly
        # otherwise so we need a flag *dies inside*
        self._update_line = True

    def _display_help(self, _):
        help_fp = os.path.join(self._runtime.datafolder.assets_folder, "regex_help")
        with open(help_fp, "r") as r_file:
            help_text = r_file.read()
        messagebox.showinfo("Regex info.", help_text, parent=self)

    def _load_example(self, _):
        val = self._main_text_box.get("1.0", END)
        if not val.isspace() and val:
            can_replace = messagebox.askokcancel("Delete current work",
                                                 "Are you sure you want to replace your current work?", parent=self)
            if not can_replace:
                return
        example_fp = os.path.join(self._runtime.datafolder.assets_folder, "example_language_file.lsf")
        with open(example_fp, "r") as r_file:
            example_text = r_file.read()
        self._main_text_box.delete("1.0", "end-1c")
        self._main_text_box.insert("1.0", example_text)

    def _exit_without_regex(self, _):
        self._main_text_box.delete("1.0", "end-1c")
        self.close()

    def _draw_buttons(self):
        # background
        RoundedButton.round_rectangle(self.screen, 20, 510, 730, 590, radius=10,
                                      fill=self.COLOUR_PALLET[1])

        # help button
        RoundedButton(self, self.screen, 30, 523, "ⓘ Help", self._display_help, fill=self.COLOUR_PALLET[3],
                      padding=20, radius=4, hover_colour=self.COLOUR_PALLET[4], click_colour=self.COLOUR_PALLET[5],
                      width=100)

        # load example button
        RoundedButton(self, self.screen, 140, 523, "Load example", self._load_example,
                      fill=self.COLOUR_PALLET[3], padding=20, radius=4, hover_colour=self.COLOUR_PALLET[4],
                      click_colour=self.COLOUR_PALLET[5], width=100)

        # close button
        RoundedButton(self, self.screen, 500, 523, "Close", self._exit_without_regex,
                      fill=self.COLOUR_PALLET[3], padding=20, radius=4, hover_colour=self.COLOUR_PALLET[4],
                      click_colour=self.COLOUR_PALLET[5], width=100)

        # draw button
        RoundedButton(self, self.screen, 610, 523, "Draw..", self.close,
                      fill=self.COLOUR_PALLET[3], padding=20, radius=4, hover_colour=self.COLOUR_PALLET[4],
                      click_colour=self.COLOUR_PALLET[5], width=100)
