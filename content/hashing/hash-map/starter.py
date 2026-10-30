class HashMap:
    def __init__(self):
        self.buckets = [[] for _ in range(4)]
        self.size = 0

    def put(self, key, value):
        # store value under key, overwriting any old value
        pass

    def get(self, key):
        # return the value for key, or None
        pass

    def remove(self, key):
        # delete key; return True if it was present, else False
        pass

    def __len__(self):
        return self.size
