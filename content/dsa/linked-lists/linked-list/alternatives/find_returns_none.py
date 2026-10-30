# expect: fail
# find returns None for a missing value instead of -1.
from algoscope import ListNode


class LinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def push_front(self, value):
        self.head = ListNode(value, self.head)
        if self.tail is None:
            self.tail = self.head
        self.size += 1

    def push_back(self, value):
        node = ListNode(value)
        if self.tail is None:
            self.head = node
        else:
            self.tail.next = node
        self.tail = node
        self.size += 1

    def pop_front(self):
        if self.head is None:
            return None
        node = self.head
        self.head = node.next
        if self.head is None:
            self.tail = None
        self.size -= 1
        return node.val

    def find(self, value):
        position, node = 0, self.head
        while node is not None:
            if node.val == value:
                return position
            node = node.next
            position += 1
        return None

    def remove(self, value):
        prev, node = None, self.head
        while node is not None and node.val != value:
            prev, node = node, node.next
        if node is None:
            return False
        if prev is None:
            self.head = node.next
        else:
            prev.next = node.next
        if node is self.tail:
            self.tail = prev
        self.size -= 1
        return True

    def __len__(self):
        return self.size
