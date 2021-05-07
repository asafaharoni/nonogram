from __future__ import annotations

from typing import List


class RangeDict(dict):
    def __init__(self):
        super().__init__()
        self.range_starts = []

    def __setitem__(self, keys, value) -> None:
        if isinstance(keys, range):
            self.range_starts.append(keys.start)
            for key in keys:
                super().__setitem__(key, value)
        else:
            raise KeyError(f'RangeDict only accepts key of type range, got {keys} of type {type(keys)}')

    def __getitem__(self, item):
        try:
            return super().__getitem__(item)
        except KeyError:
            return None

    def get_keys(self) -> List[range]:
        return self.range_starts

    def get_values(self):
        return list(set(self.values()))


class ListNode:
    def __init__(self):
        self.next = None
        self.prev = None

    def set_next(self, block) -> None:
        self.next = block

    def get_next(self) -> ListNode:
        return self.next

    def set_prev(self, prev) -> None:
        self.prev = prev

    def get_prev(self) -> ListNode:
        return self.prev

    def is_last(self) -> bool:
        return self.next is None

    def is_first(self) -> bool:
        return self.prev is None


class ListOfNodesIter:
    def __init__(self, node: ListNode, is_reversed: bool = False):
        self.next_node = node
        self.current_node = node.get_next() if is_reversed else node.get_prev()
        self.is_reversed = is_reversed

    def is_reverse_next_possible_(self) -> bool:
        return self.current_node is None and \
                ((self.is_reversed and self.next_node.is_first()) or
                 (not self.is_reversed and self.next_node.is_last() is None))

    def __next__(self) -> ListNode:
        if self.is_reverse_next_possible_():
            raise StopIteration
        if self.next_node:
            self.current_node = self.next_node
            self.set_next_node_()
            return self.current_node
        raise StopIteration

    def reverse(self) -> None:
        self.is_reversed = not self.is_reversed
        self.set_next_node_()

    def set_next_node_(self) -> None:
        if self.current_node is not None:
            if self.is_reversed:
                self.next_node = self.current_node.get_prev()
            else:
                self.next_node = self.current_node.get_next()


class ListOfNodes:
    def __init__(self):
        self.list = []
        self.reverse_iter = False

    def add_node(self, node: ListNode) -> None:
        self.list.append(node)
        if len(self.list) > 1:
            self.list[-2].set_next(self.list[-1])
            self.list[-1].set_prev(self.list[-2])

    def __getitem__(self, item):
        return self.list[item]

    def __iter__(self) -> ListOfNodesIter:
        if self.reverse_iter:
            self.reverse_iter = False
            return ListOfNodesIter(self.list[-1], True)
        else:
            return ListOfNodesIter(self.list[0])

    def __reversed__(self) -> ListOfNodes:
        self.reverse_iter = True
        return self

    def __len__(self) -> int:
        return len(self.list)
