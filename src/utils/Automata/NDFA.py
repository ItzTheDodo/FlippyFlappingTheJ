# FlippyFlappingTheJ
# ./src/utils/Automata/NDFA.py

import json

from src.utils.Automata.AutomataLink import AutomataLink
from src.utils.Automata.AutomataState import AutomataState
from src.utils.Automata.Automaton import Automaton
from src.utils.Automata.DFA import DeterministicFiniteAutomaton
from src.utils.DataStruct.Tree import Tree, Node
from src.utils.IO.AutomatonFile import AutomatonFile
from src.utils.Language.AutomataAlphabet import AutomataAlphabet


class NonDeterministicFiniteAutomaton(Automaton):

    def __init__(self, states: list[AutomataState], alphabet: AutomataAlphabet, transitions: list[AutomataLink],
                 start_state: int, final_states: list[int]):
        super().__init__(states, alphabet, transitions, start_state, final_states)

    def __str__(self):
        return (f"NDFA(States: {list(map(str, self.states))},"
                f"\n    Alphabet: {self.alphabet},"
                f"\n    Transitions: {list(map(str, self.transitions))},"
                f"\n    Start State: {self.start_state},"
                f"\n    Final States: {self.final_states})")

    def _get_lambda_transitions_from_state(self, state_id: int) -> Tree:
        transitions = Tree(0)
        for link in self.transitions:
            if not link.state_from.id == state_id:
                continue
            if link.link_by is None:
                this_transition = Node(link.id)
                for child in self._get_lambda_transitions_from_state(link.state_to.id).root.children:
                    child.parent = this_transition
                    this_transition.children.append(child)
                transitions.root.children.append(this_transition)
        return transitions

    def _get_leafs_of_dict(self, d: dict):
        leaves = []
        for k, v in d.items():
            if v == {}:
                leaves.append(k)
                continue
            leaves.extend(self._get_leafs_of_dict(v))
        return leaves

    def _exists_transition_straight_from_state(self, state_id: int, symbol: str) -> bool:
        for link in self.transitions:
            if not link.state_from.id == state_id:
                continue
            if link.link_by is None:
                continue
            for char in link.link_by:
                if char.char == symbol:
                    return True
        return False

    def get_transitions_by_id(self, transition_ids: list[int]) -> list[AutomataLink]:
        transitions = []
        for link in self.transitions:
            if link.id in transition_ids:
                transitions.append(link)
        return transitions

    def get_states_by_id(self, state_ids: list[int]) -> list[AutomataState]:
        states = []
        for state in self.states:
            if state.id in state_ids:
                states.append(state)
        return states

    def _to_effective_link(self, link: AutomataLink) -> list[AutomataLink]:
        # This function takes a link and returns all the effective links taking into account lambda states
        lambda_transitions = self._get_lambda_transitions_from_state(link.state_to.id)
        if not lambda_transitions.root.children:
            return [link]
        link_ids = [node.value for node in lambda_transitions.get_leaves()]
        links = self.get_transitions_by_id(link_ids)
        keep_orig_link = True in [self._exists_transition_straight_from_state(link.state_to.id, char.char) for char in link.link_by]
        if keep_orig_link:
            links.append(link)
        return links

    def _to_effective_link_lambda(self, link: AutomataLink) -> list[AutomataLink]:
        # This function takes a lambda link and returns all the effective links taking into account lambda states
        if link.link_by:  # accept symbol links and hand off to base function
            return self._to_effective_link(link)
        lambda_transitions = self._get_lambda_transitions_from_state(link.state_to.id)
        if not lambda_transitions.root.children:
            return [link]
        link_ids = [node.value for node in lambda_transitions.get_leaves()]
        links = self.get_transitions_by_id(link_ids)
        return links

    def get_transitions_from_state(self, state_id: int, symbol: str = None) -> (list[AutomataLink], bool):
        transitions = []
        from_state_final = False
        for link in self.transitions:
            if not link.state_from.id == state_id:
                continue
            if symbol is None:
                transitions.append(link)
                continue
            if link.link_by is None:
                from_state_final = True in [li.state_to.is_final for li in self._to_effective_link_lambda(link)] or from_state_final
                transitions.extend(self.get_transitions_from_state(link.state_to.id, symbol)[0])
                continue

            for char in link.link_by:
                if char.char == symbol:
                    effective_links = self._to_effective_link(link)
                    transitions.extend(effective_links)
                    break

        return transitions, from_state_final

    def get_transition_table(self) -> dict:
        transition_table = {}  # {state_id: {symbol: [state_ids...]}...}
        seen_ids = []

        for state in self.states:
            transition_table[state.id] = {}
            for symbol in self.alphabet:
                from_state, _ = self.get_transitions_from_state(state.id, symbol.char)
                state_ids = []
                for link in from_state:
                    state_ids.append(link.state_to.id)
                seen_ids.extend(state_ids)
                transition_table[state.id][symbol.char] = state_ids

        return transition_table

    def to_deterministic(self) -> DeterministicFiniteAutomaton:
        dfa = {}   # {state_name: {symbol: state_name...}...}

        current_states = [[self.start_state]]  # [[state_id...]...]
        final_states_flags = []

        while len(current_states) > 0:
            new_states = []
            for dfa_state in current_states:
                if str(dfa_state) in dfa.keys():
                    continue
                if not dfa_state:
                    continue
                dfa[str(dfa_state)] = {}
                for symbol in self.alphabet:
                    transitions_for_symbol = []
                    lambda_final = False
                    for state_id in dfa_state:
                        from_state, is_lambda_final = self.get_transitions_from_state(state_id, symbol.char)
                        state_ids = []
                        for link in from_state:
                            state_ids.append(link.state_to.id)
                        transitions_for_symbol.extend(state_ids)
                        lambda_final = is_lambda_final or lambda_final
                    transitions_for_symbol = list(set(transitions_for_symbol))  # remove list duplicates
                    transitions_for_symbol.sort()  # sort list since order matters because keys are strings
                    dfa[str(dfa_state)][symbol.char] = transitions_for_symbol
                    if lambda_final:
                        final_states_flags.append(str(dfa_state))
                        final_states_flags = list(set(final_states_flags))
                    new_states.append(transitions_for_symbol)

            current_states = new_states[:]

        conversion_table = list(dfa.keys())
        transitions = []
        states = []
        link_id_counter = 0
        links_to_update = []  # [[link_id, state_id]...]
        start_state = 0
        final_states = []

        for state_id, derived_states in enumerate(conversion_table):
            is_start = state_id == 0
            is_final = (len([value for value in self.final_states if value in json.loads(derived_states)]) > 0
                        or str(derived_states) in final_states_flags)
            new_state = AutomataState(state_id, is_final, is_start)
            if is_start:
                start_state = state_id
            if is_final:
                final_states.append(state_id)
            states.append(new_state)
            current_transitions = dfa[derived_states]
            for symbol in self.alphabet:
                current_char = symbol.char
                to_state_derived = current_transitions[current_char]
                if not to_state_derived:
                    continue
                to_state_id = conversion_table.index(str(to_state_derived))
                transitions.append(AutomataLink(link_id_counter, new_state, AutomataState(0), [symbol]))
                links_to_update.append([link_id_counter, to_state_id])
                link_id_counter += 1

        for link in links_to_update:
            transitions[link[0]].state_to = states[link[1]]

        return DeterministicFiniteAutomaton(states, self.alphabet, transitions, start_state, final_states)

    def negate(self) -> DeterministicFiniteAutomaton:
        dfa = self.to_deterministic()
        dfa = dfa.simplify()
        dfa.negate()
        return dfa

    def run(self, input_string: str) -> bool:
        current_states = [self.start_state]
        for char in input_string:
            new_states = []
            for state_id in current_states:
                from_state, _ = self.get_transitions_from_state(state_id, char)
                for link in from_state:
                    new_states.append(link.state_to.id)
            current_states = list(set(new_states))
        return len([state for state in current_states if state in self.final_states]) > 0

    def to_file(self, fp: str) -> AutomatonFile:
        file_contents = {"is_deterministic": False, "alphabet": [char.char for char in self.alphabet]}
        states = {}
        transitions = {}

        for state in self.states:
            states[str(state.id)] = {"initial": state.is_initial, "final": state.is_final}
        file_contents["states"] = states

        for transition in self.transitions:
            transitions[str(transition.id)] = {"from": transition.state_from.id, "to": transition.state_to.id,
                                               "link_by": [char.char for char in transition.link_by] if transition.link_by is not None else []}
        file_contents["transitions"] = transitions

        with open(fp, "w") as write_file:
            write_file.write(
                json.dumps(file_contents, indent=4, sort_keys=True, separators=(',', ': ')).replace("\\n", "\n"))

        return AutomatonFile(fp)
