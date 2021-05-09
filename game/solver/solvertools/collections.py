from __future__ import annotations

from typing import List, Optional


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
    def __init__(self, start_node: ListNode = None, stop_node: ListNode = None, is_reversed: bool = False):
        self.next_node = start_node
        if start_node:
            self.current_node = start_node.get_next() if is_reversed else start_node.get_prev()
        self.is_reversed = is_reversed
        self.has_iterated_ = False
        self.initial_is_reversed = is_reversed
        self.stop_node = stop_node

    def __next__(self) -> ListNode:
        if self.next_node is self.stop_node:
            raise StopIteration
        if self.current_node is None:
            if not self.has_iterated_ and self.initial_is_reversed != self.is_reversed:
                raise StopIteration
            else:
                self.has_iterated_ = True
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
        self.stop_node_for_iter = None
        self.start_node_for_iter = None

    def append(self, node: ListNode) -> None:
        self.list.append(node)
        if len(self.list) > 1:
            self.list[-2].set_next(self.list[-1])
            self.list[-1].set_prev(self.list[-2])

    def __getitem__(self, item):
        return self.list[item]

    def __iter__(self) -> ListOfNodesIter:
        if len(self.list) == 0:
            return ListOfNodesIter()
        stop_node = self.stop_node_for_iter
        start_node = self.start_node_for_iter
        reverse_iter = self.reverse_iter
        if start_node is None:
            if self.reverse_iter:
                start_node = self.list[-1]
            else:
                start_node = self.list[0]
        self.stop_node_for_iter = None
        self.start_node_for_iter = None
        self.reverse_iter = False
        return ListOfNodesIter(start_node, stop_node, reverse_iter)

    def reverse(self) -> ListOfNodes:
        self.reverse_iter = True
        return self

    def set_stop_node_for_iter(self, stop_node: ListNode):
        self.stop_node_for_iter = stop_node

    def set_start_node_for_iter(self, start_node: ListNode):
        assert start_node in self.list
        self.start_node_for_iter = start_node

    def __len__(self) -> int:
        return len(self.list)

    def to_list(self):
        return self.list
