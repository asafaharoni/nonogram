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


@pytest.fixture
def data():
    lst = ListOfNodes()
    for i in range(15):
        lst.add_node(Node(i))
    return {LIST: lst}


def test_add_node__successful(data):
    lst = data[LIST]
    assert len(lst) == 15
    lst.add_node(Node(15))
    assert len(lst) == 16
    lst.add_node(Node(16))
    assert len(lst) == 17


def test_iterate_forward(data):
    lst = data[LIST]
    itr = iter(lst)
    for i in range(15):
        val = next(itr)
        assert val.get_val() == i
    with pytest.raises(StopIteration):
        next(itr)


def test_iterate_backward(data):
    lst = data[LIST]
    itr = iter(reversed(lst))
    for i in range(14, -1, -1):
        val = next(itr)
        assert val.get_val() == i
    with pytest.raises(StopIteration):
        next(itr)


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
    for i in range(1, 15):
        val = next(itr)
        assert val.get_val() == i
    with pytest.raises(StopIteration):
        next(itr)
    itr.reverse()
    assert next(itr).get_val() == 13
