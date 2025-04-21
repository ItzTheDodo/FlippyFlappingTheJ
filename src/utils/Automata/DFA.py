# FlippyFlappingTheJ
# ./src/utils/Automata/DFA.py

import json
from typing import Self

from src.utils.Automata.AutomataLink import AutomataLink
from src.utils.Automata.AutomataState import AutomataState
from src.utils.Automata.Automaton import Automaton
from src.utils.DataStruct.Tree import Tree, Node
from src.utils.IO.AutomatonFile import AutomatonFile
from src.utils.Language.AutomataAlphabet import AutomataAlphabet


class DeterministicFiniteAutomaton(Automaton):

    def __init__(self, states: list[AutomataState], alphabet: AutomataAlphabet, transitions: list[AutomataLink],
                 start_state: int, final_states: list[int]):
        super().__init__(states, alphabet, transitions, start_state, final_states)

    def __str__(self):
        return (f"DFA(States: {list(map(str, self.states))},"
                f"\n    Alphabet: {self.alphabet},"
                f"\n    Transitions: {list(map(str, self.transitions))},"
                f"\n    Start State: {self.start_state},"
                f"\n    Final States: {self.final_states})")

    def get_final_states(self) -> list[AutomataState]:
        states = []
        for state in self.states:
            if state.is_final:
                states.append(state)
        return states

    @staticmethod
    def _state_in_list(state: AutomataState, li: list[AutomataState]) -> bool:
        for s in li:
            if s.id == state.id:
                return True
        return False

    @staticmethod
    def _which_node_in(item: any, li: list[Node]) -> int:
        for i, node in enumerate(li):
            if item in node.value:
                return i

    def _convert_ids_to_states(self, state_ids: list[int]) -> list[AutomataState]:
        output = []
        for state in self.states:
            if state.id in state_ids:
                output.append(state)
        return output

    def simplify(self) -> Self:
        simplification = Tree(0)
        final_states: list[int] = []
        other_states: list[int] = []
        for state in self.states:
            if state.is_final:
                final_states.append(state.id)
                continue
            other_states.append(state.id)
        final_states_node = Node(set(final_states))
        final_states_node.parent = simplification.root
        simplification.root.children.append(final_states_node)
        other_states_node = Node(set(other_states))
        other_states_node.parent = simplification.root
        simplification.root.children.append(other_states_node)

        prev_sets = []
        cur_sets = [set(final_states), set(other_states)]
        i = 0
        times_complete = 0

        # Loop
        while not times_complete == len(self.alphabet):
            if prev_sets == cur_sets:
                times_complete += 1
            else:
                times_complete = 0
            leaves: list[Node] = simplification.get_leaves()
            char_test: str = self.alphabet[i % len(self.alphabet)].char
            prev_sets = cur_sets[:]
            cur_sets = []
            for node in leaves:
                state_ids: set[int] = node.value
                possible_children = len(leaves)
                new_nodes: list[list[int]] = [[] for _ in range(possible_children + 1)]
                for state_id in state_ids:
                    transitions = self.get_transitions_from_state(state_id, char_test)
                    if not transitions:
                        new_node_loc = -1
                    else:
                        transition = transitions[0]
                        new_node_loc = self._which_node_in(transition.state_to.id, leaves)
                    new_nodes[new_node_loc].append(state_id)
                for new_node in new_nodes:
                    if not new_node:
                        continue
                    cur_sets.append(set(new_node))
                    node_set = Node(set(new_node))
                    node_set.parent = node
                    node.children.append(node_set)
            i += 1

        new_states = simplification.get_leaves()
        transition_table = {str(list(state.value)): c for c, state in enumerate(new_states)}
        new_dfa_transitions = []
        new_dfa_states = []
        transition_id_counter = 0
        transition_to_update: list[tuple[int, int]] = []  # [(transition_id, state_to_id)...]
        initial_state = 0
        final_states = []
        for state_id, node in enumerate(new_states):
            old_state_ids: list[int] = list(node.value)
            old_transitions = self.get_transitions_from_state(old_state_ids[0])
            old_states = self._convert_ids_to_states(old_state_ids)
            is_final = False
            is_initial = False
            for state in old_states:
                if state.is_final:
                    is_final = True
                if state.is_initial:
                    is_initial = True
                    initial_state = state_id
            if is_final:
                final_states.append(state_id)
            new_state = AutomataState(state_id, is_final, is_initial)
            new_dfa_states.append(new_state)
            for transition in old_transitions:
                state_to_id = 0
                for assignment in transition_table.keys():
                    li = json.loads(assignment)
                    if transition.state_to.id in li:
                        state_to_id = transition_table[assignment]
                        break
                new_dfa_transitions.append(AutomataLink(transition_id_counter, new_state, AutomataState(0), transition.link_by))
                transition_to_update.append((transition_id_counter, state_to_id))
                transition_id_counter += 1
        for transition_id, state_id in transition_to_update:
            new_dfa_transitions[transition_id].state_to = new_dfa_states[state_id]

        return DeterministicFiniteAutomaton(new_dfa_states, self.alphabet, new_dfa_transitions, initial_state, final_states)

    def negate(self):
        final_states = []
        for state in self.states:
            state.is_final = not state.is_final
            if state.is_final:
                final_states.append(state.id)
        self._final_states = final_states[:]

    def get_transitions_from_state(self, state_id: int, symbol: str = None) -> list[AutomataLink]:
        transitions = []
        for link in self.transitions:
            if not link.state_from.id == state_id:
                continue
            if symbol is None:
                transitions.append(link)
                continue
            for char in link.link_by:
                if char.char == symbol:
                    transitions.append(link)
                    break
        return transitions

    def run(self, input_string: str) -> bool:
        current_state = self.states[self.start_state]
        for char in input_string:
            transitions = self.get_transitions_from_state(current_state.id, char)
            if not transitions:
                return False
            current_state = transitions[0].state_to
        return current_state.is_final

    def get_transition_table(self) -> dict:
        transition_table = {}
        for state in self.states:
            transition_table[state.id] = {}
            for symbol in self.alphabet:
                from_state = self.get_transitions_from_state(state.id, symbol.char)
                state_ids = []
                for link in from_state:
                    state_ids.append(link.state_to.id)
                transition_table[state.id][symbol.char] = state_ids
        return transition_table

    def to_file(self, fp: str) -> AutomatonFile:
        file_contents = {"is_deterministic": True, "alphabet": [char.char for char in self.alphabet]}
        states = {}
        transitions = {}

        for state in self.states:
            states[str(state.id)] = {"initial": state.is_initial, "final": state.is_final}
        file_contents["states"] = states

        for transition in self.transitions:
            transitions[str(transition.id)] = {"from": transition.state_from.id, "to": transition.state_to.id,
                                               "link_by": [char.char for char in transition.link_by]}
        file_contents["transitions"] = transitions

        with open(fp, "w") as write_file:
            write_file.write(
                json.dumps(file_contents, indent=4, sort_keys=True, separators=(',', ': ')).replace("\\n", "\n"))

        return AutomatonFile(fp)

