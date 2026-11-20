from typing import Any, Callable, Generator, List, Optional


class DoubleNode:
    """Represents a node in a Doubly Linked List with bidirectional pointers."""

    def __init__(self, data: Any):
        self.data: Any = data
        self.prev: Optional["DoubleNode"] = None
        self.next: Optional["DoubleNode"] = None

    def __repr__(self) -> str:
        return f"DoubleNode({self.data})"


class DoublyLinkedList:
    """
    Custom Doubly Linked List for shopping cart operations, supporting
    bidirectional iteration and dynamic node manipulation.
    """

    def __init__(self):
        self.head: Optional[DoubleNode] = None
        self.tail: Optional[DoubleNode] = None
        self._length: int = 0

    def append(self, data: Any) -> DoubleNode:
        """
        Appends an element to the end (tail) of the doubly linked list.
        Time Complexity: O(1)
        """
        new_node = DoubleNode(data)
        if self.tail is None:
            self.head = new_node
            self.tail = new_node
        else:
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node
        self._length += 1
        return new_node

    def prepend(self, data: Any) -> DoubleNode:
        """
        Inserts an element at the beginning (head) of the doubly linked list.
        Time Complexity: O(1)
        """
        new_node = DoubleNode(data)
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            new_node.next = self.head
            self.head.prev = new_node
            self.head = new_node
        self._length += 1
        return new_node

    def find_node(self, predicate: Callable[[Any], bool]) -> Optional[DoubleNode]:
        """
        Finds and returns the first DoubleNode where predicate(data) is True.
        Time Complexity: O(n)
        """
        current = self.head
        while current is not None:
            if predicate(current.data):
                return current
            current = current.next
        return None

    def remove_node(self, node: DoubleNode) -> bool:
        """
        Unlinks a specific node from the list.
        Time Complexity: O(1)
        """
        if node is None:
            return False

        if node.prev is not None:
            node.prev.next = node.next
        else:
            self.head = node.next

        if node.next is not None:
            node.next.prev = node.prev
        else:
            self.tail = node.prev

        node.prev = None
        node.next = None
        self._length -= 1
        return True

    def remove(self, predicate: Callable[[Any], bool]) -> bool:
        """
        Searches for a node matching the predicate and unlinks it.
        Time Complexity: O(n)
        """
        target = self.find_node(predicate)
        if target:
            return self.remove_node(target)
        return False

    def traverse_forward(self) -> Generator[Any, None, None]:
        """Traverses the list from head to tail."""
        current = self.head
        while current is not None:
            yield current.data
            current = current.next

    def traverse_backward(self) -> Generator[Any, None, None]:
        """Traverses the list from tail to head."""
        current = self.tail
        while current is not None:
            yield current.data
            current = current.prev

    def to_list(self) -> List[Any]:
        """Converts the list to a standard Python list (forward order)."""
        return list(self.traverse_forward())

    def clear(self):
        """Clears all nodes from the doubly linked list."""
        self.head = None
        self.tail = None
        self._length = 0

    def calculate_total(self, subtotal_func: Callable[[Any], float]) -> float:
        """Calculates cumulative sum by applying subtotal_func to each node's data."""
        total = 0.0
        for item in self.traverse_forward():
            total += float(subtotal_func(item))
        return round(total, 2)

    def __len__(self) -> int:
        return self._length

    def __iter__(self):
        return self.traverse_forward()
