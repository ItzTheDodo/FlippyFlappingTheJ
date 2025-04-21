# FlippyFlappingTheJ
# ./src/utils/Language/AutomataAlphabet.py

from typing import overload, Self

from src.utils.Language.AutomataChar import AutomataChar


class AutomataAlphabet:
    """
        Class used to represent an alphabet for an automata

        ...

        Attributes
        ----------
        alphabet -> list[AutomataChar]
            list of characters in the alphabet

        Methods
        -------
        add(symbol: AutomataChar)
            adds a character to the alphabet
        get_all() -> list[AutomataChar]
            returns all characters in the alphabet
        get(symbol: AutomataChar) -> AutomataChar
            returns the character in the alphabet
        get(index: int) -> AutomataChar
            returns the character at the given index
        get_pos(char: AutomataChar) -> int
            return the position of a string char (-1 if not exist)
        copy() -> AutomataAlphabet
            returns a deep copy of the automata alphabet object
        """

    def __init__(self, alphabet: list[AutomataChar] = None):

        if alphabet is None:  # Since we can't use mutable types as default arguments
            self._alphabet = []
        else:
            self._alphabet = alphabet

    def add(self, symbol: AutomataChar):
        self.alphabet.append(symbol)
        self._remove_duplicates()

    def get_all(self) -> list[AutomataChar]:
        return self.alphabet

    def get_pos(self, char: AutomataChar) -> int:
        for c, achar in enumerate(self.alphabet):
            if char.char == achar.char:
                return c
        return -1

    def copy(self) -> Self:
        return AutomataAlphabet(self.alphabet[:])

    @overload
    def get(self, symbol: AutomataChar) -> AutomataChar:
        return self.alphabet[self.alphabet.index(symbol)]

    def get(self, index: int) -> AutomataChar:
        return self.alphabet[index]

    @property
    def alphabet(self) -> list[AutomataChar]:
        return self._alphabet

    @alphabet.setter
    def alphabet(self, value: list[AutomataChar]):
        self._alphabet = value

    def _remove_duplicates(self):
        seen: set[str] = set(self.alphabet)
        self.alphabet = [char for char in seen]

    def __len__(self):
        return len(self.alphabet)

    def __iter__(self):
        return iter(self.alphabet)

    def __contains__(self, symbol: AutomataChar):
        return symbol in self.alphabet

    def __getitem__(self, index: int):
        return self.alphabet[index]

    def __setitem__(self, index: int, value: AutomataChar):
        self.alphabet[index] = value

    def __str__(self):
        return str(self.alphabet)

    def __add__(self, other):
        new = AutomataAlphabet(self.alphabet + other.alphabet)
        new._remove_duplicates()
        return new
