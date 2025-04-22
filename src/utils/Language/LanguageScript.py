# FlippyFlappingTheJ
# ./src/utils/Language/LanguageScript.py

from __future__ import annotations

import os
import re
import time

from src.utils.AppDataConfig.Datafolder import DataFolder
from src.utils.Automata.AutomatonBuilder import AutomatonBuilder
from src.utils.Language.AutomataAlphabet import AutomataAlphabet
from src.utils.Language.AutomataLanguage import AutomataLanguage


class LanguageScriptFile:
    """
    Class used to represent a language script file

    ...

    Attributes
    ----------
    path -> str
        path to the language script file
    alphabet -> AutomataAlphabet
        alphabet of the language script file
    language -> AutomataLanguage
        language of the language script file

    Methods
    -------
    load_file() -> str
        loads the contents of the file
    parse_alphabet(lines: str) -> AutomataAlphabet
        parses the alphabet from the file
    parse_language(lines: str) -> AutomataLanguage
        parses the language from the file
    parse() -> None
        parses the alphabet and language from the file
    """

    def __init__(self, file_path: str):

        self._path = file_path
        self._file_contents = self.load_file()

        self._alphabet: AutomataAlphabet = AutomataAlphabet()
        self._language: AutomataLanguage = AutomataLanguage(self.alphabet)
        self.parse()

    @staticmethod
    def load_by_string(contents: str, datafolder: DataFolder) -> LanguageScriptFile:
        fp = os.path.join(datafolder.temp_folder, f"temp_lsf_{time.time()}.lsf")
        with open(fp, "w") as w_file:
            w_file.write(contents)
        return LanguageScriptFile(fp)

    def load_file(self) -> str:
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"File '{self.path}' not found.")
        if not os.path.isfile(self.path):
            raise FileNotFoundError(f"'{self.path}' is not a file.")
        if not os.access(self.path, os.R_OK):
            raise PermissionError(f"File '{self.path}' is not readable.")
        if not os.path.basename(self.path).endswith('.lsf'):
            raise ValueError(f"File '{self.path}' is not a Language Script File.")

        with open(self.path, 'r') as rfile:
            return rfile.read()

    @property
    def path(self) -> str:
        return self._path

    @path.setter
    def path(self, value: str):
        self._path = value
        self._file_contents = self.load_file()
        self.parse()

    def __str__(self) -> str:
        return (f"LanguageScriptFile({self.path}, "
                f"{self._alphabet}, "
                f"{self._language})")

    @staticmethod
    def parse_alphabet(lines: str) -> AutomataAlphabet:
        alphabet_chars = re.search(r"(alphabet:=)|(alphabet := )\"(.*?)\"", lines)
        if alphabet_chars is None:
            raise ValueError("No alphabet found but invalid.")
        return AutomataAlphabet(list(alphabet_chars.group(3)))

    @staticmethod
    def parse_language(alphabet, lines: str) -> AutomataLanguage:
        language_chars = re.search(r"(language:=)|(language := ){((.|\n)*)}", lines)
        if language_chars is None:
            raise ValueError("No language found but invalid.")
        raw_language = language_chars.group(3)
        language_lines = raw_language.split("\n")
        language_lines = map(str.strip, language_lines)  # Remove leading/trailing whitespace
        language_lines = filter(None, language_lines)  # Remove empty lines
        return AutomataLanguage(alphabet, list(language_lines))

    def _check_for_invalid_characters(self, string: str) -> bool:
        # example string: "{{a} OR {b} OR {c}}*" "valid characters: {a, b, c}"
        match = re.match(r"{(.*)}", string).group(1)
        values = match.split(" OR ")

        for charset in values:
            if "{" in charset:
                charset = re.match(r"{(.*)}", charset).group(1)
            set_of_chars = set(list(charset))
            if not set_of_chars.intersection(self.alphabet) == set_of_chars:
                return True
        return False

    def _check_language_validity(self):
        for lang in self._language:
            if lang == "AND":
                continue
            if lang == "OR":
                continue
            matches = re.search(r"{(.*?)}(.*)", lang)
            if matches is None:
                raise ValueError("Language is not valid.")
            # Ensure no illegal characters are present with alphabet
            if self._check_for_invalid_characters(lang):
                raise ValueError("Language contains characters not in alphabet.")
            # set_of_chars = set(list(str(matches.group(1))))
            # if not set_of_chars.intersection(self._alphabet) == set_of_chars:
            #     raise ValueError("Language contains characters not in alphabet.")

    def parse(self):
        self._language = None
        self._alphabet = None

        lines = self._file_contents.split('\n')

        for line in lines:
            if line.startswith("//") or line == "":
                continue

            if self._language is not None and self._alphabet is not None:
                break

            if line.startswith("alphabet := ") or line.startswith("alphabet:="):
                self._alphabet = self.parse_alphabet(self._file_contents)

            if line.startswith("language := ") or line.startswith("language:="):
                self._language = self.parse_language(self._alphabet, self._file_contents)

        if self._alphabet is None:
            raise ValueError("No alphabet found in file.")
        if self._language is None:
            raise ValueError("No language found in file.")

        self._check_language_validity()

    @property
    def alphabet(self) -> AutomataAlphabet:
        return self._alphabet

    @alphabet.setter
    def alphabet(self, value: AutomataAlphabet):
        self._alphabet = value
        self._language = AutomataLanguage(self.alphabet, self.language.language)
        self._check_language_validity()

    @property
    def language(self) -> AutomataLanguage:
        return self._language
