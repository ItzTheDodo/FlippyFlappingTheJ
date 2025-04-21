# FlippyFlappingTheJ
# ./src/utils/LayoutEngine/ForceDirected.py

import math
import random

from src.utils.Automata.AutomatonBuilder import AutomatonBuilder


class ForceDirectedLayout:

    def __init__(self, automaton_builder: AutomatonBuilder, width: int = 730, height: int = 480, iterations: int = 1000, cooling: float = 0.99):
        self._automaton_builder = automaton_builder
        self._width = width
        self._height = height
        self._iterations = iterations
        self._cooling = cooling
        self._radius = 50

        center_x = width / 2
        center_y = height / 2
        self._positions: dict[int, tuple[float, float]] = {
            state.id: (center_x + random.uniform(-width / 10, width / 10),
                       center_y + random.uniform(-height / 10, height / 10))
            for state in automaton_builder.states}

        # Ensure the initial state is the leftmost state
        if automaton_builder.initial_state is not None:
            initial_state = automaton_builder.get_state(automaton_builder.initial_state)
            self._positions[initial_state.id] = (0, center_y)

    @property
    def automaton_builder(self) -> AutomatonBuilder:
        return self._automaton_builder

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def iterations(self) -> int:
        return self._iterations

    @property
    def cooling(self) -> float:
        return self._cooling

    @property
    def positions(self) -> dict[int: tuple[float, float]]:
        return self._positions

    def calculate_layout(self) -> None:
        temperature = self._width / 10.0

        for _ in range(self._iterations):
            forces: dict[int, list[float]] = {state_id: [0, 0] for state_id in self._positions}

            # Calculate repulsive forces (node collision detection)
            for state_id1, pos1 in self._positions.items():
                for state_id2, pos2 in self._positions.items():
                    if state_id1 != state_id2:
                        dx = pos1[0] - pos2[0]
                        dy = pos1[1] - pos2[1]
                        distance = math.sqrt(dx ** 2 + dy ** 2)
                        if distance > 0:
                            min_distance = self._radius * 2
                            if distance < min_distance:
                                repulsive_force = 1000 / (distance ** 2)
                                forces[state_id1][0] += repulsive_force * dx / distance
                                forces[state_id1][1] += repulsive_force * dy / distance

            # Calculate attractive forces (edge length constraints)
            for transition in self._automaton_builder.transitions:
                from_state = transition.state_from.id
                to_state = transition.state_to.id
                pos1 = self._positions[from_state]
                pos2 = self._positions[to_state]
                dx = pos2[0] - pos1[0]
                dy = pos2[1] - pos1[1]
                distance = math.sqrt(dx ** 2 + dy ** 2)
                if distance > 0:
                    attractive_force = (distance ** 2) / 100
                    forces[from_state][0] += attractive_force * dx / distance
                    forces[from_state][1] += attractive_force * dy / distance
                    forces[to_state][0] -= attractive_force * dx / distance
                    forces[to_state][1] -= attractive_force * dy / distance

            # Update positions
            for state_id, force in forces.items():
                dx, dy = force
                distance = math.sqrt(dx ** 2 + dy ** 2)
                if distance > 0:
                    displacement = min(distance, temperature)
                    self._positions[state_id] = (
                        self._positions[state_id][0] + (dx / distance) * displacement,
                        self._positions[state_id][1] + (dy / distance) * displacement
                    )

            # Cool down
            temperature *= self._cooling

    def get_positions(self) -> dict[int: tuple[float, float]]:
        return self._positions
