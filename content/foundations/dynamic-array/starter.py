class DynArray:
    def __init__(self):
        self.capacity = 1
        self.size = 0
        self.slots = [None] * self.capacity

    def append(self, value):
        pass

    def get(self, i):
        pass

    def set(self, i, value):
        pass

    def pop(self):
        pass

    def __len__(self):
        return self.size
