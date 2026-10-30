# expect: slow
# No tail pointer: push_back walks from the head every time, so n pushes cost O(n^2).
from algoscope import ListNode


class LinkedList:
    def __init__(self):
        self.head = None
        self.size = 0

    def push_front(self, value):
        self.head = ListNode(value, self.head)
        self.size += 1

    def push_back(self, value):
        node = ListNode(value)
        if self.head is None:
            self.head = node
        else:
            last = self.head
            while last.next is not None:
                last = last.next
            last.next = node
        self.size += 1

    def pop_front(self):
        if self.head is None:
            return None
        node = self.head
        self.head = node.next
        self.size -= 1
        return node.val

    def find(self, value):
        position, node = 0, self.head
        while node is not None:
            if node.val == value:
                return position
            node = node.next
            position += 1
        return -1

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
        self.size -= 1
        return True

    def __len__(self):
        return self.size
