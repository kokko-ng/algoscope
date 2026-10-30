class Node:
    """A list node with fixed fields, so marking nodes (node.seen = True) raises AttributeError."""

    __slots__ = ("next", "val")

    def __init__(self, val, next=None):  # noqa: A002 - the conventional field name
        self.val = val
        self.next = next


def build_fixed(values):
    head = None
    for v in reversed(values):
        head = Node(v, head)
    return head


def with_cycle(values, pos):
    """Build a list and link its tail back to the node at index pos (no cycle when pos is None)."""
    head = build_fixed(values)
    if head is None or pos is None:
        return head
    tail, entry, i = head, None, 0
    while True:
        if i == pos:
            entry = tail
        if tail.next is None:
            break
        tail = tail.next
        i += 1
    tail.next = entry
    return head


def visual():
    return (with_cycle([3, 8, 5, 1, 9, 4, 7], 2),)


def fixed():
    return [
        (None,),
        (with_cycle([1], None),),
        (with_cycle([1], 0),),
        (with_cycle([1, 2], 0),),
        (with_cycle([1, 2], 1),),
        (with_cycle([1, 2, 3], None),),
        (with_cycle([1, 2, 3, 4], 3),),
    ]


def cases(n, rng):
    values = rng.sample(range(10 * n + 10), n)
    pos = rng.randrange(n) if n and rng.random() < 0.7 else None
    return [(with_cycle(values, pos),)]


def bench(n, rng):
    return [(with_cycle(list(range(n)), n // 3),)]
