# FlippyFlappingTheJ
# ./src/utils/Automata/AutomatonBuilder.py

from __future__ import annotations

from src.utils.Automata.AutomataLink import AutomataLink
from src.utils.Automata.AutomataState import AutomataState
from src.utils.Automata.DFA import DeterministicFiniteAutomaton
from src.utils.Automata.NDFA import NonDeterministicFiniteAutomaton
from src.utils.Language.AutomataAlphabet import AutomataAlphabet
from src.utils.Language.AutomataChar import AutomataChar


class AutomatonBuilder:
    """
    A class to build and manipulate finite automata, including both deterministic (DFA) and non-deterministic (NDFA) types.


    ...


    Attributes
    ----------
    states: list[AutomataState]
        A list of states in the automaton.
    transitions: list[AutomataLink]
        A list of transitions between states in the automaton.
    final_states: list[int]
        A list of IDs of final states in the automaton.
    initial_state: int | None
        The ID of the initial state, or None if not set.
    alphabet: AutomataAlphabet
        The alphabet used by the automaton.

    Methods
    -------
    get_builder_from_finite_automata(fa: DeterministicFiniteAutomaton | NonDeterministicFiniteAutomaton) -> AutomatonBuilder:
        Creates an AutomatonBuilder from an existing finite automaton.

    is_deterministic() -> bool:
        Checks if the automaton is deterministic.

    to_finite_automata() -> DeterministicFiniteAutomaton | NonDeterministicFiniteAutomaton:
        Converts the builder to a finite automaton.

    add_state(is_final: bool, is_initial: bool, _id: int = None) -> tuple[bool, str]:
        Adds a state to the automaton.

    get_state(state_id: int) -> AutomataState | None:
        Retrieves a state by its ID.

    remove_state(state_id: int) -> tuple[bool, str]:
        Removes a state from the automaton.

    is_char_in_alphabet(char: str) -> AutomataChar | None:
        Checks if a character is in the automaton's alphabet.

    add_transition(state_from_id: int, state_to_id: int, link_by: str) -> tuple[bool, str]:
        Adds a transition between states in the automaton.

    get_transition(transition_id: int) -> AutomataLink | None:
        Retrieves a transition by its ID.

    remove_transition(transition_id: int) -> tuple[bool, str]:
        Removes a transition from the automaton.

    toggle_state_initial(state_id: int) -> tuple[bool, str]:
        Toggles the initial state status of a state.

    toggle_state_final(state_id: int) -> tuple[bool, str]:
        Toggles the final state status of a state.
    """

    def __init__(self):

        # Core automaton assets
        self._states: list[AutomataState] = []
        self._transitions: list[AutomataLink] = []
        self._final_states: list[int] = []
        self._initial_state: int | None = None
        self._alphabet: AutomataAlphabet = AutomataAlphabet()

        # tracking variables
        self._transition_id_counter: int = 0
        self._state_id_counter: int = 0

    def __str__(self) -> str:
        return (f"DFA(States: {list(map(str, self.states))},"
                f"\n    Alphabet: {self.alphabet},"
                f"\n    Transitions: {list(map(str, self.transitions))},"
                f"\n    Start State: {self._initial_state},"
                f"\n    Final States: {self.final_states})")

    @staticmethod
    def get_builder_from_finite_automata(fa: DeterministicFiniteAutomaton | NonDeterministicFiniteAutomaton) -> AutomatonBuilder:
        builder = AutomatonBuilder()
        max_transition_id: int = 0
        max_state_id: int = 0

        for state in fa.states:
            max_state_id = max(state.id, max_state_id)
            builder.add_state(state.is_final, state.is_initial, _id=state.id)

        for transition in fa.transitions:
            max_transition_id = max(transition.id, max_transition_id)
            if transition.link_by is None:
                builder.add_transition(transition.state_from.id, transition.state_to.id, None)
                continue
            for char in transition.link_by:
                builder.add_transition(transition.state_from.id, transition.state_to.id, char.char)

        builder._transition_id_counter = max_transition_id + 1
        builder._state_id_counter = max_state_id + 1
        return builder

    @property
    def states(self) -> list[AutomataState]:
        return self._states

    @property
    def transitions(self) -> list[AutomataLink]:
        return self._transitions

    @property
    def final_states(self) -> list[int]:
        return self._final_states

    @property
    def initial_state(self) -> int:
        return self._initial_state

    @property
    def alphabet(self) -> AutomataAlphabet:
        return self._alphabet

    def is_deterministic(self) -> bool:
        init_li: list[int] = [0 for _ in self._alphabet]
        state_and_transitions: dict[int, list[int]] = {}

        for transition in self._transitions:
            state_id = transition.state_from.id
            if state_id not in state_and_transitions.keys():
                state_and_transitions[state_id] = init_li[:]
            if transition.link_by is None:
                return False
            for char in transition.link_by:
                pos = self._alphabet.get_pos(char)
                if pos == -1:
                    raise Exception("Illegal character in Automaton " + str(char.char))
                state_and_transitions[state_id][pos] += 1
        for val in state_and_transitions.values():
            for amount_conns in val:
                if amount_conns > 1:
                    return False
        return True

    def to_finite_automata(self) -> DeterministicFiniteAutomaton | NonDeterministicFiniteAutomaton:
        if self.is_deterministic():
            return DeterministicFiniteAutomaton(self._states, self._alphabet, self._transitions, self._initial_state, self._final_states)
        return NonDeterministicFiniteAutomaton(self._states, self._alphabet, self._transitions, self._initial_state, self._final_states)

    def add_state(self, is_final: bool, is_initial: bool, _id: int = None) -> tuple[bool, str]:
        if is_initial and self._initial_state is not None:
            return False, "Initial state already exists"
        if _id is not None:
            state = AutomataState(_id, is_final, is_initial)
            self._states.append(state)
            if is_final:
                self._final_states.append(_id)
            if is_initial:
                self._initial_state = _id
            return True, str(_id)
        state = AutomataState(self._state_id_counter, is_final, is_initial)
        if is_final:
            self._final_states.append(self._state_id_counter)
        if is_initial:
            self._initial_state = self._state_id_counter
        self._state_id_counter += 1
        self._states.append(state)
        return True, str(self._state_id_counter - 1)

    def get_state(self, state_id: int) -> AutomataState | None:
        for state in self._states:
            if state.id == state_id:
                return state
        return None

    def remove_state(self, state_id: int) -> tuple[bool, str]:
        old_state = None
        for c, state in enumerate(self._states):
            if state.id == state_id:
                old_state = self._states.pop(c)
                break
        if old_state is None:
            return False, "State does not exist"
        if old_state.is_initial:
            self._initial_state = None
        if old_state.is_final:
            self._final_states.remove(state_id)

        for transition in self._transitions[:]:
            if transition.state_to.id == state_id or transition.state_from.id == state_id:
                self.remove_transition(transition.id)

        return True, ""

    def is_char_in_alphabet(self, char: str) -> AutomataChar | None:
        for achar in self._alphabet:
            if achar.char == char:
                return achar
        return None

    def add_transition(self, state_from_id: int, state_to_id: int, link_by: str | list[str] | None) -> tuple[bool, str]:
        link_by_char = []
        if isinstance(link_by, str):
            temp_char = self.is_char_in_alphabet(link_by)
            if temp_char is None:
                temp_char = AutomataChar(link_by)
                self._alphabet.add(temp_char)
            link_by_char.append(temp_char)
        elif isinstance(link_by, list):
            for char in link_by:
                temp_char = self.is_char_in_alphabet(char)
                if temp_char is None:
                    temp_char = AutomataChar(char)
                    self._alphabet.add(temp_char)
                link_by_char.append(temp_char)
        elif link_by is None:
            link_by_char = None
        else:
            return False, "Invalid link by!"

        state_from = self.get_state(state_from_id)
        state_to = self.get_state(state_to_id)
        if state_from is None or state_to is None:
            return False, "States do not exist!"

        transition = AutomataLink(self._transition_id_counter, state_from, state_to, link_by_char)
        self._transition_id_counter += 1
        self._transitions.append(transition)
        return True, str(self._transition_id_counter - 1)

    def get_transition(self, transition_id: int) -> AutomataLink | None:
        for transition in self._transitions:
            if transition.id == transition_id:
                return transition
        return None

    def _exists_char_in_transitions(self, char: AutomataChar) -> bool:
        for transition in self._transitions:
            if transition.link_by is None:
                continue
            for tchar in transition.link_by:
                if tchar.char == char:
                    return True
        return False

    def _remove_char_from_alphabet(self, char: AutomataChar):
        for c, achar in enumerate(self._alphabet):
            if achar.char == char.char:
                self._alphabet.alphabet.pop(c)
                return

    def remove_transition(self, transition_id: int) -> tuple[bool, str]:
        old_transition = None
        for c, transition in enumerate(self._transitions):
            if transition.id == transition_id:
                old_transition = self._transitions.pop(c)
                break
        if old_transition is None:
            return False, "Transition does not exist"
        if old_transition.link_by is None:
            return True, ""
        for char in old_transition.link_by:
            if not self._exists_char_in_transitions(char):
                self._remove_char_from_alphabet(char)
        return True, ""

    def toggle_state_initial(self, state_id: int) -> tuple[bool, str]:
        if self._initial_state == state_id:
            self._initial_state = None
            for state in self._states:
                if state.id == state_id:
                    state.is_initial = False
            return True, ""
        if self._initial_state is not None:
            return False, "There already exists an initial state"
        for state in self._states:
            if state.id == state_id:
                state.is_initial = True
        self._initial_state = state_id
        return True, ""

    def toggle_state_final(self, state_id: int) -> tuple[bool, str]:
        for state in self._states:
            if not state.id == state_id:
                continue
            if state.is_final:
                self._final_states.remove(state_id)
                state.is_final = False
                return True, ""
            self._final_states.append(state_id)
            state.is_final = True
            return True, ""

    def is_final(self, state_id: int) -> bool:
        return state_id in self.final_states

    def is_initial(self, state_id: int) -> bool:
        return state_id == self.initial_state

    def exists_transition(self, state_id1: int, state_id2: int) -> AutomataLink | None:
        for transition in self._transitions:
            if transition.state_from.id == state_id1 and transition.state_to.id == state_id2:
                return transition
        return None
