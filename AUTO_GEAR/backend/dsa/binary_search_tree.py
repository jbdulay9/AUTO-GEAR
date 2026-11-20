"""
Binary Search Tree (BST) Implementation for AUTO GEAR.
Used for hierarchical in-memory product indexing, search by ID, and tree traversals.

Time Complexities:
- Insertion: Average O(log n), Worst O(n) (unbalanced)
- Search: Average O(log n), Worst O(n)
- Deletion: Average O(log n), Worst O(n)
- Traversals (Inorder, Preorder, Postorder): O(n)
Space Complexity: O(n)
"""

from typing import Any, List, Optional, Tuple


class BSTNode:
    """Represents a node in the Binary Search Tree."""

    def __init__(self, key: int, data: Any):
        self.key: int = int(key)
        self.data: Any = data
        self.left: Optional["BSTNode"] = None
        self.right: Optional["BSTNode"] = None

    def __repr__(self) -> str:
        return f"BSTNode(key={self.key}, data={self.data})"


class BinarySearchTree:
    """
    Custom Binary Search Tree supporting key-based product indexing,
    fast lookup, deletion, and tree traversals.
    """

    def __init__(self):
        self.root: Optional[BSTNode] = None
        self._size: int = 0

    def insert(self, key: int, data: Any) -> BSTNode:
        """
        Inserts a new key-data pair into the BST. If key already exists, updates data.
        Time Complexity: Average O(log n), Worst O(n)
        """
        new_node = BSTNode(key, data)
        if self.root is None:
            self.root = new_node
            self._size += 1
            return new_node

        current = self.root
        while True:
            if key == current.key:
                current.data = data  # Update existing key
                return current
            elif key < current.key:
                if current.left is None:
                    current.left = new_node
                    self._size += 1
                    return new_node
                current = current.left
            else:
                if current.right is None:
                    current.right = new_node
                    self._size += 1
                    return new_node
                current = current.right

    def search(self, key: int) -> Optional[Any]:
        """
        Searches for a node by key. Returns data if found, None otherwise.
        Time Complexity: Average O(log n), Worst O(n)
        """
        current = self.root
        while current is not None:
            if key == current.key:
                return current.data
            elif key < current.key:
                current = current.left
            else:
                current = current.right
        return None

    def delete(self, key: int) -> bool:
        """
        Deletes a node with the specified key from the tree.
        Handles nodes with 0, 1, or 2 children (using in-order successor).
        Time Complexity: Average O(log n), Worst O(n)
        """
        deleted = [False]

        def _delete_recursive(node: Optional[BSTNode], target_key: int) -> Optional[BSTNode]:
            if node is None:
                return None

            if target_key < node.key:
                node.left = _delete_recursive(node.left, target_key)
            elif target_key > node.key:
                node.right = _delete_recursive(node.right, target_key)
            else:
                deleted[0] = True
                # Case 1 & 2: Node has 0 or 1 child
                if node.left is None:
                    return node.right
                elif node.right is None:
                    return node.left

                # Case 3: Node has 2 children; find inorder successor (min in right subtree)
                successor = self._find_min(node.right)
                node.key = successor.key
                node.data = successor.data
                node.right = _delete_recursive(node.right, successor.key)

            return node

        self.root = _delete_recursive(self.root, int(key))
        if deleted[0]:
            self._size -= 1
        return deleted[0]

    def _find_min(self, node: BSTNode) -> BSTNode:
        """Helper to find the node with the minimum key in a subtree."""
        current = node
        while current.left is not None:
            current = current.left
        return current

    def inorder(self) -> List[Any]:
        """
        Inorder Traversal: Left -> Root -> Right.
        Returns elements sorted in ascending order of keys.
        Time Complexity: O(n)
        """
        result = []

        def _traverse(node: Optional[BSTNode]):
            if node:
                _traverse(node.left)
                result.append(node.data)
                _traverse(node.right)

        _traverse(self.root)
        return result

    def preorder(self) -> List[Any]:
        """
        Preorder Traversal: Root -> Left -> Right.
        Captures the hierarchical root-first structure.
        Time Complexity: O(n)
        """
        result = []

        def _traverse(node: Optional[BSTNode]):
            if node:
                result.append(node.data)
                _traverse(node.left)
                _traverse(node.right)

        _traverse(self.root)
        return result

    def postorder(self) -> List[Any]:
        """
        Postorder Traversal: Left -> Right -> Root.
        Useful for bottom-up analysis and deletion.
        Time Complexity: O(n)
        """
        result = []

        def _traverse(node: Optional[BSTNode]):
            if node:
                _traverse(node.left)
                _traverse(node.right)
                result.append(node.data)

        _traverse(self.root)
        return result

    def size(self) -> int:
        """Returns the number of nodes in the BST."""
        return self._size

    def is_empty(self) -> bool:
        """Returns True if the tree has no nodes."""
        return self.root is None

    def clear(self):
        """Clears all nodes from the BST."""
        self.root = None
        self._size = 0
