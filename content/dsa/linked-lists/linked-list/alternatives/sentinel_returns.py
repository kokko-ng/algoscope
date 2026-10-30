# expect: pass
# Literal reading: a local placeholder node in remove, and push methods that return the new length.
from algoscope import ListNode


class LinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.count = 0

    def push_front(self, value):
        node = ListNode(value, self.head)
        self.head = node
        if self.count == 0:
            self.tail = node
        self.count += 1
        return self.count

    def push_back(self, value):
        node = ListNode(value)
        if self.count == 0:
            self.head = self.tail = node
        else:
            self.tail.next = node
            self.tail = node
        self.count += 1
        return self.count

    def pop_front(self):
        if self.count == 0:
            return None
        value = self.head.val
        self.head = self.head.next
        self.count -= 1
        if self.count == 0:
            self.tail = None
        return value

    def find(self, value):
        node = self.head
        for position in range(self.count):
            if node.val == value:
                return position
            node = node.next
        return -1

    def remove(self, value):
        before = ListNode(None, self.head)
        prev = before
        while prev.next is not None:
            if prev.next.val == value:
                if prev.next is self.tail:
                    self.tail = prev if prev is not before else None
                prev.next = prev.next.next
                self.head = before.next
                self.count -= 1
                return True
            prev = prev.next
        return False

    def __len__(self):
        return self.count
