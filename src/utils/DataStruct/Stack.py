# FlippyFlappingTheJ
# ./src/utils/DataStruct/Stack.py


class Stack:
    """
        Class used to implement a stack data structure

        ...

        Methods
        -------
        push(value: any)
            pushes a value onto the stack
        pop() -> any
            pops a value from the stack
        peek() -> any
            returns the top value of the stack
        is_empty() -> bool
            checks if the stack is empty
        clear()
            clears the stack
        get_all() -> list[any]
            returns all values in the stack in a generator
    """

    def __init__(self):

        self._stack: list[any] = []

    def __str__(self) -> str:
        return str(self._stack)

    def __len__(self) -> int:
        return len(self._stack)

    def __iter__(self) -> iter:
        return iter(reversed(self._stack))

    def push(self, value: any):
        self._stack.append(value)

    def pop(self) -> any:
        if len(self._stack) == 0:
            return None
        return self._stack.pop()

    def peek(self) -> any:
        if len(self._stack) == 0:
            return None
        return self._stack[-1]

    def is_empty(self) -> bool:
        return len(self._stack) == 0

    def clear(self):
        self._stack.clear()

    def get_all(self) -> list[any]:
        for item in self:
            yield item
            self.pop()
