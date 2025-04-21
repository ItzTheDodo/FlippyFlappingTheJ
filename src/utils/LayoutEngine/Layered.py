from src.utils.Automata.AutomatonBuilder import AutomatonBuilder


class LayeredLayout:
    def __init__(self, automaton_builder: AutomatonBuilder, layer_height=100, node_spacing=50):
        self._automaton_builder = automaton_builder
        self._layer_height = layer_height
        self._node_spacing = node_spacing
        self._positions = self._calculate_positions()

    def _calculate_positions(self):
        positions = {}
        layers = self._assign_layers()
        for layer, states in layers.items():
            y = layer * self._layer_height
            x_start = (len(states) - 1) * self._node_spacing / -2
            for i, state in enumerate(states):
                x = x_start + i * self._node_spacing
                positions[state.id] = (x, y)
        return positions

    def _assign_layers(self):
        layers = {}
        visited = set()
        queue = [(self._automaton_builder.initial_state, 0)]
        while queue:
            state_id, layer = queue.pop(0)
            if state_id not in visited:
                visited.add(state_id)
                if layer not in layers:
                    layers[layer] = []
                state = self._automaton_builder.get_state(state_id)
                layers[layer].append(state)
                for transition in self._automaton_builder.get_transitions_from_state(state_id):
                    queue.append((transition.state_to.id, layer + 1))
        return layers

    @property
    def positions(self):
        return self._positions
