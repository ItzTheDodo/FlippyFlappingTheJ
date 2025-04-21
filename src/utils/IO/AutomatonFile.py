# FlippyFlappingTheJ
# ./src/utils/IO/AutomatonFile.py

import os.path

from src.utils.AppDataConfig.Config import ConfigurationFile
from src.utils.Automata.AutomataLink import AutomataLink
from src.utils.Automata.AutomataState import AutomataState
from src.utils.Language.AutomataAlphabet import AutomataAlphabet
from src.utils.Language.AutomataChar import AutomataChar


class AutomatonFile(ConfigurationFile):

    def __init__(self, fp: str):
        super().__init__(fp)

        _, extension = os.path.splitext(self.url)
        if not extension == ".automaton":
            raise ValueError(f"File type: {extension}, Expected .automaton")

    def is_deterministic(self) -> bool:
        return bool(self.getValue("is_deterministic"))

    def get_alphabet(self) -> AutomataAlphabet:
        alphabet_chars = list(self.getValue("alphabet"))
        alphabet = AutomataAlphabet()

        for char in alphabet_chars:
            automata_char = AutomataChar(char)
            alphabet.add(automata_char)

        return alphabet

    def get_states(self) -> tuple[list[AutomataState], list[int], int]:
        """
        RETURNS
        -------
        (
            list of states -> AutomataState,
            list of final state ids -> list[int],
            the initial state id -> int
        )
        """

        file_states = self.getValue("states")

        states: list[AutomataState] = []
        final_states: list[int] = []
        initial_state: int | None = None

        for state_id, details in file_states.items():
            is_final = details["final"]
            is_initial = details["initial"]
            istate_id = int(state_id)
            states.append(AutomataState(istate_id, is_final, is_initial))
            if is_initial:
                initial_state = istate_id
            if is_final:
                final_states.append(istate_id)

        return states, final_states, initial_state

    def get_transitions(self, states: list[AutomataState]) -> list[AutomataLink]:
        file_transitions = self.getValue("transitions")

        transitions: list[AutomataLink] = []

        for transition_id, details in file_transitions.items():
            state_from: AutomataState | None = None
            state_to: AutomataState | None = None
            for state in states:
                if state.id == int(details["from"]):
                    state_from = state
                if state.id == int(details["to"]):
                    state_to = state
            if state_from is None or state_to is None:
                raise ValueError(f"State {details["from"]} or {details["to"]} does not exist in states passed in")

            link_by: list[AutomataChar] = []
            for char in details["by"]:
                link_by.append(AutomataChar(char))

            transitions.append(AutomataLink(int(transition_id), state_from, state_to, link_by))

        return transitions
