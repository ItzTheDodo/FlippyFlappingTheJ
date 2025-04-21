# FlippyFlappingTheJ
# ./src/utils/TkUtils/TkRichText/RichText.py

import tkinter as ttk
import difflib


class TkRichText(ttk.Text):

    def __init__(self, master, *, colour_patterns=None, **kwargs):
        ttk.Text.__init__(self, master=master, **kwargs)

        if colour_patterns is None:
            self._colour_patterns = []
        else:
            self._colour_patterns = colour_patterns

        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._event_proxy)

        self._on_change_callback = []
        self._on_scroll_callback = []
        self._buffered_text = ""

        self._default_font = ttk.font.nametofont(self.cget("font"))
        self._em = self._default_font.measure("m")
        self._default_font_size = self._default_font.cget("size")

        self._setup_tags()
        self.bind("<Tab>", self._insert_tab)

    def _reorder_tags(self):
        for i in self._colour_patterns:
            self.tag_raise(i[1])
        self.tag_raise("sel")

    def set_colour_pattern(self, pattern):
        for tag in self.tag_names():
            self.tag_remove(tag, "1.0", "end")
        self._colour_patterns = pattern
        self._reorder_tags()

    def _event_proxy(self, *args):
        cmd = (self._orig, ) + args
        result = self.tk.call(cmd)

        if (args[0] == "xview" or args[0] == "yview") and args[1] == "moveto" or args[1] == "scroll":
            for i in self._on_scroll_callback:
                i(args[1])

        if args[0] in ("insert", "delete", "replace") or args[0:3] == ("mark", "set", "insert"):
            self.on_change_callback(self.get("1.0", "end"))

        return result

    def register_on_change_callback(self, callback):
        self._on_change_callback.append(callback)

    def register_on_scroll_callback(self, callback):
        self._on_scroll_callback.append(callback)

    def on_change_callback(self, sv, diff=False):
        for i in self._on_change_callback:
            i(sv)
        _, _, diff_indexes = self.get_difference("1.0", "end")
        for k in self._colour_patterns:
            for i in diff_indexes:
                ri = sv.rfind("\n", 0, i)
                ri = 0 if ri == -1 else ri
                fi = sv.find("\n", ri)
                fi = len(sv) if fi == -1 else fi
                self.highlighted_pattern(k[0], k[1], start=f"{ri + 1}.0" if diff else "1.0", end=f"{fi}.0" if diff else "end", regexp=(len(k) > 2 and k[2]), highlight=k[3] if len(k) > 3 else None)

    def get_lmargin(self, step=1):
        return self._em + self._default_font.measure("\u2022 ") * (step - 1)

    def insert_bullet(self, i, text, *tags):
        self.insert(i, f"\u2022 {text}", "bullet", *tags)

    def _insert_tab(self, *_):
        self.insert(ttk.INSERT, " " * 4)
        return 'break'

    def get_difference(self, start, end):
        diff_added = []
        diff_removed = []
        diff_indexes = []
        case1 = self._buffered_text
        case2 = self.get(start, end)
        for i, s in enumerate(difflib.ndiff(case1, case2)):
            if s[0] == "":
                continue
            if s[0] == "-":
                diff_removed.append((i, s[-1]))
            elif s[0] == "+":
                diff_added.append((i, s[-1]))
            diff_indexes.append(i)
        return diff_added, diff_removed, diff_indexes

    def highlighted_pattern(self, pattern, *tag, start="1.0", end="end", regexp=False, highlight=None):
        for i in tag:
            self.tag_remove(i, start, end)  # remove tag first
        start = self.index(start)  # test
        end = self.index(end)
        self.mark_set("matchStart", start)
        self.mark_set("matchEnd", start)
        self.mark_set("searchLimit", end)

        count = ttk.IntVar()
        index = self.search(pattern, "matchEnd", "searchLimit", count=count, regexp=regexp)
        while count.get() > 0:
            if index == "" or count.get() == 0:
                return
            self.mark_set("matchStart", index)
            self.mark_set("matchEnd", "%s+%sc" % (index, count.get()))
            for i in tag:
                if highlight is None:
                    self.tag_add(i, "matchStart", "matchEnd")
                else:
                    section = self.get("matchStart", "matchEnd")
                    p1 = section.find(highlight)
                    self.tag_add(i, f"{index}+{p1}c", f"{index}+{p1 + len(highlight)}c")
            index = self.search(pattern, "matchEnd", "searchLimit", count=count, regexp=regexp)

    def _setup_tags(self):
        base_default = ttk.font.Font(self, **self._default_font.configure())

        self._bold = base_default.copy()
        self._bold.configure(weight="bold")
        self.tag_configure("bold", font=self._bold)

        self._italic = base_default.copy()
        self._italic.configure(slant="italic")
        self.tag_configure("italic", font=self._italic)

        self._underline = base_default.copy()
        self._underline.configure(underline=True)
        self.tag_configure("underline", font=self._underline)

        ## Colours ##
        self.tag_configure("red", foreground="red")
        self.tag_configure("green", foreground="green")
        self.tag_configure("blue", foreground="blue")
        self.tag_configure("yellow", foreground="yellow")
        self.tag_configure("cyan", foreground="cyan")
        self.tag_configure("magenta", foreground="magenta")
        self.tag_configure("orange", foreground="orange")
        self.tag_configure("purple", foreground="purple")
        self.tag_configure("black", foreground="black")
        self.tag_configure("white", foreground="white")
        self.tag_configure("grey", foreground="grey")
        self.tag_configure("light_grey", foreground="light grey")
        self.tag_configure("dark_grey", foreground="dark grey")
        self.tag_configure("grey_highlight", background="light grey")
        ########

        self.tag_raise("sel")
