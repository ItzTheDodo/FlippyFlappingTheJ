# FlippyFlappingTheJ
# ./src/utils/DataStruct/Stack.py

from typing import Self, Iterable


class Node:
    """
        Class used to implement a tree node

        ...

        Attributes
        ----------
        value -> any
            represents the value of the node
        children -> list[Node]
            represents the children of the node
        parent -> Node
            represents the parent of the node

        Methods
        -------
        add_child(child: Node)
            adds a child to the node
        remove_child(child: Node) -> Node
            removes a child from the node
    """

    def __init__(self, value: any = None):
        self._value = value
        self._children = []
        self._parent = None

    def add_child(self, child: Self):
        child.parent = self
        self._children.append(child)

    def remove_child(self, child: Self) -> Self:
        child.parent = None
        self._children.remove(child)
        return child

    @property
    def is_root(self) -> bool:
        return self.parent is None

    @property
    def is_leaf(self) -> bool:
        return len(self.children) == 0

    @property
    def parent(self) -> Self:
        return self._parent

    @parent.setter
    def parent(self, value: Self):
        self._parent = value

    @property
    def children(self) -> list[Self]:
        return self._children

    @property
    def value(self) -> any:
        return self._value

    @value.setter
    def value(self, value: any):
        self._value = value

    def __str__(self) -> str:
        return f"Node({self.value}, children = {self.children})"

    def __iter__(self):
        yield self
        for child in self.children:
            yield from child


class Tree:
    """
        Class used to implement a tree data structure
        Note: builtin iter method performs a depth first search

        ...

        Attributes
        ----------
        root -> Node
            represents the root of the tree

        Methods
        -------
        breadth_first_search() -> list[Node]
            performs a breadth first search on the tree
        get_leaves() -> list[Node]
            returns all the leaf nodes
    """

    def __init__(self, root: any = None):
        self._root = Node(root)

    def __str__(self) -> str:
        return f"Tree({self.root})"

    def __iter__(self):  # Depth First Search
        yield from self.root

    def breadth_first_search(self) -> list[Node]:
        queue = [self.root]
        while queue:
            node = queue.pop(0)
            yield node
            queue.extend(node.children)

    @property
    def root(self) -> Node:
        return self._root

    @root.setter
    def root(self, value: any):
        self._root = Node(value)

    def get_leaves(self) -> list[Node]:
        output: list[Node] = []
        for node in self:
            if node.is_leaf:
                output.append(node)
        return output
