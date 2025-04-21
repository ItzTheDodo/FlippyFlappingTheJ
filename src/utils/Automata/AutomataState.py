# FlippyFlappingTheJ
# ./src/utils/Automata/AutomataState.py


class AutomataState:
    """
    Class used to represent a state in an automata

    ...

    Attributes
    ----------
    id -> int
        represents a unique identifier for the state in an automata
    is_final -> bool
        determines if the state is a final acceptance state
    if_initial -> bool
        determines if the state is the initial state in the automata
    """

    def __init__(self, state_id: int, is_final: bool = False, is_initial: bool = False):

        self._id = state_id
        self._is_final = is_final
        self._is_initial = is_initial

    def __str__(self):
        return (f"State(ID: {self.id},"
                f" Is Final: {self.is_final},"
                f" Is Initial: {self.is_initial})")

    @property
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, value: int):
        self._id = value

    @property
    def is_final(self) -> bool:
        return self._is_final

    @is_final.setter
    def is_final(self, value: bool):
        self._is_final = value

    @property
    def is_initial(self) -> bool:
        return self._is_initial

    @is_initial.setter
    def is_initial(self, value: bool):
        self._is_initial = value
