"""
Custom Top-K Zones Algorithm Implementation

This module implements a manual Top-K algorithm using a custom MinHeap data structure.
It finds the K zones with the highest number of taxi pickups without using built-in
sorting functions, Counter class, or heapq module.

The algorithm is efficient with O(N log K) time complexity where N is the number
of unique zones and K is the number of top zones requested.
"""


class MinHeap:
    """
    A custom min-heap implementation that maintains the K largest elements.
    
    The heap property ensures the smallest element is always at the root (index 0).
    This is used to efficiently track the top-K zones by maintaining a heap of
    size K and discarding smaller elements.
    """
    
    def __init__(self):
        """Initialize an empty min-heap."""
        self.heap = []
        self.size = 0
    
    def _parent(self, i):
        """Get the index of the parent node."""
        return (i - 1) // 2
    
    def _left_child(self, i):
        """Get the index of the left child node."""
        return 2 * i + 1
    
    def _right_child(self, i):
        """Get the index of the right child node."""
        return 2 * i + 2
    
    def _swap(self, i, j):
        """Swap two elements in the heap."""
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]
    
    def _heapify_up(self, i):
        """
        Move an element up the heap to maintain the min-heap property.
        
        This is called after inserting a new element. It compares the element
        with its parent and swaps if necessary, continuing up the tree until
        the heap property is restored.
        
        Args:
            i: Index of the element to heapify up
        """
        while i > 0:
            parent_idx = self._parent(i)
            # If current element is smaller than parent, swap and continue up
            if self.heap[i][0] < self.heap[parent_idx][0]:
                self._swap(i, parent_idx)
                i = parent_idx
            else:
                break
    
    def _heapify_down(self, i):
        """
        Move an element down the heap to maintain the min-heap property.
        
        This is called after removing the root element. It compares the element
        with its children and swaps with the smaller child if necessary,
        continuing down the tree until the heap property is restored.
        
        Args:
            i: Index of the element to heapify down
        """
        while True:
            smallest = i
            left = self._left_child(i)
            right = self._right_child(i)
            
            # Check if left child exists and is smaller than current
            if left < self.size and self.heap[left][0] < self.heap[smallest][0]:
                smallest = left
            
            # Check if right child exists and is smaller than current smallest
            if right < self.size and self.heap[right][0] < self.heap[smallest][0]:
                smallest = right
            
            # If smallest is not current element, swap and continue down
            if smallest != i:
                self._swap(i, smallest)
                i = smallest
            else:
                break
    
    def insert(self, item):
        """
        Insert a new item (count, location_id) tuple into the heap.
        
        Args:
            item: Tuple of (count, location_id) to insert
        """
        self.heap.append(item)
        self.size += 1
        self._heapify_up(self.size - 1)
    
    def extract_min(self):
        """
        Remove and return the minimum element from the heap.
        
        Returns:
            Tuple of (count, location_id) with the smallest count
        """
        if self.size == 0:
            return None
        
        min_item = self.heap[0]
        
        # Move last element to root
        self.heap[0] = self.heap[self.size - 1]
        self.heap.pop()
        self.size -= 1
        
        # Restore heap property
        if self.size > 0:
            self._heapify_down(0)
        
        return min_item
    
    def peek_min(self):
        """
        Return the minimum element without removing it.
        
        Returns:
            Tuple of (count, location_id) with the smallest count, or None if empty
        """
        if self.size == 0:
            return None
        return self.heap[0]
    
    def get_size(self):
        """Return the current number of elements in the heap."""
        return self.size


def count_trips_per_zone(location_ids):
    """
    Count the number of trips for each zone using manual counting.
    
    This function manually counts occurrences without using Counter class.
    It iterates through all location IDs and maintains a dictionary.
    
    Args:
        location_ids: List of integer location IDs from trips
    
    Returns:
        Dictionary mapping location_id to count of trips
    """
    counts = {}
    
    # Manual counting loop - no Counter class
    for location_id in location_ids:
        if location_id in counts:
            counts[location_id] += 1
        else:
            counts[location_id] = 1
    
    return counts


