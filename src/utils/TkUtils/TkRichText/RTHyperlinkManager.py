# FlippyFlappingTheJ
# ./src/utils/TkUtils/TkRichText/RTHyperlinkManager.py

from src.utils.TkUtils.TkRichText.RichText import TkRichText


class HyperlinkManager:

    def __init__(self, text):

        if not isinstance(text, TkRichText):
            raise TypeError("text must be a TkRichText object")

        self.text = text
        self.links = []

        self.text.tag_config("hyper", foreground="blue", underline=1)
        self.text.tag_bind("hyper", "<Enter>", self._enter)
        self.text.tag_bind("hyper", "<Leave>", self._leave)
        self.text.tag_bind("hyper", "<Button-1>", self._click)

        self.reset()

    def listener(self, *_):
        regexp = r"(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})"
        self.text.highlighted_pattern(regexp, "hyper", regexp=True)

    def reset(self):
        self.links = []

    def add(self, cmd_onclick):
        self.links.append(cmd_onclick)

    def _enter(self, *_):
        self.text.config(cursor="hand2")

    def _leave(self, *_):
        self.text.config(cursor="")

    def _click(self, event):
        for i in self.links:
            i(event)
