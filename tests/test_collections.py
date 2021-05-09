import pytest

from game.solver.solvertools.collections import ListOfNodes, ListNode


class Node(ListNode):
    def __init__(self, val):
        super().__init__()
        self.val = val

    def get_val(self):
        return self.val

    def __eq__(self, other):
        return self.val == other.val


LIST = 'lst'
INITIAL_LIST_SIZE = 15


@pytest.fixture
def data():
    lst = ListOfNodes()
    for i in range(INITIAL_LIST_SIZE):
        lst.append(Node(i))
    return {LIST: lst}


def test_add_node__successful(data):
    lst = data[LIST]
    assert len(lst) == INITIAL_LIST_SIZE
    lst.append(Node(15))
    assert len(lst) == INITIAL_LIST_SIZE + 1
    lst.append(Node(16))
    assert len(lst) == INITIAL_LIST_SIZE + 2


def test_iterate_forward(data):
    lst = data[LIST]
    itr = iter(lst)
    for i in range(INITIAL_LIST_SIZE):
        val = next(itr)
        assert val.get_val() == i
    with pytest.raises(StopIteration):
        next(itr)


def test_iterate_backward(data):
    lst = data[LIST]
    itr = iter(lst.reverse())
    for i in range(INITIAL_LIST_SIZE - 1, -1, -1):
        val = next(itr)
        assert val.get_val() == i
    with pytest.raises(StopIteration):
        next(itr)
    # lst should not be reversed after iter was called.
    itr = iter(lst)
    for i in range(INITIAL_LIST_SIZE):
        val = next(itr)
        assert val.get_val() == i
    with pytest.raises(StopIteration):
        next(itr)


def test_iterate_backwards_single_item():
    lst = ListOfNodes()
    lst.append(Node(0))
    itr = iter(lst)
    val = next(itr)
    assert val.get_val() == 0


def test_iterator_for_loop(data):
    lst = data[LIST]
    for i, node in enumerate(lst):
        assert node.get_val() == i
    for i, node in enumerate(lst.reverse()):
        assert node.get_val() == len(lst) - 1 - i


def test_iterator_reverse(data):
    lst = data[LIST]
    itr = iter(lst)
    itr.reverse()
    with pytest.raises(StopIteration):
        next(itr)
    itr.reverse()
    for i in range(10):
        val = next(itr)
        assert val.get_val() == i
    itr.reverse()
    for i in range(8, -1, -1):
        val = next(itr)
        assert val.get_val() == i
    with pytest.raises(StopIteration):
        next(itr)
    itr.reverse()
    for i in range(1, INITIAL_LIST_SIZE):
        val = next(itr)
        assert val.get_val() == i
    with pytest.raises(StopIteration):
        next(itr)
    itr.reverse()
    assert next(itr).get_val() == 13


def test_iterator_stop_node(data):
    lst = data[LIST]
    for stop_index in range(1, INITIAL_LIST_SIZE):
        lst.set_stop_node_for_iter(lst[INITIAL_LIST_SIZE - stop_index])
        itr = iter(lst)
        for i in range(INITIAL_LIST_SIZE - stop_index):
            val = next(itr)
            assert val.get_val() == i
        with pytest.raises(StopIteration):
            next(itr)
    # Check stop node changes after iteration.
    itr = iter(lst)
    for i in range(INITIAL_LIST_SIZE):
        val = next(itr)
        assert val.get_val() == i
    with pytest.raises(StopIteration):
        next(itr)

