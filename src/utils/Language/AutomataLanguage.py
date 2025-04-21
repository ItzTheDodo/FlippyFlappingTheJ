# FlippyFlappingTheJ
# ./src/utils/Language/AutomataLanguage.py

import re

from src.utils.Automata.AutomataLink import AutomataLink
from src.utils.Automata.AutomataState import AutomataState
from src.utils.DataStruct.Stack import Stack
from src.utils.Language.AutomataAlphabet import AutomataAlphabet
from src.utils.Automata.NDFA import NonDeterministicFiniteAutomaton
from src.utils.Language.AutomataChar import AutomataChar


class AutomataLanguage:

    def __init__(self, alphabet: AutomataAlphabet, language: list[str] = None):

        if language is None:  # Since we can't use mutable types as default arguments
            self._language = []
        else:
            self._language = language

        self._alphabet = alphabet

    def __str__(self) -> str:
        output = ""
        for i in self.language:
            if i == "AND":
                output += "∧"
            elif i == "OR":
                output += "∨"
            else:
                output += i
        return output

    def __iter__(self):
        return iter(self._language)

    @property
    def language(self) -> list[str]:
        return self._language

    @language.setter
    def language(self, value: list[str]):
        self._language = value

    @property
    def alphabet(self) -> AutomataAlphabet:
        return self._alphabet

    @alphabet.setter
    def alphabet(self, value: AutomataAlphabet):
        self._alphabet = value

    def add(self, symbol: str):
        self._language.append(symbol)

    def get_all(self) -> list[str]:
        return self._language

    @staticmethod
    def _parse_language(automaton_language: str) -> list:
        opened_brackets = 0
        output = []
        current_entry = ["", "", "", ""]
        is_end_statement = False

        for char in automaton_language:
            if is_end_statement:
                if char == "*":
                    current_entry[1] = char
                    output.append(current_entry)
                    current_entry = ["", "", "", ""]
                    is_end_statement = False
                    continue
                output.append(current_entry)
                current_entry = ["", "", "", ""]
                is_end_statement = False
            if char == "{":
                opened_brackets += 1
            if char == "}":
                opened_brackets -= 1
                if opened_brackets < 0:
                    raise Exception("Invalid brackets!")
                current_entry[0] += char
                is_end_statement = opened_brackets == 0
                continue
            if opened_brackets > 0:
                current_entry[0] += char
            if opened_brackets == 0:
                if char == "∧":
                    output.append(["", "", "", "∧"])
                elif char == "∨":
                    output.append(["", "", "∨", ""])
                else:
                    raise Exception("Invalid char! : " + char)
        output.append(current_entry)
        return output

    @staticmethod
    def automaton_language_to_postfix(automaton_language: str, alphabet: AutomataAlphabet) -> str:
        if automaton_language == "":
            return ""

        operand_precidence = {"*": 3, "∨": 1, "∧": 2}
        stack = Stack()
        postfix = ""

        items = AutomataLanguage._parse_language(automaton_language)

        for statement in items:
            if statement[0] != "":
                chars = re.match(r"{(.*)}", statement[0]).group(1)
                if "OR" in chars:
                    new_lang = AutomataLanguage(alphabet, chars.split(" "))
                    postfix += new_lang.automaton_language_to_postfix(str(new_lang), alphabet)
                else:
                    if chars == "":
                        chars = "λ"
                    postfix += chars
                    for _ in range(len(chars) - 1):
                        postfix += "∧"
            if statement[1] != "":
                while not stack.is_empty() and operand_precidence[stack.peek()] >= operand_precidence[statement[1]]:
                    postfix += stack.pop()
                stack.push(statement[1])
            if statement[2] != "":
                while not stack.is_empty() and operand_precidence[stack.peek()] >= operand_precidence["∨"]:
                    postfix += stack.pop()
                stack.push("∨")
            if statement[3] != "":
                while not stack.is_empty() and operand_precidence[stack.peek()] >= operand_precidence["∧"]:
                    postfix += stack.pop()
                stack.push("∧")

        while not stack.is_empty():
            postfix += stack.pop()

        return postfix

    @staticmethod
    def create_single_automaton(char: str) -> NonDeterministicFiniteAutomaton:
        states = [AutomataState(0, False, True),
                  AutomataState(1, True, False)]
        if char == "λ":
            alphabet = AutomataAlphabet([])
            transitions = [AutomataLink(0, states[0], states[1], None)]
        else:
            alphabet = AutomataAlphabet([AutomataChar(char)])
            transitions = [AutomataLink(0, states[0], states[1], alphabet.alphabet)]
        start_state = 0
        final_states = [1]

        return NonDeterministicFiniteAutomaton(states, alphabet, transitions, start_state, final_states)

    @staticmethod
    def create_union_of_automata(automaton1: NonDeterministicFiniteAutomaton,
                                 automaton2: NonDeterministicFiniteAutomaton) -> NonDeterministicFiniteAutomaton:
        alphabet = automaton1.alphabet + automaton2.alphabet
        state_id_counter = 0
        link_id_counter = 0
        states = [AutomataState(state_id_counter, False, True)]
        state_id_counter += 1
        states.append(AutomataState(state_id_counter, True, False))
        state_id_counter += 1
        # initial id = 0, final id = 1
        transitions = []

        for state in automaton1.states + automaton2.states:
            state.id = state_id_counter
            if state.is_final:
                state.is_final = False
                transitions.append(AutomataLink(link_id_counter, state, states[1], None))
                link_id_counter += 1
            if state.is_initial:
                state.is_initial = False
                transitions.append(AutomataLink(link_id_counter, states[0], state, None))
                link_id_counter += 1
            states.append(state)
            state_id_counter += 1

        for transition in automaton1.transitions + automaton2.transitions:
            transitions.append(AutomataLink(link_id_counter, transition.state_from,
                                            transition.state_to, transition.link_by))
            link_id_counter += 1

        return NonDeterministicFiniteAutomaton(states, alphabet, transitions, 0, [1])

    @staticmethod
    def create_concatenation_of_automata(automaton1: NonDeterministicFiniteAutomaton,
                                         automaton2: NonDeterministicFiniteAutomaton) -> NonDeterministicFiniteAutomaton:
        alphabet = automaton1.alphabet + automaton2.alphabet
        state_id_counter = 0
        link_id_counter = 0
        states = []
        transitions = []
        a1_final_state = None
        final_state_ids = []

        for state in automaton1.states:
            state.id = state_id_counter
            if state.is_final:
                a1_final_state = state
                state.is_final = False
            states.append(state)
            state_id_counter += 1

        for transition in automaton2.transitions:
            if transition.state_from.is_initial:
                transition.state_from = a1_final_state

        for state in automaton2.states:
            if state.is_initial:
                continue
            if state.is_final:
                final_state_ids.append(state_id_counter)
            state.id = state_id_counter
            states.append(state)
            state_id_counter += 1

        for transition in automaton1.transitions + automaton2.transitions:
            transitions.append(AutomataLink(link_id_counter, transition.state_from,
                                            transition.state_to, transition.link_by))
            link_id_counter += 1

        return NonDeterministicFiniteAutomaton(states, alphabet, transitions, 0, final_state_ids)

    @staticmethod
    def create_kleene_star_of_automaton(automaton: NonDeterministicFiniteAutomaton) -> NonDeterministicFiniteAutomaton:
        alphabet = automaton.alphabet
        state_id_counter = 0
        link_id_counter = 0
        states = [AutomataState(state_id_counter, False, True)]
        state_id_counter += 1
        states.append(AutomataState(state_id_counter, True, False))
        state_id_counter += 1
        transitions = []

        automaton_final_id = 0
        automaton_init_id = 0

        for state in automaton.states:
            state.id = state_id_counter
            if state.is_final:
                state.is_final = False
                transitions.append(AutomataLink(link_id_counter, state, states[1], None))
                automaton_final_id = state_id_counter
                link_id_counter += 1
            if state.is_initial:
                state.is_initial = False
                transitions.append(AutomataLink(link_id_counter, states[0], state, None))
                automaton_init_id = state_id_counter
                link_id_counter += 1
            states.append(state)
            state_id_counter += 1

        for transition in automaton.transitions:
            transitions.append(AutomataLink(link_id_counter, transition.state_from,
                                            transition.state_to, transition.link_by))
            link_id_counter += 1

        transitions.append(AutomataLink(link_id_counter, states[0], states[1], None))
        link_id_counter += 1
        transitions.append(AutomataLink(link_id_counter, states[automaton_final_id], states[automaton_init_id], None))

        return NonDeterministicFiniteAutomaton(states, alphabet, transitions, 0, [1])

    def to_non_deterministic_finite_automaton(self) -> NonDeterministicFiniteAutomaton:
        # Using thompsons construction

        postfix = self.automaton_language_to_postfix(str(self), self.alphabet)

        if postfix == "":
            return self.create_single_automaton(None)

        stack = Stack()

        for char in postfix:
            if char == "∧":
                automaton2 = stack.pop()
                automaton1 = stack.pop()
                stack.push(self.create_concatenation_of_automata(automaton1, automaton2))
            elif char == "∨":
                automaton2 = stack.pop()
                automaton1 = stack.pop()
                stack.push(self.create_union_of_automata(automaton1, automaton2))
            elif char == "*":
                automaton = stack.pop()
                stack.push(self.create_kleene_star_of_automaton(automaton))
            else:
                stack.push(self.create_single_automaton(char))

        return stack.pop()
