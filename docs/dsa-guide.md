# Data structures and algorithms: a guide with Python samples

## About this guide

This guide explains the data structures and algorithms in the algoscope curriculum.
The text uses ASD-STE100 Simplified Technical English.
Each sentence is short and has one instruction or one fact.
Technical names, for example "array", "heap" and "binary search", are used as they are.

Each section gives:

1. The purpose of the data structure or algorithm.
2. The procedure that it uses.
3. A table of its cost.
4. A Python sample. The sample ends with `assert` lines that show the correct results.

NOTE: The test `harness/tests/test_guide.py` runs each Python sample in this guide.
If you change a sample, run the test again.

## Contents

1. [How to measure cost](#how-to-measure-cost)
2. [Dynamic arrays](#dynamic-arrays)
3. [Two pointers](#two-pointers)
4. [Sliding window](#sliding-window)
5. [Hash maps and prefix sums](#hash-maps-and-prefix-sums)
6. [Sorting](#sorting)
7. [Binary search](#binary-search)
8. [Linked lists](#linked-lists)
9. [Stacks and queues](#stacks-and-queues)
10. [Recursion and backtracking](#recursion-and-backtracking)
11. [Binary trees and binary search trees](#binary-trees-and-binary-search-trees)
12. [Heaps](#heaps)
13. [Tries](#tries)
14. [Graphs](#graphs)
15. [Dynamic programming](#dynamic-programming)
16. [Greedy algorithms and intervals](#greedy-algorithms-and-intervals)
17. [Balanced trees](#balanced-trees)
18. [Range queries](#range-queries)
19. [Bit manipulation](#bit-manipulation)
20. [String matching](#string-matching)
21. [Capstone: route planning on a grid](#capstone-route-planning-on-a-grid)
22. [How to select a data structure](#how-to-select-a-data-structure)

## How to measure cost

An algorithm does a number of steps.
The number of steps changes when the size of the input changes.
We use the letter n for the size of the input.

Big-O notation shows how fast the number of steps increases when n increases.
It does not show the exact number of steps.
It shows only the largest term, without constants.

The table shows the usual cost classes, from fast to slow.

| Cost | Name | Example |
|---|---|---|
| O(1) | constant | Get an item from a list by its index |
| O(log n) | logarithmic | Binary search in a sorted list |
| O(n) | linear | Find the largest value in a list |
| O(n log n) | linearithmic | Merge sort |
| O(n^2) | quadratic | Compare each pair of items |
| O(2^n) | exponential | Make all subsets of a set |

To find the cost of a function, do these steps:

1. Count the steps that each line does for one input.
2. Find the loops. Multiply the cost of a loop body by the number of times that the loop runs.
3. Add the costs of the parts that run one after the other.
4. Keep only the term that increases fastest. Remove the constants.

The two functions below give the same result.
The first function compares each pair of items, so its cost is O(n^2).
The second function reads each item one time, so its cost is O(n).

```python
def has_duplicate_slow(items):
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j]:
                return True
    return False


def has_duplicate_fast(items):
    seen = set()
    for item in items:
        if item in seen:
            return True
        seen.add(item)
    return False


assert has_duplicate_slow([3, 1, 4, 1]) is True
assert has_duplicate_fast([3, 1, 4, 1]) is True
assert has_duplicate_fast([2, 7, 1, 8]) is False
```

CAUTION: Some Python operations look like one step, but they do many steps.
For example, `x in some_list`, `some_list.insert(0, x)` and `some_list[a:b]` each have a cost of O(n).
algoscope counts these hidden steps.

## Dynamic arrays

A dynamic array keeps items in a row of memory slots.
You can get any item by its index in O(1).
The Python `list` is a dynamic array.

The array has a capacity. The capacity is the number of slots.
The size is the number of slots that contain items.
When the size is equal to the capacity, the array must increase its capacity.

To add an item at the end, do these steps:

1. If the array is full, make a new block of slots that is two times larger.
2. Copy each item into the new block.
3. Put the new item in the first empty slot.
4. Increase the size by 1.

A copy has a cost of O(n), but it occurs only after the capacity doubles.
Thus, n additions have a total cost of O(n).
The average cost of one addition is O(1). This is "amortized" cost.

| Operation | Cost |
|---|---|
| Get or set by index | O(1) |
| Add at the end | O(1) amortized |
| Remove from the end | O(1) |
| Add or remove at the start | O(n) |

```python
class DynArray:
    def __init__(self):
        self.capacity = 1
        self.size = 0
        self.slots = [None] * self.capacity

    def append(self, value):
        if self.size == self.capacity:
            bigger = [None] * (self.capacity * 2)
            for i in range(self.size):
                bigger[i] = self.slots[i]
            self.slots = bigger
            self.capacity *= 2
        self.slots[self.size] = value
        self.size += 1

    def get(self, index):
        if not 0 <= index < self.size:
            raise IndexError(index)
        return self.slots[index]

    def pop(self):
        if self.size == 0:
            raise IndexError("pop from empty array")
        self.size -= 1
        value = self.slots[self.size]
        self.slots[self.size] = None
        return value


array = DynArray()
for value in [5, 8, 2, 9, 4]:
    array.append(value)
assert array.capacity == 8
assert array.get(3) == 9
assert array.pop() == 4
assert array.size == 4
```

NOTE: If the capacity increases by a constant (for example, 1 slot) and not by a factor, n additions have a cost of O(n^2).

## Two pointers

The two pointers procedure uses two indices in one sequence.
The indices move toward each other, or they move in the same direction.
Each move removes part of the search space.
Thus, a loop in a loop (O(n^2)) can become one loop (O(n)).

Use two pointers when:

- The input is sorted.
- You must find a pair of items that agree with a condition.
- You must change a list in place.

### Pair sum in a sorted list

To find two items with a given sum, do these steps:

1. Put the left pointer at the start. Put the right pointer at the end.
2. Calculate the sum of the two items.
3. If the sum is too small, move the left pointer one position to the right.
4. If the sum is too large, move the right pointer one position to the left.
5. Stop when the sum is correct or when the pointers meet.

The cost is O(n), because each step moves one pointer.

```python
def pair_sum(nums, target):
    left, right = 0, len(nums) - 1
    while left < right:
        total = nums[left] + nums[right]
        if total == target:
            return [left, right]
        if total < target:
            left += 1
        else:
            right -= 1
    return [-1, -1]


assert pair_sum([1, 3, 4, 6, 8, 11, 14], 17) == [1, 6]
assert pair_sum([1, 2, 3], 10) == [-1, -1]
```

### Remove duplicates from a sorted list

The slow pointer shows the end of the part without duplicates.
The fast pointer reads each item one time.

```python
def remove_duplicates(nums):
    slow = 0
    for fast in range(len(nums)):
        if fast == 0 or nums[fast] != nums[slow - 1]:
            nums[slow] = nums[fast]
            slow += 1
    return slow


values = [1, 1, 2, 3, 3, 3, 4]
length = remove_duplicates(values)
assert values[:length] == [1, 2, 3, 4]
```

## Sliding window

A sliding window is a range of adjacent items.
The window moves from left to right across the input.
When the window moves, you add the new item and remove the old item.
You do not calculate the full window again.

Use a sliding window when you must find the best range of adjacent items.

| Window type | Cost |
|---|---|
| Fixed size k | O(n) |
| Variable size | O(n), because each pointer moves at most n times |

### Window with a fixed size

```python
def max_window_sum(nums, k):
    window = sum(nums[:k])
    best = window
    for right in range(k, len(nums)):
        window += nums[right] - nums[right - k]
        best = max(best, window)
    return best


assert max_window_sum([2, 1, 5, 1, 3, 2], 3) == 9
```

### Window with a variable size

To find the longest part of a string without repeated characters, do these steps:

1. Move the right edge of the window one character at a time.
2. If the new character is already in the window, move the left edge past its last position.
3. Record the length of the window after each step.

```python
def longest_unique(text):
    last_seen = {}
    left = 0
    best = 0
    for right, char in enumerate(text):
        if char in last_seen and last_seen[char] >= left:
            left = last_seen[char] + 1
        last_seen[char] = right
        best = max(best, right - left + 1)
    return best


assert longest_unique("abcabcbb") == 3
assert longest_unique("pwwkew") == 3
assert longest_unique("") == 0
```

## Hash maps and prefix sums

A hash map keeps pairs of keys and values.
A hash function changes each key into a bucket number.
Thus, you can find, add or remove a key in O(1) on average.
The Python `dict` and `set` are hash tables.

Two keys can go into the same bucket. This is a collision.
With chaining, each bucket holds a list of pairs.
When the number of pairs becomes too large, the table doubles its number of buckets and puts each pair in its new bucket.

| Operation | Average cost | Worst cost |
|---|---|---|
| Put, get, remove | O(1) | O(n) |

```python
class ChainedHashMap:
    def __init__(self):
        self.buckets = [[] for _ in range(8)]
        self.size = 0

    def _bucket(self, key):
        return self.buckets[hash(key) % len(self.buckets)]

    def put(self, key, value):
        bucket = self._bucket(key)
        for pair in bucket:
            if pair[0] == key:
                pair[1] = value
                return
        bucket.append([key, value])
        self.size += 1
        if self.size > 2 * len(self.buckets):
            self._grow()

    def get(self, key, default=None):
        for stored_key, value in self._bucket(key):
            if stored_key == key:
                return value
        return default

    def remove(self, key):
        bucket = self._bucket(key)
        for i, pair in enumerate(bucket):
            if pair[0] == key:
                bucket.pop(i)
                self.size -= 1
                return True
        return False

    def _grow(self):
        pairs = [pair for bucket in self.buckets for pair in bucket]
        self.buckets = [[] for _ in range(2 * len(self.buckets))]
        for key, value in pairs:
            self._bucket(key).append([key, value])


table = ChainedHashMap()
for number in range(40):
    table.put(f"key{number}", number)
assert table.get("key17") == 17
assert table.remove("key17") is True
assert table.get("key17") is None
assert len(table.buckets) > 8
```

### Find a pair with a dictionary

Use a dictionary to record the index of each value that you read.
For each new value, look for the value that completes the target.

```python
def two_sum(nums, target):
    index_of = {}
    for i, value in enumerate(nums):
        if target - value in index_of:
            return [index_of[target - value], i]
        index_of[value] = i
    return [-1, -1]


assert two_sum([2, 7, 11, 15], 9) == [0, 1]
```

### Prefix sums

A prefix sum is the sum of all items from the start to a position.
The sum of a range is the difference between two prefix sums.

To count the ranges that have a sum equal to k, do these steps:

1. Keep the prefix sum of the items that you read.
2. Keep a dictionary that counts each prefix sum that you found before.
3. For each position, add the count of the earlier prefix sum that is equal to (prefix sum - k).

The cost is O(n).

```python
def count_ranges_with_sum(nums, k):
    counts = {0: 1}
    prefix = 0
    found = 0
    for value in nums:
        prefix += value
        found += counts.get(prefix - k, 0)
        counts[prefix] = counts.get(prefix, 0) + 1
    return found


assert count_ranges_with_sum([1, 1, 1], 2) == 2
assert count_ranges_with_sum([1, 2, 3, -3, 3], 3) == 5
```

## Sorting

A sorting algorithm puts items in order.
Different algorithms have different costs and different properties.
A stable sort keeps equal items in their initial order.

| Algorithm | Best | Average | Worst | Extra memory | Stable |
|---|---|---|---|---|---|
| Insertion sort | O(n) | O(n^2) | O(n^2) | O(1) | Yes |
| Merge sort | O(n log n) | O(n log n) | O(n log n) | O(n) | Yes |
| Quicksort | O(n log n) | O(n log n) | O(n^2) | O(log n) | No |
| Counting sort | O(n + k) | O(n + k) | O(n + k) | O(k) | Yes |

NOTE: For counting sort, k is the range of the values.

### Insertion sort

Insertion sort moves each item to the left until the item is in the correct position.
It is fast for small lists and for lists that are almost sorted.

```python
def insertion_sort(items):
    for i in range(1, len(items)):
        current = items[i]
        j = i - 1
        while j >= 0 and items[j] > current:
            items[j + 1] = items[j]
            j -= 1
        items[j + 1] = current
    return items


assert insertion_sort([5, 2, 4, 6, 1, 3]) == [1, 2, 3, 4, 5, 6]
```

### Merge sort

Merge sort uses the "divide and conquer" procedure:

1. Divide the list into two halves.
2. Sort each half with the same procedure.
3. Merge the two sorted halves into one sorted list.

There are log n levels of division. Each level does O(n) work to merge.
Thus, the cost is O(n log n).

```python
def merge_sort(items):
    if len(items) <= 1:
        return items
    middle = len(items) // 2
    left = merge_sort(items[:middle])
    right = merge_sort(items[middle:])
    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


assert merge_sort([38, 27, 43, 3, 9, 82, 10]) == [3, 9, 10, 27, 38, 43, 82]
```

### Quicksort

Quicksort selects a pivot and divides the list in place:

1. Move all items that are smaller than the pivot to the left side.
2. Put the pivot after them.
3. Sort the left side and the right side with the same procedure.

If the pivot is always the smallest or the largest item, the cost becomes O(n^2).
A random pivot or the middle item decreases this risk.

```python
def quicksort(items, low=0, high=None):
    if high is None:
        high = len(items) - 1
    if low >= high:
        return items
    middle = (low + high) // 2
    items[middle], items[high] = items[high], items[middle]
    pivot = items[high]
    boundary = low
    for scan in range(low, high):
        if items[scan] < pivot:
            items[scan], items[boundary] = items[boundary], items[scan]
            boundary += 1
    items[boundary], items[high] = items[high], items[boundary]
    quicksort(items, low, boundary - 1)
    quicksort(items, boundary + 1, high)
    return items


assert quicksort([9, 4, 7, 1, 8, 2, 2]) == [1, 2, 2, 4, 7, 8, 9]
```

### Counting sort

Counting sort does not compare items.
It counts how many times each value occurs, then it writes the values in order.
Use it only when the values are small integers.

```python
def counting_sort(values, max_value):
    counts = [0] * (max_value + 1)
    for value in values:
        counts[value] += 1
    result = []
    for value, count in enumerate(counts):
        result.extend([value] * count)
    return result


assert counting_sort([4, 1, 3, 1, 0, 4], 4) == [0, 1, 1, 3, 4, 4]
```

## Binary search

Binary search finds a value in a sorted list.
Each step compares the middle item with the target and removes half of the list.
Thus, the cost is O(log n).

To find the first index with a value that is equal to or larger than the target, do these steps:

1. Set `lo` to 0. Set `hi` to the length of the list.
2. While `lo` is less than `hi`, calculate `mid`.
3. If the item at `mid` is less than the target, set `lo` to `mid + 1`.
4. If not, set `hi` to `mid`.
5. When the loop stops, `lo` is the result.

```python
def lower_bound(nums, target):
    lo, hi = 0, len(nums)
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo


assert lower_bound([1, 3, 3, 5, 8], 3) == 1
assert lower_bound([1, 3, 3, 5, 8], 4) == 3
assert lower_bound([1, 3, 3, 5, 8], 9) == 5
```

CAUTION: Make sure that each loop step makes the range smaller.
If it does not, the loop does not stop.

### Binary search on the answer

You can also use binary search when the answer is a number and a check is "monotonic".
Monotonic means: if the check is true for x, it is also true for each value larger than x.

For example, find the smallest daily capacity that ships all packages in a given number of days.
The packages must stay in their order.

```python
def days_needed(weights, capacity):
    days, load = 1, 0
    for weight in weights:
        if load + weight > capacity:
            days += 1
            load = 0
        load += weight
    return days


def min_capacity(weights, days):
    lo, hi = max(weights), sum(weights)
    while lo < hi:
        mid = (lo + hi) // 2
        if days_needed(weights, mid) <= days:
            hi = mid
        else:
            lo = mid + 1
    return lo


assert min_capacity([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 5) == 15
```

The cost is O(n log S), where S is the sum of the weights.

## Linked lists

A linked list is a chain of nodes.
Each node holds a value and a reference to the next node.
You can add or remove a node in O(1) if you have a reference to the node before it.
You cannot get an item by its index in O(1). You must follow the chain.

| Operation | Cost |
|---|---|
| Add or remove at the head | O(1) |
| Add at the tail, with a tail reference | O(1) |
| Find a value | O(n) |
| Get the item at index i | O(i) |

### Reverse a linked list

Use three references: `prev`, `current` and `following`.
Change the direction of each link, one node at a time.

```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def build_list(values):
    head = None
    for value in reversed(values):
        head = ListNode(value, head)
    return head


def to_list(head):
    values = []
    while head is not None:
        values.append(head.val)
        head = head.next
    return values


def reverse(head):
    prev = None
    current = head
    while current is not None:
        following = current.next
        current.next = prev
        prev = current
        current = following
    return prev


assert to_list(reverse(build_list([1, 2, 3, 4]))) == [4, 3, 2, 1]
assert reverse(None) is None
```

### Find a cycle with a slow and a fast pointer

The slow pointer moves one node at each step. The fast pointer moves two nodes.
If the list has a cycle, the fast pointer meets the slow pointer.
This procedure uses O(1) extra memory.

```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def has_cycle(head):
    slow = fast = head
    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            return True
    return False


nodes = [ListNode(value) for value in range(5)]
for first, second in zip(nodes, nodes[1:]):
    first.next = second
assert has_cycle(nodes[0]) is False
nodes[-1].next = nodes[2]
assert has_cycle(nodes[0]) is True
```

## Stacks and queues

A stack is "last in, first out" (LIFO). You add and remove items at the top.
A queue is "first in, first out" (FIFO). You add items at the back and remove them at the front.

| Operation | Stack (Python `list`) | Queue (`collections.deque`) |
|---|---|---|
| Add | `append`, O(1) | `append`, O(1) |
| Remove | `pop()`, O(1) | `popleft()`, O(1) |

CAUTION: Do not use `list.pop(0)` for a queue. It moves all the other items, so its cost is O(n).

### Check brackets with a stack

```python
def brackets_match(text):
    closers = {")": "(", "]": "[", "}": "{"}
    stack = []
    for char in text:
        if char in "([{":
            stack.append(char)
        elif char in closers:
            if not stack or stack.pop() != closers[char]:
                return False
    return not stack


assert brackets_match("{[()()]}") is True
assert brackets_match("([)]") is False
assert brackets_match("((") is False
```

### Next larger value with a monotonic stack

A monotonic stack keeps its items in order.
For each new value, remove the smaller values from the stack. The new value is their answer.
Each index goes into the stack one time and comes out one time. Thus, the cost is O(n).

```python
def next_greater(nums):
    answer = [-1] * len(nums)
    stack = []
    for i, value in enumerate(nums):
        while stack and nums[stack[-1]] < value:
            answer[stack.pop()] = value
        stack.append(i)
    return answer


assert next_greater([2, 1, 2, 4, 3]) == [4, 2, 4, -1, -1]
```

### Use a queue

```python
from collections import deque

queue = deque()
for task in ["read", "parse", "write"]:
    queue.append(task)
assert queue.popleft() == "read"
assert list(queue) == ["parse", "write"]
```

## Recursion and backtracking

A recursive function calls itself with a smaller problem.
Each recursive function must have two parts:

1. A base case. The base case gives the answer without a recursive call.
2. A recursive step. The recursive step makes the problem smaller and calls the function.

Each call uses memory on the call stack.
Python stops when the depth is more than about 1000 calls.

### Memoization

If a recursive function calculates the same value many times, record each result.
This is memoization. It can change an exponential cost into a linear cost.

```python
from functools import cache


@cache
def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)


assert fib(10) == 55
assert fib(90) == 2880067194370816120
```

### Backtracking

Backtracking builds a solution one choice at a time.
After it examines a choice, it removes that choice and tries the next choice.

To make all subsets of a list, do these steps for each item:

1. Include the item and continue with the next item.
2. Remove the item and continue with the next item.

There are 2^n subsets. Thus, the cost is O(n x 2^n).

```python
def subsets(items):
    result = []
    current = []

    def choose(index):
        if index == len(items):
            result.append(current.copy())
            return
        current.append(items[index])
        choose(index + 1)
        current.pop()
        choose(index + 1)

    choose(0)
    return result


assert sorted(subsets([1, 2, 3])) == [[], [1], [1, 2], [1, 2, 3], [1, 3], [2], [2, 3], [3]]
```

```python
def permutations(items):
    result = []
    used = [False] * len(items)
    current = []

    def extend():
        if len(current) == len(items):
            result.append(current.copy())
            return
        for i, item in enumerate(items):
            if not used[i]:
                used[i] = True
                current.append(item)
                extend()
                current.pop()
                used[i] = False

    extend()
    return result


assert len(permutations([1, 2, 3, 4])) == 24
```

## Binary trees and binary search trees

A binary tree is a set of nodes. Each node has a value and at most two children: left and right.
The top node is the root. A node without children is a leaf.
The height is the number of levels.

A binary search tree (BST) has one more rule:
all values in the left subtree are smaller than the node, and all values in the right subtree are larger.
Each comparison removes one subtree from the search.

| Operation | Balanced BST | Unbalanced BST |
|---|---|---|
| Find, add, remove | O(log n) | O(n) |
| In-order traversal | O(n) | O(n) |

NOTE: If you add sorted values to a plain BST, the tree becomes a chain. The cost becomes O(n).
Self-balancing trees (for example, AVL trees) prevent this. See [Balanced trees](#balanced-trees).

### Traversals

There are three depth-first orders:

- Pre-order: node, left subtree, right subtree.
- In-order: left subtree, node, right subtree. In a BST, this order gives the values from smallest to largest.
- Post-order: left subtree, right subtree, node.

A breadth-first traversal reads the tree one level at a time. It uses a queue.

```python
from collections import deque


class TreeNode:
    def __init__(self, val, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def insert(root, value):
    if root is None:
        return TreeNode(value)
    if value < root.val:
        root.left = insert(root.left, value)
    elif value > root.val:
        root.right = insert(root.right, value)
    return root


def contains(root, value):
    while root is not None:
        if value == root.val:
            return True
        root = root.left if value < root.val else root.right
    return False


def inorder(root):
    if root is None:
        return []
    return inorder(root.left) + [root.val] + inorder(root.right)


def level_order(root):
    levels = []
    queue = deque([root] if root else [])
    while queue:
        level = []
        for _ in range(len(queue)):
            node = queue.popleft()
            level.append(node.val)
            for child in (node.left, node.right):
                if child is not None:
                    queue.append(child)
        levels.append(level)
    return levels


def height(root):
    if root is None:
        return 0
    return 1 + max(height(root.left), height(root.right))


root = None
for value in [50, 30, 70, 20, 40, 85, 35]:
    root = insert(root, value)
assert inorder(root) == [20, 30, 35, 40, 50, 70, 85]
assert level_order(root) == [[50], [30, 70], [20, 40, 85], [35]]
assert contains(root, 35) is True
assert contains(root, 36) is False
assert height(root) == 4
```

## Heaps

A heap is a binary tree that you keep in a list.
For the item at index i, the children are at indices 2i + 1 and 2i + 2.
In a min-heap, each parent is smaller than or equal to its children.
Thus, the smallest item is always at index 0.

To add an item ("sift up"), do these steps:

1. Put the item at the end of the list.
2. While the item is smaller than its parent, swap the item with its parent.

To remove the smallest item ("sift down"), do these steps:

1. Move the last item to index 0.
2. While the item is larger than one of its children, swap it with the smaller child.

| Operation | Cost |
|---|---|
| Peek at the smallest item | O(1) |
| Push, pop | O(log n) |
| Build a heap from n items (`heapify`) | O(n) |

```python
class MinHeap:
    def __init__(self):
        self.items = []

    def push(self, value):
        self.items.append(value)
        child = len(self.items) - 1
        while child > 0:
            parent = (child - 1) // 2
            if self.items[parent] <= self.items[child]:
                break
            self.items[parent], self.items[child] = self.items[child], self.items[parent]
            child = parent

    def pop(self):
        items = self.items
        smallest = items[0]
        last = items.pop()
        if items:
            items[0] = last
            parent = 0
            while True:
                child = 2 * parent + 1
                if child >= len(items):
                    break
                if child + 1 < len(items) and items[child + 1] < items[child]:
                    child += 1
                if items[parent] <= items[child]:
                    break
                items[parent], items[child] = items[child], items[parent]
                parent = child
        return smallest


heap = MinHeap()
for value in [5, 3, 8, 1, 9, 2]:
    heap.push(value)
assert [heap.pop() for _ in range(6)] == [1, 2, 3, 5, 8, 9]
```

### Use heapq

The Python module `heapq` gives min-heap functions for a list.
To find the k largest items, keep a min-heap of size k.
The cost is O(n log k).

```python
import heapq


def k_largest(nums, k):
    heap = []
    for value in nums:
        heapq.heappush(heap, value)
        if len(heap) > k:
            heapq.heappop(heap)
    return sorted(heap, reverse=True)


assert k_largest([3, 1, 5, 12, 2, 11], 3) == [12, 11, 5]
```

## Tries

A trie (prefix tree) keeps a set of strings.
Each node is one character. Each path from the root spells a prefix.
A flag on a node shows that a word ends there.

The cost of each operation is O(L), where L is the length of the word.
The cost does not change with the number of words in the trie.

```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.end = False


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for char in word:
            node = node.children.setdefault(char, TrieNode())
        node.end = True

    def _walk(self, text):
        node = self.root
        for char in text:
            node = node.children.get(char)
            if node is None:
                return None
        return node

    def search(self, word):
        node = self._walk(word)
        return node is not None and node.end

    def starts_with(self, prefix):
        return self._walk(prefix) is not None


trie = Trie()
for word in ["car", "cart", "cat"]:
    trie.insert(word)
assert trie.search("car") is True
assert trie.search("ca") is False
assert trie.starts_with("ca") is True
assert trie.starts_with("dog") is False
```

## Graphs

A graph is a set of vertices (nodes) and edges (connections).
An edge can have a direction, and it can have a weight.
We use V for the number of vertices and E for the number of edges.

An adjacency list keeps, for each vertex, a list of its neighbours.
A Python dictionary of lists is a good adjacency list.

| Algorithm | Purpose | Cost |
|---|---|---|
| Breadth-first search (BFS) | Shortest paths when all edges have the same weight | O(V + E) |
| Depth-first search (DFS) | Reachability, components, cycles | O(V + E) |
| Topological sort | Order of tasks with dependencies | O(V + E) |
| Dijkstra | Shortest paths with weights that are not negative | O((V + E) log V) |
| Union-find | Connected groups while edges are added | Almost O(1) for each operation |

### Breadth-first search

BFS starts at one vertex and reads the graph one layer at a time.
It uses a queue. It marks each vertex as visited when the vertex goes into the queue.
Thus, each vertex goes into the queue only one time.

```python
from collections import deque


def bfs_distances(graph, start):
    distance = {start: 0}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for neighbour in graph[node]:
            if neighbour not in distance:
                distance[neighbour] = distance[node] + 1
                queue.append(neighbour)
    return distance


graph = {"A": ["B", "C"], "B": ["D"], "C": ["D", "E"], "D": ["F"], "E": ["F"], "F": []}
assert bfs_distances(graph, "A") == {"A": 0, "B": 1, "C": 1, "D": 2, "E": 2, "F": 3}
```

### Depth-first search

DFS goes as deep as possible on one path. Then it goes back and tries the next path.
This sample uses a stack and not recursion, so a deep graph does not stop Python.

```python
def path_exists(graph, source, target):
    seen = set()
    stack = [source]
    while stack:
        node = stack.pop()
        if node == target:
            return True
        if node in seen:
            continue
        seen.add(node)
        stack.extend(graph[node])
    return False


graph = {1: [2], 2: [3], 3: [], 4: [1]}
assert path_exists(graph, 1, 3) is True
assert path_exists(graph, 3, 1) is False
```

### Topological sort

A topological order puts each vertex before all the vertices that it points to.
It exists only if the graph has no cycle.

Kahn's algorithm does these steps:

1. For each vertex, count the edges that go into it.
2. Put each vertex with zero incoming edges in a queue.
3. Remove a vertex from the queue and add it to the order.
4. Decrease the count of each neighbour by 1. If a count becomes zero, put that neighbour in the queue.
5. If the order does not contain all the vertices, the graph has a cycle.

```python
from collections import deque


def topological_order(graph):
    incoming = dict.fromkeys(graph, 0)
    for node in graph:
        for after in graph[node]:
            incoming[after] += 1
    queue = deque(node for node, count in incoming.items() if count == 0)
    order = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for after in graph[node]:
            incoming[after] -= 1
            if incoming[after] == 0:
                queue.append(after)
    return order if len(order) == len(graph) else None


tasks = {"fetch": ["build"], "build": ["test", "package"], "test": ["release"], "package": ["release"], "release": []}
order = topological_order(tasks)
assert order.index("build") < order.index("test") < order.index("release")
assert topological_order({"a": ["b"], "b": ["a"]}) is None
```

### Dijkstra's algorithm

Dijkstra's algorithm finds the shortest distance from one vertex to all the others.
All edge weights must be zero or more.
Next, it always takes the vertex with the smallest known distance. A heap gives this vertex fast.

```python
import heapq


def dijkstra(graph, start):
    distance = {start: 0}
    heap = [(0, start)]
    while heap:
        dist, node = heapq.heappop(heap)
        if dist > distance[node]:
            continue
        for neighbour, weight in graph[node]:
            candidate = dist + weight
            if candidate < distance.get(neighbour, float("inf")):
                distance[neighbour] = candidate
                heapq.heappush(heap, (candidate, neighbour))
    return distance


roads = {"A": [("B", 4), ("C", 1)], "C": [("B", 2), ("D", 7)], "B": [("D", 1)], "D": []}
assert dijkstra(roads, "A") == {"A": 0, "B": 3, "C": 1, "D": 4}
```

CAUTION: Do not use Dijkstra's algorithm when an edge has a negative weight. The result can be incorrect.

### Union-find

Union-find (disjoint set union) keeps a set of groups.
`find` gives the representative of the group of an item.
`union` joins two groups.

Two methods keep the trees flat:

- Path compression: `find` connects each node on the path directly to the root.
- Union by size: `union` attaches the smaller tree below the larger tree.

With the two methods, each operation is almost O(1).

```python
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.size = [1] * n
        self.groups = n

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a, b):
        root_a, root_b = self.find(a), self.find(b)
        if root_a == root_b:
            return False
        if self.size[root_a] < self.size[root_b]:
            root_a, root_b = root_b, root_a
        self.parent[root_b] = root_a
        self.size[root_a] += self.size[root_b]
        self.groups -= 1
        return True


groups = UnionFind(6)
groups.union(0, 1)
groups.union(1, 2)
groups.union(3, 4)
assert groups.find(0) == groups.find(2)
assert groups.find(0) != groups.find(3)
assert groups.groups == 3
```

## Dynamic programming

Dynamic programming (DP) solves a problem with two properties:

- Overlapping subproblems: the same smaller problem occurs many times.
- Optimal substructure: the best answer comes from the best answers to smaller problems.

There are two methods:

1. Top-down: write the recursion, then record each result (memoization).
2. Bottom-up: fill a table from the smallest problems to the largest (tabulation).

To write a DP solution, do these steps:

1. Define the state. Write what `dp[i]` (or `dp[i][j]`) means in one sentence.
2. Write the transition. Show how a state comes from smaller states.
3. Write the base cases.
4. Find the order that fills each state after the states that it needs.
5. Find the answer in the table.

### One-dimensional DP

Find the number of ways to climb n stairs, with steps of 1 or 2 stairs.
`ways[i]` is the number of ways to reach stair i.

```python
def climb_stairs(n):
    ways = [1, 1] + [0] * max(0, n - 1)
    for i in range(2, n + 1):
        ways[i] = ways[i - 1] + ways[i - 2]
    return ways[n]


assert climb_stairs(5) == 8
```

### Two-dimensional DP

The longest common subsequence (LCS) of two strings is the longest sequence of characters that is in both strings, in the same order.
`dp[i][j]` is the LCS length of the first i characters of `a` and the first j characters of `b`.
The cost is O(n x m).

```python
def lcs_length(a, b):
    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[len(a)][len(b)]


assert lcs_length("abcde", "ace") == 3
assert lcs_length("abc", "xyz") == 0
```

### Knapsack and coin change

In the 0/1 knapsack, each item has a weight and a value. You can use each item one time.
`best[w]` is the largest value with a total weight of at most w.
Go through the weights from high to low, so that each item is used only one time.

In coin change, you can use each coin many times.
`fewest[a]` is the smallest number of coins with a total of a.

```python
def knapsack(weights, values, capacity):
    best = [0] * (capacity + 1)
    for weight, value in zip(weights, values):
        for w in range(capacity, weight - 1, -1):
            best[w] = max(best[w], best[w - weight] + value)
    return best[capacity]


def coin_change(coins, amount):
    fewest = [0] + [float("inf")] * amount
    for total in range(1, amount + 1):
        for coin in coins:
            if coin <= total:
                fewest[total] = min(fewest[total], fewest[total - coin] + 1)
    return fewest[amount] if fewest[amount] != float("inf") else -1


assert knapsack([1, 3, 4, 5], [1, 4, 5, 7], 7) == 9
assert coin_change([1, 2, 5], 11) == 3
assert coin_change([2], 3) == -1
```

## Greedy algorithms and intervals

A greedy algorithm makes the best local choice at each step and does not change it later.
A greedy algorithm is fast, but it is correct only for some problems.
Before you use a greedy algorithm, make sure that a local choice cannot make the final answer worse.

Many interval problems become simple after you sort the intervals.

### Merge overlapping intervals

1. Sort the intervals by their start.
2. Compare each interval with the last merged interval.
3. If they overlap, extend the last merged interval. If not, add the interval as a new one.

The cost is O(n log n), because of the sort.

```python
def merge_intervals(intervals):
    merged = []
    for start, end in sorted(intervals):
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged


assert merge_intervals([[1, 3], [8, 10], [2, 6], [15, 18]]) == [[1, 6], [8, 10], [15, 18]]
```

### Interval scheduling

To keep the largest number of intervals that do not overlap, always keep the interval that ends first.
This greedy choice leaves the most time for the other intervals.

```python
def max_non_overlapping(intervals):
    count = 0
    last_end = float("-inf")
    for start, end in sorted(intervals, key=lambda pair: pair[1]):
        if start >= last_end:
            count += 1
            last_end = end
    return count


assert max_non_overlapping([[1, 2], [2, 3], [3, 4], [1, 3]]) == 3
```

### Meeting rooms

To find the minimum number of rooms, sort the meetings by start time.
Keep a min-heap of the end times of the rooms that are in use.
If the earliest end time is before the new start time, that room becomes free.

```python
import heapq


def rooms_needed(meetings):
    ends = []
    for start, end in sorted(meetings):
        if ends and ends[0] <= start:
            heapq.heapreplace(ends, end)
        else:
            heapq.heappush(ends, end)
    return len(ends)


assert rooms_needed([[0, 30], [5, 10], [15, 20]]) == 2
```

## Balanced trees

A BST is fast only when its height is small.
The order of the inserts sets the height of a plain BST.
A balanced tree changes its shape after each insert, so that its height stays at O(log n).

### Why sorted inserts break a plain BST

If you add the values 1, 2, 3 and so on, each new value is larger than all the values in the tree.
Thus, each new node goes to the right of the last node, and the tree becomes a chain.
A chain of n nodes has a height of n. Each search has a cost of O(n), as in a linked list.
Sorted input is common, for example IDs and timestamps that increase.

### Height and balance factor

The height of a node is the number of levels in its subtree. An empty subtree has a height of 0.
The balance factor of a node is the height of its left subtree minus the height of its right subtree.
An AVL tree keeps the balance factor of each node at -1, 0 or 1.
This rule keeps the height of the tree at less than about 1.44 log2 n.

Each node keeps its own height.
Thus, the tree calculates a balance factor in O(1), without a walk through the subtrees.

### AVL rotations

A rotation changes the shape of a subtree, but the in-order sequence of the values does not change.
A rotation changes only three references, so its cost is O(1).

To do a right rotation at node X, do these steps:

1. Let P be the left child of X. P becomes the new root of the subtree.
2. Move the right subtree of P to the left side of X.
3. Make X the right child of P.
4. Update the height of X. Then update the height of P.

A left rotation is the mirror image. Change "left" to "right" and "right" to "left" in each step.

An insert can make the balance factor of a node 2 or -2.
The table shows the four cases and their rotations.

| Case | Balance factor of the node | Balance factor of the child on the heavy side | Fix |
|---|---|---|---|
| Left-left | 2 | 0 or more (left child) | One right rotation at the node |
| Right-right | -2 | 0 or less (right child) | One left rotation at the node |
| Left-right | 2 | Less than 0 (left child) | A left rotation at the left child, then a right rotation at the node |
| Right-left | -2 | More than 0 (right child) | A right rotation at the right child, then a left rotation at the node |

To add a value to an AVL tree, do these steps:

1. Add the value as in a plain BST.
2. Go back up the path to the root. Update the height of each node.
3. At each node, calculate the balance factor.
4. If the factor is 2 or -2, find the case in the table. Do its rotations.
5. Continue to the root.

| Operation | Plain BST, worst case | AVL tree |
|---|---|---|
| Find, add, remove | O(n) | O(log n) |
| One rotation | Not used | O(1) |
| Height after n sorted inserts | n | Less than about 1.44 log2 n |

The sample adds the values 1 to 1000 in order.
The plain BST becomes a chain with a height of 1000. The AVL tree has a height of 10.

```python
import math


class Node:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None
        self.height = 1


def height(node):
    return node.height if node else 0


def balance(node):
    return height(node.left) - height(node.right)


def update(node):
    node.height = 1 + max(height(node.left), height(node.right))


def rotate_right(node):
    pivot = node.left
    node.left = pivot.right
    pivot.right = node
    update(node)
    update(pivot)
    return pivot


def rotate_left(node):
    pivot = node.right
    node.right = pivot.left
    pivot.left = node
    update(node)
    update(pivot)
    return pivot


def insert(node, val):
    if node is None:
        return Node(val)
    if val < node.val:
        node.left = insert(node.left, val)
    elif val > node.val:
        node.right = insert(node.right, val)
    else:
        return node
    update(node)
    if balance(node) > 1:
        if balance(node.left) < 0:
            node.left = rotate_left(node.left)  # left-right case
        return rotate_right(node)
    if balance(node) < -1:
        if balance(node.right) > 0:
            node.right = rotate_right(node.right)  # right-left case
        return rotate_left(node)
    return node


def build(values):
    root = None
    for value in values:
        root = insert(root, value)
    return root


def inorder(node):
    return inorder(node.left) + [node.val] + inorder(node.right) if node else []


def is_balanced(node):
    if node is None:
        return True
    return abs(balance(node)) <= 1 and is_balanced(node.left) and is_balanced(node.right)


def plain_bst_height(values):
    """Add values to a plain BST without rotations. Return its height."""
    root, tallest = None, 0
    for value in values:
        depth, parent, node = 1, None, root
        while node is not None:
            parent, depth = node, depth + 1
            node = node.left if value < node.val else node.right
        child = Node(value)
        if parent is None:
            root = child
        elif value < parent.val:
            parent.left = child
        else:
            parent.right = child
        tallest = max(tallest, depth)
    return tallest


# each of the four cases gives the same balanced tree, with 2 at the root
for order in ([3, 2, 1], [1, 2, 3], [3, 1, 2], [1, 3, 2]):
    root = build(order)
    assert (root.val, root.left.val, root.right.val) == (2, 1, 3)
    assert height(root) == 2

values = list(range(1, 1001))
assert plain_bst_height(values) == 1000  # sorted inserts make a chain
root = build(values)
assert inorder(root) == values
assert is_balanced(root)
assert height(root) == 10
assert height(root) <= 1.44 * math.log2(len(values) + 2)

import random

shuffled = random.Random(5).sample(range(10_000), 10_000)
root = build(shuffled)
assert is_balanced(root)
assert height(root) <= 1.44 * math.log2(10_000 + 2)
```

NOTE: After one insert, one rotation or one double rotation is sufficient.
A remove can need rotations at each node on the path, so it does up to O(log n) rotations.

NOTE: Red-black trees use a weaker rule. Their height is at most 2 log2 (n + 1), and they do fewer rotations.
Many libraries use them for sorted maps.

CAUTION: The Python standard library has no balanced BST.
The `bisect` module keeps a list sorted, but each insert moves items, so its cost is O(n).

## Range queries

A range query asks for one value over a range of indices.
For example, it asks for the sum or the minimum of the items from index lo to index hi - 1.
If the list does not change, a [prefix sum](#prefix-sums) array gives each range sum in O(1).
But one change to an item then changes O(n) prefix sums.

A Fenwick tree and a segment tree make a change and a query both O(log n).

| Structure | Change one item | Range sum | Range minimum | Memory |
|---|---|---|---|---|
| Plain list | O(1) | O(n) | O(n) | O(n) |
| Prefix sum array | O(n) | O(1) | Not supported | O(n) |
| Fenwick tree | O(log n) | O(log n) | Not supported | O(n) |
| Segment tree | O(log n) | O(log n) | O(log n) | O(n), about 2n slots |

### Fenwick tree

A Fenwick tree (binary indexed tree) keeps partial sums in a list. It uses indices from 1.
The slot at index i holds the sum of a block of items that ends at item i.
The length of that block is `i & -i`, the lowest set bit of i. See [Bit manipulation](#bit-manipulation).
For example, slot 6 (binary 110) holds 2 items, and slot 8 (binary 1000) holds 8 items.

To get the sum of the first i items, do these steps:

1. Set the total to 0.
2. Add the slot at index i to the total.
3. Remove the lowest set bit from i: `i -= i & -i`.
4. If i is more than 0, go back to step 2.

To add a delta to item i, do these steps:

1. Add the delta to the slot at index i.
2. Go to the next slot that covers item i: `i += i & -i`.
3. If i is not more than n, go back to step 1.

Each loop runs at most about log2 n times.
The sum of the items from lo to hi - 1 is `prefix_sum(hi) - prefix_sum(lo)`.

CAUTION: A Fenwick tree needs an operation that you can undo, for example subtraction for sums.
You cannot get the minimum of a range from two prefix minimums. For a range minimum, use a segment tree.

### Segment tree

A segment tree is a binary tree over the list. Each node holds the result for a range of items.
The leaves are the items. In a range minimum tree, each parent holds the smaller value of its two children.
The sample keeps the tree in a list from index 1. Node i has the children 2i and 2i + 1.
The leaves are at the indices n to 2n - 1.

To change one item, do these steps:

1. Write the new value in its leaf.
2. Move to the parent of the node.
3. Set the parent to the minimum of its two children.
4. Do steps 2 and 3 again until you reach the root.

To find the minimum of the items from lo to hi - 1, do these steps:

1. Put the two edges at the leaves for lo and hi.
2. If the left edge is a right child, use its value. Then move the edge one node to the right.
3. If the right edge is a right child, move it one node to the left. Use its value.
4. Move both edges up to their parents.
5. Stop when the edges meet. The result is the smallest value that you used.

Each level adds at most two nodes, so a query reads at most about 2 log2 n nodes.
A segment tree works for each associative operation, for example minimum, maximum, sum and greatest common divisor.

```python
import random


class FenwickTree:
    def __init__(self, size):
        self.tree = [0] * (size + 1)  # index 0 is not used

    def add(self, index, delta):
        i = index + 1
        while i < len(self.tree):
            self.tree[i] += delta
            i += i & -i  # go to the next node that covers index

    def prefix_sum(self, count):
        """Return the sum of the first count items."""
        total, i = 0, count
        while i > 0:
            total += self.tree[i]
            i -= i & -i  # remove the lowest set bit
        return total

    def range_sum(self, lo, hi):
        """Return the sum of the items from index lo to index hi - 1."""
        return self.prefix_sum(hi) - self.prefix_sum(lo)


class MinSegmentTree:
    def __init__(self, values):
        self.size = len(values)
        self.tree = [float("inf")] * self.size + list(values)
        for node in range(self.size - 1, 0, -1):
            self.tree[node] = min(self.tree[2 * node], self.tree[2 * node + 1])

    def set(self, index, value):
        node = index + self.size
        self.tree[node] = value
        while node > 1:
            node //= 2
            self.tree[node] = min(self.tree[2 * node], self.tree[2 * node + 1])

    def range_min(self, lo, hi):
        """Return the smallest item from index lo to index hi - 1."""
        best = float("inf")
        lo, hi = lo + self.size, hi + self.size
        while lo < hi:
            if lo & 1:
                best = min(best, self.tree[lo])
                lo += 1
            if hi & 1:
                hi -= 1
                best = min(best, self.tree[hi])
            lo //= 2
            hi //= 2
        return best


assert [i & -i for i in range(1, 9)] == [1, 2, 1, 4, 1, 2, 1, 8]

values = [5, 2, 8, 1, 9, 3]
sums = FenwickTree(len(values))
for index, value in enumerate(values):
    sums.add(index, value)
assert sums.prefix_sum(3) == 15
assert sums.range_sum(2, 5) == 18
sums.add(3, 10)  # values[3] becomes 11
assert sums.range_sum(2, 5) == 28

mins = MinSegmentTree(values)
assert mins.range_min(0, 6) == 1
assert mins.range_min(4, 6) == 3
mins.set(3, 7)
assert mins.range_min(0, 6) == 2
assert mins.range_min(2, 5) == 7

# compare both trees with direct calculation, after many random changes
rng = random.Random(3)
data = [rng.randint(-50, 50) for _ in range(37)]
sums, mins = FenwickTree(len(data)), MinSegmentTree(data)
for index, value in enumerate(data):
    sums.add(index, value)
for _ in range(500):
    index, value = rng.randrange(len(data)), rng.randint(-50, 50)
    sums.add(index, value - data[index])
    mins.set(index, value)
    data[index] = value
    lo = rng.randrange(len(data))
    hi = rng.randrange(lo + 1, len(data) + 1)
    assert sums.range_sum(lo, hi) == sum(data[lo:hi])
    assert mins.range_min(lo, hi) == min(data[lo:hi])
```

NOTE: A segment tree with "lazy propagation" can also add a value to a full range in O(log n).

## Bit manipulation

An integer is a sequence of bits. One bit operation changes many bits in one step.
Use bit operations for sets of flags, for small sets of integers, and for some fast calculations.

The operators are:

- `a & b` (AND): a bit is 1 only if it is 1 in a and in b.
- `a | b` (OR): a bit is 1 if it is 1 in a or in b.
- `a ^ b` (XOR): a bit is 1 if the two bits are different.
- `~a` (NOT): each bit changes. In Python, `~a` is equal to `-a - 1`.
- `a << k` (left shift): the bits move k places to the left. This multiplies a by 2^k.
- `a >> k` (right shift): the bits move k places to the right. This divides a by 2^k and rounds down.

To work with bit k of n, use these expressions:

- Set the bit: `n | (1 << k)`.
- Clear the bit: `n & ~(1 << k)`.
- Test the bit: `(n >> k) & 1`.
- Change the bit to its opposite value: `n ^ (1 << k)`.

| Operation | Cost |
|---|---|
| AND, OR, XOR, NOT or a shift on one machine word | O(1) |
| Set, clear or test one bit | O(1) |
| Count the set bits with `n & (n - 1)` | O(number of set bits) |
| XOR of n numbers | O(n) |
| Make all subsets of n items as bitmasks | O(n x 2^n) |

NOTE: The costs are for numbers that fit in one machine word, for example 64 bits.
Python integers have no fixed size. For a number with b bits, each operation has a cost of O(b / 64).

### Remove the lowest set bit

`n & (n - 1)` removes the lowest set bit of n.
When you subtract 1, the lowest set bit becomes 0, and each 0 bit below it becomes 1.
The AND then clears all of those bits.

Two uses come from this operation:

- A number n is a power of two when n is more than 0 and `n & (n - 1)` is 0.
- To count the set bits, remove the lowest set bit until n is 0. Each loop removes one bit.

`n & -n` keeps only the lowest set bit. The [Fenwick tree](#fenwick-tree) uses this value.

### XOR tricks

XOR has three useful properties:

- `x ^ x` is 0.
- `x ^ 0` is x.
- The order does not change the result. Thus, `a ^ b ^ a` is b.

In a list, each number occurs two times, except one number.
To find the single number, XOR all the numbers. The pairs become 0, and only the single number stays.
The cost is O(n), and the extra memory is O(1). A solution with a set uses O(n) memory.

### Subsets as bitmasks

A set of n items has 2^n subsets.
Each integer from 0 to 2^n - 1 can show one subset: bit i is 1 when item i is in the subset.

To make all subsets, do these steps:

1. Count from 0 to 2^n - 1. Each number is a mask.
2. For each mask, include item i if bit i of the mask is 1.

This gives the same subsets as [backtracking](#backtracking), without recursion.
A mask is also a small dictionary key, for example for a DP state that is a subset of items.

```python
from functools import reduce


def set_bit(n, k):
    return n | (1 << k)


def clear_bit(n, k):
    return n & ~(1 << k)


def test_bit(n, k):
    return (n >> k) & 1 == 1


def is_power_of_two(n):
    return n > 0 and n & (n - 1) == 0


def count_bits(n):
    count = 0
    while n:
        n &= n - 1  # remove the lowest set bit
        count += 1
    return count


def single_number(nums):
    return reduce(lambda a, b: a ^ b, nums, 0)


def subsets(items):
    result = []
    for mask in range(1 << len(items)):
        result.append([item for i, item in enumerate(items) if (mask >> i) & 1])
    return result


assert 0b1100 & 0b1010 == 0b1000
assert 0b1100 | 0b1010 == 0b1110
assert 0b1100 ^ 0b1010 == 0b0110
assert 5 << 3 == 40 and 40 >> 3 == 5

flags = 0
flags = set_bit(flags, 1)
flags = set_bit(flags, 4)
assert flags == 0b10010
assert test_bit(flags, 4) and not test_bit(flags, 2)
assert clear_bit(flags, 4) == 0b10

assert 0b10110 & (0b10110 - 1) == 0b10100  # n & (n - 1) removes the lowest set bit
assert [n for n in range(1, 70) if is_power_of_two(n)] == [1, 2, 4, 8, 16, 32, 64]
assert count_bits(0b1011_0110) == 5 == bin(0b1011_0110).count("1")

assert single_number([4, 1, 2, 1, 2]) == 4

assert subsets(["a", "b", "c"]) == [[], ["a"], ["b"], ["a", "b"], ["c"], ["a", "c"], ["b", "c"], ["a", "b", "c"]]

assert ~5 == -6  # Python integers have no fixed width
assert ~5 & 0xFF == 0b1111_1010  # a mask keeps only the low 8 bits
```

CAUTION: In Python, `~5` is -6, and a right shift of a negative number keeps the sign.
For a result with a fixed width, AND the result with a mask, for example `0xFFFFFFFF` for 32 bits.

## String matching

A string search finds each position where a pattern occurs in a text.
We use n for the length of the text and m for the length of the pattern.

| Algorithm | Preparation | Search, usual text | Search, worst case | Extra memory |
|---|---|---|---|---|
| Naive | None | O(n) | O(n x m) | O(1) |
| KMP | O(m) | O(n) | O(n) | O(m) |
| Rabin-Karp | O(m) | O(n + m) | O(n x m) | O(1) |

NOTE: The Python `in` operator and `str.find` use a fast built-in algorithm. Use them in usual code.
Use these algorithms when you must control the steps, for example for many patterns or for a stream of text.

### Naive search

To find a pattern with the naive procedure, do these steps:

1. Put the pattern at position 0 of the text.
2. Compare the characters from left to right until two characters are different.
3. If all m characters are equal, record the position.
4. Move the pattern one position to the right. Go back to step 2.

The worst case occurs when almost all of the pattern matches at each position.
For example, the pattern "aaaaaaaaab" in a text of 1,000 "a" characters needs 991 x 10 comparisons.
After each failure, the search starts again from the first character of the pattern. It does not use the comparisons that it did.

### KMP

The Knuth-Morris-Pratt (KMP) algorithm never goes back in the text.
When a character is different, KMP knows how much of the pattern still agrees with the last characters that it read.
The failure table gives that length.

`fail[i]` is the length of the longest proper prefix of `pattern[: i + 1]` that is also a suffix of it.
A proper prefix is shorter than the full string.
For "ababaca", the table is [0, 0, 1, 2, 3, 0, 1]. For example, "ababa" starts and ends with "aba", so `fail[4]` is 3.

To make the failure table, do these steps:

1. Set `fail[0]` to 0. Set `length` to 0.
2. For each i from 1, compare `pattern[i]` with `pattern[length]`.
3. While they are different and `length` is more than 0, set `length` to `fail[length - 1]`.
4. If they are equal, add 1 to `length`.
5. Set `fail[i]` to `length`.

To search with KMP, do these steps:

1. Set `matched` to 0. It is the number of pattern characters that agree now.
2. For each character of the text, compare it with `pattern[matched]`.
3. While they are different and `matched` is more than 0, set `matched` to `fail[matched - 1]`.
4. If they are equal, add 1 to `matched`.
5. If `matched` is equal to m, record a match. Then set `matched` to `fail[m - 1]`.

`matched` increases at most n times, and each step back decreases it.
Thus, the search does at most 2n comparisons.

### Rabin-Karp

Rabin-Karp compares hashes before it compares characters.
It calculates the hash of the pattern and the hash of each window of m characters in the text.
A rolling hash gets the hash of the next window from the hash of the last window in O(1).

The hash of the window c0 c1 ... c(m-1) is (c0 x B^(m-1) + c1 x B^(m-2) + ... + c(m-1)) mod M.
B is the base, for example 256. M is a large prime modulus, for example 1,000,000,007.
The modulus keeps the numbers small.

To move the window one position to the right, do these steps:

1. Subtract the first character x B^(m-1). Keep B^(m-1) mod M in a variable.
2. Multiply the result by B.
3. Add the new character.
4. Take the result mod M.

Two different strings can have the same hash. This is a false positive.
Thus, when the two hashes are equal, compare the characters of the window with the pattern.
With a large prime modulus, false positives are rare, and the average cost is O(n + m).
With a bad modulus, or with a text that an attacker selects, many windows are false positives. The cost becomes O(n x m).

Rabin-Karp is good for many patterns of the same length. Keep the hashes of the patterns in a set.

```python
def naive_search(text, pattern):
    """Return the start of each match, and the number of character comparisons."""
    found, comparisons = [], 0
    for start in range(len(text) - len(pattern) + 1):
        for offset, char in enumerate(pattern):
            comparisons += 1
            if text[start + offset] != char:
                break
        else:
            found.append(start)
    return found, comparisons


def failure_table(pattern):
    """fail[i] is the length of the longest proper prefix of pattern[: i + 1] that is also its suffix."""
    fail = [0] * len(pattern)
    length = 0
    for i in range(1, len(pattern)):
        while length > 0 and pattern[i] != pattern[length]:
            length = fail[length - 1]
        if pattern[i] == pattern[length]:
            length += 1
        fail[i] = length
    return fail


def kmp_search(text, pattern):
    fail = failure_table(pattern)
    found, comparisons, matched = [], 0, 0
    for i, char in enumerate(text):
        while True:
            comparisons += 1
            if char == pattern[matched]:
                matched += 1
                break
            if matched == 0:
                break
            matched = fail[matched - 1]
        if matched == len(pattern):
            found.append(i - len(pattern) + 1)
            matched = fail[matched - 1]
    return found, comparisons


def rabin_karp(text, pattern, base=256, modulus=1_000_000_007):
    """Return the start of each match, and the number of hash candidates."""
    m = len(pattern)
    if m > len(text):
        return [], 0
    high = pow(base, m - 1, modulus)  # the weight of the first character in a window
    target = window = 0
    for i in range(m):
        target = (target * base + ord(pattern[i])) % modulus
        window = (window * base + ord(text[i])) % modulus
    found, candidates = [], 0
    for start in range(len(text) - m + 1):
        if window == target:
            candidates += 1
            if text[start : start + m] == pattern:  # a check removes false positives
                found.append(start)
        if start + m < len(text):
            window = (window - ord(text[start]) * high) % modulus
            window = (window * base + ord(text[start + m])) % modulus
    return found, candidates


assert failure_table("ababaca") == [0, 0, 1, 2, 3, 0, 1]

text = "abababacaba ababaca"
expected = [2, 12]
assert naive_search(text, "ababaca")[0] == expected
assert kmp_search(text, "ababaca")[0] == expected
assert rabin_karp(text, "ababaca")[0] == expected
assert kmp_search("aaaa", "aa")[0] == [0, 1, 2]  # matches can overlap

# the worst case for the naive search: n = 1,000 and m = 10
text, pattern = "a" * 1_000, "a" * 9 + "b"
assert naive_search(text, pattern) == ([], 991 * 10)
found, comparisons = kmp_search(text, pattern)
assert found == [] and comparisons <= 2 * len(text)

# a small modulus gives many false candidates, but the check removes them
found, candidates = rabin_karp("the cat sat on the mat", "at", modulus=5)
assert found == [5, 9, 20]
assert candidates == 9  # 6 of the 9 candidates are false positives
assert rabin_karp("the cat sat on the mat", "at")[1] == 3
```

CAUTION: Do not report a match from equal hashes only. Always compare the characters.
The sample uses a small modulus of 5 to show 6 false positives that the check removes.

## Capstone: route planning on a grid

This section uses [graphs](#graphs), [heaps](#heaps) and breadth-first search together.
A robot must cross a grid map from a start cell to a goal cell.
Each cell has a cost to enter, for example 1 for a road and 9 for mud. The robot cannot enter a wall cell.
Find the route with the lowest total cost, and the cells on that route.

### Grid as a graph

Each open cell is a vertex. Each cell connects to its four neighbours: up, down, left and right.
The weight of an edge is the cost of the cell that the edge enters.
You do not need an adjacency list. Calculate the neighbours of a cell when you need them.
A grid of R rows and C columns has V = R x C vertices and at most 4V edges.

| Method | Use it when | Cost on a grid |
|---|---|---|
| BFS | Each move has the same cost | O(V) |
| 0-1 BFS with a deque | Each move costs 0 or 1 | O(V) |
| Dijkstra with a heap | The costs are different and not negative | O(V log V) |
| A* search | As Dijkstra, with a good estimate of the cost to the goal | O(V log V) in the worst case |

### Dijkstra on a grid

To find the cheapest route, do these steps:

1. Put the start cell in a min-heap with a cost of 0.
2. Remove the cell with the lowest cost from the heap.
3. If the cell is the goal, stop. Its cost is the answer.
4. If the cost is more than the best known cost of the cell, ignore this old entry.
5. For each open neighbour, calculate the cost through this cell.
6. If that cost is lower than the best known cost, record it. Record this cell as the parent.
7. Push the neighbour with its new cost. Go back to step 2.
8. If the heap becomes empty, no route exists.

### Path reconstruction

Dijkstra gives the lowest cost. To get the route, keep a parent pointer for each cell.
The parent is the cell before it on the best known route.

To make the route from the parent pointers, do these steps:

1. Start at the goal.
2. Go to the parent of the current cell, and record it.
3. Stop at the start cell, which has no parent.
4. Reverse the list.

The route has at most V cells, so this costs O(V).

### BFS for uniform costs

When each move has the same cost, the cheapest route is the route with the fewest steps.
BFS finds that route in O(V + E), without a heap.
On the sample grid, BFS finds a route of 4 steps through the mud, with a cost of 28.
Dijkstra finds a route of 6 steps around the mud, with a cost of 6.

```python
import heapq
from collections import deque

WALL = None
STEPS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def neighbours(grid, cell):
    row, col = cell
    for dr, dc in STEPS:
        r, c = row + dr, col + dc
        if 0 <= r < len(grid) and 0 <= c < len(grid[0]) and grid[r][c] is not WALL:
            yield (r, c)


def path_to(parent, goal):
    path = [goal]
    while parent[path[-1]] is not None:
        path.append(parent[path[-1]])
    return path[::-1]


def cheapest_route(grid, start, goal):
    """Dijkstra. A move into a cell costs the number in that cell."""
    cost = {start: 0}
    parent = {start: None}
    heap = [(0, start)]
    while heap:
        spent, cell = heapq.heappop(heap)
        if cell == goal:
            return spent, path_to(parent, goal)
        if spent > cost[cell]:
            continue  # an old entry: a cheaper route to this cell was found
        for nxt in neighbours(grid, cell):
            candidate = spent + grid[nxt[0]][nxt[1]]
            if candidate < cost.get(nxt, float("inf")):
                cost[nxt] = candidate
                parent[nxt] = cell
                heapq.heappush(heap, (candidate, nxt))
    return None


def fewest_steps(grid, start, goal):
    """BFS. Each move has the same cost."""
    parent = {start: None}
    queue = deque([start])
    while queue:
        cell = queue.popleft()
        if cell == goal:
            path = path_to(parent, goal)
            return len(path) - 1, path
        for nxt in neighbours(grid, cell):
            if nxt not in parent:
                parent[nxt] = cell
                queue.append(nxt)
    return None


def route_cost(grid, path):
    return sum(grid[r][c] for r, c in path[1:])


grid = [
    [1, 1, 1, 1, 1],
    [1, 9, 9, 9, 1],
    [1, 1, WALL, 1, 1],
]
start, goal = (1, 0), (1, 4)

cost, path = cheapest_route(grid, start, goal)
assert cost == 6
assert path == [(1, 0), (0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 4)]

steps, short_path = fewest_steps(grid, start, goal)
assert steps == 4
assert short_path == [(1, 0), (1, 1), (1, 2), (1, 3), (1, 4)]
assert route_cost(grid, short_path) == 28  # the fewest steps is not the lowest cost

# when each cell costs the same, BFS and Dijkstra agree
flat = [[1] * 6 for _ in range(5)]
flat[2][1:5] = [WALL] * 4
for target in [(4, 5), (3, 2), (0, 0)]:
    assert cheapest_route(flat, (2, 0), target)[0] == fewest_steps(flat, (2, 0), target)[0]

closed = [[1, WALL], [WALL, 1]]
assert cheapest_route(closed, (0, 0), (1, 1)) is None
assert fewest_steps(closed, (0, 0), (1, 1)) is None
```

CAUTION: Use BFS only when all moves have the same cost.
With different costs, the route with the fewest steps can have a much higher cost.

NOTE: 0-1 BFS puts a cell after a move of cost 0 at the front of the deque, and other cells at the back.

NOTE: A* search is Dijkstra with one change: each heap key also includes an estimate of the cost to the goal.
On this grid, the lowest cell cost x the Manhattan distance is a good estimate.
The estimate must never be more than the true cost. If it is, A* can return a route that is not the cheapest.

## How to select a data structure

Use the table to find a data structure for the operation that you must do quickly.

| You must | Use | Cost |
|---|---|---|
| Get an item by its position | List (dynamic array) | O(1) |
| Find if a value exists | Set | O(1) average |
| Find a value from a key | Dictionary | O(1) average |
| Add and remove at the end only | List as a stack | O(1) |
| Add at one end and remove at the other end | `collections.deque` | O(1) |
| Get the smallest or largest item many times | Heap (`heapq`) | O(log n) |
| Find a value in sorted data | Sorted list and binary search | O(log n) |
| Keep data sorted while you add and remove | Balanced BST | O(log n) |
| Get the sum of a range while items change | Fenwick tree | O(log n) |
| Get the minimum, maximum or sum of a range while items change | Segment tree | O(log n) |
| Keep a set of small integers, and join or compare sets quickly | Bitset (an integer used as bits) | O(1) for each bit. O(n / 64) to join two sets of n bits |
| Find words by their prefix | Trie | O(L) |
| Model connections between items | Graph (adjacency list) | O(V + E) to traverse |
| Join groups and check if two items are in the same group | Union-find | Almost O(1) |

When you start a new problem, do these steps:

1. Write the size of the input. Find the largest cost that is fast enough. For n = 100000, O(n log n) is usually the limit.
2. Find the operation that the solution does most often.
3. Select the data structure that makes that operation fast.
4. Write the simple solution first. Then find the step that repeats work and remove the repetition.
5. Test the solution with an empty input, one item, and the largest input.
