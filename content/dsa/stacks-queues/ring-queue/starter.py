class RingQueue:
    def __init__(self, capacity=4):
        self.slots = [None] * capacity
        self.front = 0
        self.size = 0

    def enqueue(self, value):
        pass

    def dequeue(self):
        pass

    def peek(self):
        pass

    def __len__(self):
        return self.size