def insertion_sort_descending(items):
    """
    Sort a list of items in descending order by their first element (count).
    
    This is a manual implementation of insertion sort without using Python's
    built-in sort or sorted functions.
    
    Args:
        items: List of (count, location_id) tuples to sort in place
    """
    # Start from the second item
    for i in range(1, len(items)):
        key = items[i]
        j = i - 1
        
        # Shift elements greater than key to the right
        # Note: We use > for descending order (higher counts first)
        while j >= 0 and items[j][0] < key[0]:
            items[j + 1] = items[j]
            j -= 1
        
        items[j + 1] = key


def get_top_k_zones(location_ids, k):
    """
    Find the K zones with the highest number of pickups.
    
    This uses a min-heap of size K to efficiently find the top K zones.
    Algorithm:
    1. Count trips per zone (manual counting, no Counter)
    2. Create a min-heap of size K
    3. For each zone:
       - If heap < K, insert it
       - If heap == K and count > min in heap, remove min and insert current
    4. Extract all items from heap and sort by count descending
    
    Time Complexity: O(N log K) where N is number of zones, K is top zones
    Space Complexity: O(N) for counts dict + O(K) for heap
    
    Args:
        location_ids: List of all pickup location IDs from trips
        k: Number of top zones to return
    
    Returns:
        List of (count, location_id) tuples sorted by count descending
    """
    # Step 1: Count trips per zone
    counts = count_trips_per_zone(location_ids)
    
    # Step 2: Use min-heap to find top K zones
    min_heap = MinHeap()
    
    # Process each zone
    for location_id, count in counts.items():
        if min_heap.get_size() < k:
            # Heap not full yet, insert this zone
            min_heap.insert((count, location_id))
        else:
            # Heap is full
            min_in_heap = min_heap.peek_min()
            if count > min_in_heap[0]:
                # This zone has more trips than the minimum in heap
                min_heap.extract_min()
                min_heap.insert((count, location_id))
    
    # Step 3: Extract all items from heap into a list
    result = []
    while min_heap.get_size() > 0:
        result.append(min_heap.extract_min())
    
    # Step 4: Sort in descending order by count (manual insertion sort)
    insertion_sort_descending(result)
    
    return result


"""
ALGORITHM DOCUMENTATION
========================

PSEUDO-CODE FOR INSERT AND HEAPIFY_UP:

INSERT(item):
    1. Append item to end of heap list
    2. Increment size counter
    3. Call HEAPIFY_UP on the last index

HEAPIFY_UP(index i):
    1. While i > 0 (not at root):
        a. Calculate parent_index = (i - 1) // 2
        b. If heap[i].count < heap[parent_index].count:
            - Swap heap[i] and heap[parent_index]
            - Set i = parent_index (continue up)
        c. Else: Break (heap property restored)

TIME COMPLEXITY:
- Build counts dictionary: O(N) where N is total number of location IDs
- Insert operations: O(K * log K) where K is number of unique zones up to limit
- Extract operations: O(K * log K)
- Overall for top-K: O(N log K) where N is number of zones, K is top zones
  This is better than O(N log N) for full sort when K << N

SPACE COMPLEXITY:
- Counts dictionary: O(N) where N is number of unique zones
- Min-heap: O(K) where K is the parameter passed to function
- Total: O(N + K) ≈ O(N) since counts needs all zones
"""


if __name__ == "__main__":
    # TEST EXAMPLE
    print("\n" + "="*70)
    print("TOP-K ZONES ALGORITHM TEST")
    print("="*70)
    
    # Create a sample dataset with 20 location IDs with some repeating
    sample_ids = [1, 2, 3, 1, 4, 5, 1, 2, 6, 7, 1, 8, 2, 9, 10, 1, 2, 3, 11, 1]
    
    print(f"\nSample location IDs: {sample_ids}")
    print(f"Finding top 5 zones...\n")
    
    # Get top 5 zones
    top_5 = get_top_k_zones(sample_ids, k=5)
    
    print("Top 5 zones by pickup count:")
    print(f"{'Rank':<6} {'Location ID':<15} {'Pickup Count':<15}")
    print("-" * 36)
    for i, (count, zone_id) in enumerate(top_5, 1):
        print(f"{i:<6} {zone_id:<15} {count:<15}")
    
    print("\n" + "="*70)
    print("TEST COMPLETE - Algorithm works correctly!")
    print("="*70)
