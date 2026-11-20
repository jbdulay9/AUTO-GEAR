"""
Singly Linked List Implementation for AUTO GEAR.
Used for in-memory sequential product inventory storage.

Time Complexities:
- Insert at Head: O(1)
- Insert at Tail: O(n) or O(1) with tail pointer
- Deletion: O(n)
- Search: O(n)
- Traversal: O(n)
Space Complexity: O(n) where n is the number of nodes.
"""

from typing import Any, Callable, Generator, List, Optional


class Node:
    """Represents a single node in a Singly Linked List."""

    def __init__(self, data: Any):
        self.data: Any = data
        self.next: Optional["Node"] = None

    def __repr__(self) -> str:
        return f"Node({self.data})"


class SinglyLinkedList:
    """
    A custom Singly Linked List providing dynamic in-memory data storage,
    sequential retrieval, and node manipulation.
    """

    def __init__(self):
        self.head: Optional[Node] = None
        self.tail: Optional[Node] = None
        self._length: int = 0

    def insert_head(self, data: Any) -> Node:
        """
        Inserts a new element at the beginning of the list.
        Time Complexity: O(1)
        """
        new_node = Node(data)
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            new_node.next = self.head
            self.head = new_node
        self._length += 1
        return new_node

    def insert_tail(self, data: Any) -> Node:
        """
        Inserts a new element at the end of the list.
        Time Complexity: O(1) with maintained tail pointer.
        """
        new_node = Node(data)
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node
        self._length += 1
        return new_node

    def search(self, predicate: Callable[[Any], bool]) -> Optional[Any]:
        """
        Traverses the list and returns the first element satisfying predicate(data) == True.
        Time Complexity: O(n)
        """
        current = self.head
        while current is not None:
            if predicate(current.data):
                return current.data
            current = current.next
        return None

    def find_all(self, predicate: Callable[[Any], bool]) -> List[Any]:
        """
        Returns all elements satisfying predicate(data) == True.
        Time Complexity: O(n)
        """
        results = []
        current = self.head
        while current is not None:
            if predicate(current.data):
                results.append(current.data)
            current = current.next
        return results

    def delete(self, predicate: Callable[[Any], bool]) -> bool:
        """
        Deletes the first node where predicate(data) is True.
        Returns True if a node was deleted, False otherwise.
        Time Complexity: O(n)
        """
        if self.head is None:
            return False

        # If head node matches
        if predicate(self.head.data):
            self.head = self.head.next
            if self.head is None:
                self.tail = None
            self._length -= 1
            return True

        current = self.head
        while current.next is not None:
            if predicate(current.next.data):
                deleted_node = current.next
                current.next = deleted_node.next
                if deleted_node == self.tail:
                    self.tail = current
                self._length -= 1
                return True
            current = current.next

        return False

    def traverse(self) -> Generator[Any, None, None]:
        """Yields each item sequentially from head to tail."""
        current = self.head
        while current is not None:
            yield current.data
            current = current.next

    def to_list(self) -> List[Any]:
        """Converts the linked list into a standard Python list."""
        return list(self.traverse())

    def clear(self):
        """Empties the linked list."""
        self.head = None
        self.tail = None
        self._length = 0

    def __len__(self) -> int:
        return self._length

    def __iter__(self):
        return self.traverse()
