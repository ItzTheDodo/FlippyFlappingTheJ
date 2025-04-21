# FlippyFlappingTheJ
# ./src/utils/TkUtils/TkRichText/RTTempText.py

from src.utils.TkUtils.TkRichText.RichText import TkRichText


class TkTempText:

    def __init__(self, textwidget: TkRichText):

        self.textwidget = textwidget

        if not isinstance(self.textwidget, TkRichText):
            raise Exception("[TkTempText] Invalid text object: Use TkRichText")

        self.textwidget.tag_configure("tmp_txt")
        self._text = None
        self._tag_range = None

    def _remove_text(self):
        if not self._tag_range:
            return
        self.textwidget.tag_remove("tmp_txt", self._tag_range[0], self._tag_range[1])
        self.textwidget.tag_remove("light_grey", self._tag_range[0], self._tag_range[1])
        self.textwidget.delete(self._tag_range[0], self._tag_range[1])

    def on_mouse_move(self, e):
        self._remove_text()
        extra_lines = self._text.count("\n")
        last_ret_on = len(self._text.split("\n")[-1])
        start_mpos = self.textwidget.index("@%d,%d" % (e.x, e.y)).split(".")[0] + ".0"
        last_mpos = "%d.%d" % (int(start_mpos.split(".")[0]) + extra_lines, int(start_mpos.split(".")[1]) + last_ret_on)
        self.textwidget.insert(start_mpos, self._text)
        self.textwidget.tag_add("tmp_txt", start_mpos, last_mpos)
        self.textwidget.tag_add("light_grey", start_mpos, last_mpos)
        self._tag_range = (start_mpos, last_mpos)
        self.textwidget.bind("<Leave>", self.hide_text)

    def show_text(self, text):
        if text is None:
            return
        self._text = text + "\n"
        self.textwidget.bind("<Motion>", self.on_mouse_move)
        self.textwidget.bind("<Escape>", self.hide_text)
        self.textwidget.bind("<Button-1>", self.convert_to_perm_text)

    def hide_text(self, *_):
        if self._text is None:
            return
        self.textwidget.unbind("<Motion>")
        self.textwidget.unbind("<Leave>")
        self.textwidget.unbind("<Escape>")
        self.textwidget.unbind("<Button-1>")
        self._text = None
        self._remove_text()

    def convert_to_perm_text(self, *_):
        if self._text is None:
            return
        self.textwidget.unbind("<Motion>")
        self.textwidget.unbind("<Leave>")
        self.textwidget.unbind("<Escape>")
        self.textwidget.unbind("<Button-1>")
        self._text = None
        self.textwidget.tag_remove("tmp_txt", self._tag_range[0], self._tag_range[1])
        self.textwidget.tag_remove("light_grey", self._tag_range[0], self._tag_range[1])
        self._tag_range = None
