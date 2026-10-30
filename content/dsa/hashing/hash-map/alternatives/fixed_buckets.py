# expect: slow
# Never grows: 4 buckets forever, so chains reach O(n) and the run is O(n^2).
class HashMap:
    def __init__(self):
        self.buckets = [[] for _ in range(4)]
        self.size = 0

    def put(self, key, value):
        bucket = self.buckets[hash(key) % len(self.buckets)]
        for pair in bucket:
            if pair[0] == key:
                pair[1] = value
                return
        bucket.append([key, value])
        self.size += 1

    def get(self, key):
        for pair in self.buckets[hash(key) % len(self.buckets)]:
            if pair[0] == key:
                return pair[1]
        return None

    def remove(self, key):
        bucket = self.buckets[hash(key) % len(self.buckets)]
        for i in range(len(bucket)):
            if bucket[i][0] == key:
                bucket[i] = bucket[-1]
                bucket.pop()
                self.size -= 1
                return True
        return False

    def __len__(self):
        return self.size
