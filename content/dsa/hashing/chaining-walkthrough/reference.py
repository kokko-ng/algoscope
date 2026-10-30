class ChainedMap:
    def __init__(self):
        self.buckets = [[] for _ in range(5)]

    def put(self, key, value):
        index = hash(key) % len(self.buckets)
        bucket = self.buckets[index]
        for pair in bucket:
            if pair[0] == key:
                pair[1] = value
                return
        bucket.append([key, value])

    def get(self, key):
        bucket = self.buckets[hash(key) % len(self.buckets)]
        for pair in bucket:
            if pair[0] == key:
                return pair[1]
        return None
