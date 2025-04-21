# FlippyFlappingTheJ
# ./src/utils/Automata/Automaton.py

from src.utils.Automata.AutomataLink import AutomataLink
from src.utils.Automata.AutomataState import AutomataState
from src.utils.IO.AutomatonFile import AutomatonFile
from src.utils.Language.AutomataAlphabet import AutomataAlphabet


class Automaton:
    """
    Class used to represent an automaton

    ...

    Attributes
    ----------
    states -> list[AutomataState]
        list of states in the automaton
    alphabet -> AutomataAlphabet
        alphabet of the automaton
    transitions -> list[AutomataLink]
        list of transitions in the automaton
    start_state -> int
        id of the start state
    final_states -> list[int]
        list of ids of final states

    Methods
    -------
    run(input_string: str) -> bool
        runs the automaton on the input string
    get_transitions_from_state(state_id: int, symbol: str = None) -> list[AutomataLink]
        gets the transitions from a state (with a given symbol if provided)
    get_transition_table() -> dict
        gets the transition table of the automaton
    """

    def __init__(self, states: list[AutomataState], alphabet: AutomataAlphabet, transitions: list[AutomataLink],
                 start_state: int, final_states: list[int]):

        self._states = states
        self._alphabet = alphabet
        self._transitions = transitions
        self._start_state = start_state
        self._final_states = final_states

        self._validate_states(states)

    def _validate_states(self, states: list[AutomataState]):
        if not all(isinstance(state, AutomataState) for state in states):
            raise ValueError("All states must be of type AutomataState.")

        for state in states:
            if state.is_final and state.id not in self._final_states:
                raise ValueError("Final states must be included in the states list.")
            if state.id in self._final_states and not state.is_final:
                raise ValueError("Final states must be marked as final.")
            if state.id == self._start_state and not state.is_initial:
                raise ValueError("Start state must be marked as start.")
            if state.is_initial and state.id != self._start_state:
                raise ValueError("Start state must be marked as start.")

    def __str__(self):
        return (f"Automaton(States: {list(map(str, self.states))},"
                f"\n    Alphabet: {self.alphabet},"
                f"\n    Transitions: {list(map(str, self.transitions))},"
                f"\n    Start State: {self.start_state},"
                f"\n    Final States: {self.final_states})")

    @property
    def states(self) -> list[AutomataState]:
        return self._states

    @states.setter
    def states(self, value: list[AutomataState]):
        self._validate_states(value)
        self._states = value

    @property
    def alphabet(self) -> AutomataAlphabet:
        return self._alphabet

    @property
    def transitions(self) -> list[AutomataLink]:
        return self._transitions

    @property
    def start_state(self) -> int:
        return self._start_state

    @property
    def final_states(self) -> list[int]:
        return self._final_states

    def to_file(self, fp: str) -> AutomatonFile: ...

    def run(self, input_string: str) -> bool: ...

    def get_transitions_from_state(self, state_id: int, symbol: str = None) -> list[AutomataLink]: ...

    def get_transition_table(self) -> dict: ...
