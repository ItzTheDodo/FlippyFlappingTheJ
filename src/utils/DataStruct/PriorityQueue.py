# FlippyFlappingTheJ
# ./src/utils/DataStruct/PriorityQueue.py

from collections.abc import Callable


class PriorityQueue:

    def __init__(self, compare: Callable[[any, any], bool] | None = None):

        self.queue = []
        self._compare = compare

    def __str__(self):
        return ' '.join([str(i) for i in self.queue])

    # for checking if the queue is empty
    def is_empty(self):
        return len(self.queue) == 0

    # for inserting an element in the queue
    def insert(self, data):
        self.queue.append(data)

    # for popping an element based on Priority
    def delete(self):
        max_val = 0
        for i in range(len(self.queue)):
            if self._compare is None:
                if self.queue[i] > self.queue[max_val]:
                    max_val = i
            else:
                if self._compare(self.queue[i], self.queue[max_val]):
                    max_val = i
        item = self.queue[max_val]
        del self.queue[max_val]
        return item

    def __iter__(self):
        return self

    def __next__(self):
        for _ in range(len(self.queue)):
            return self.delete()
        raise StopIteration
