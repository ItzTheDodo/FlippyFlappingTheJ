# FlippyFlappingTheJ
# ./src/utils/Language/AutomataChar.py


class AutomataChar(str):
    """
    Class used to represent a character in an automata language

    ...

    Attributes
    ----------
    char -> str
        string representation of the character
    """

    def __init__(self, char: str):
        self._char = char

    @property
    def char(self) -> str:
        return self._char

    @char.setter
    def char(self, value: str):
        self._char = value

    def __str__(self) -> str:
        return self.char
