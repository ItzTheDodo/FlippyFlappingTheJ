# FlippyFlappingTheJ
# ./src/utils/Automata/AutomataLink.py

from src.utils.Automata.AutomataState import AutomataState
from src.utils.Language.AutomataChar import AutomataChar


class AutomataLink:
    """
    Class used to represent a link in an automata

    ...

    Attributes
    ----------
    id -> int
        represents a unique identifier for the state in an automata
    state_from -> AutomataState
        represents the state from which the link originates
    state_to -> AutomataState
        represents the state to which the link points
    link_by -> list[AutomataChar] | AutomataLanguage | None
        represents the character or language that the link is associated with
        (lambda state transitions are represented by None)
    """

    def __init__(self, link_id: int,
                 state_from: AutomataState, state_to: AutomataState,
                 link_by: list[AutomataChar] | None):

        self._id = link_id
        self._state_from = state_from
        self._state_to = state_to
        self._link_by = link_by

    def __str__(self) -> str:
        return (f"Link(ID: {self.id},"
                f" From: {self.state_from.id},"
                f" To: {self.state_to.id},"
                f" Link By: {self.link_by})")

    @property
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, value: int):
        self._id = value

    @property
    def state_from(self) -> AutomataState:
        return self._state_from

    @state_from.setter
    def state_from(self, value: AutomataState):
        self._state_from = value

    @property
    def state_to(self) -> AutomataState:
        return self._state_to

    @state_to.setter
    def state_to(self, value: AutomataState):
        self._state_to = value

    @property
    def link_by(self) -> list[AutomataChar] | None:
        return self._link_by

    @link_by.setter
    def link_by(self, value: list[AutomataChar] | None):
        self._link_by = value
