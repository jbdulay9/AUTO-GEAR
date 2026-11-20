"""
Data Structures and Algorithms package for AUTO GEAR.
Exports all 9 manual algorithm implementations and data structures.
"""

from backend.dsa.linked_list import Node, SinglyLinkedList
from backend.dsa.doubly_linked_list import DoubleNode, DoublyLinkedList
from backend.dsa.binary_search import linear_search, binary_search, compare_searches
from backend.dsa.sorting import (
    bubble_sort,
    selection_sort,
    insertion_sort,
    merge_sort,
    quick_sort,
    benchmark_all_sorts,
)
from backend.dsa.binary_search_tree import BSTNode, BinarySearchTree
from backend.dsa.backtracking import build_accessory_bundles
from backend.dsa.greedy import greedy_budget_recommendations
from backend.dsa.dynamic_programming import (
    knapsack_dp_recommendations,
    compare_greedy_vs_dp,
)
from backend.dsa.graph import Graph, get_default_store_graph

__all__ = [
    "Node",
    "SinglyLinkedList",
    "DoubleNode",
    "DoublyLinkedList",
    "linear_search",
    "binary_search",
    "compare_searches",
    "bubble_sort",
    "selection_sort",
    "insertion_sort",
    "merge_sort",
    "quick_sort",
    "benchmark_all_sorts",
    "BSTNode",
    "BinarySearchTree",
    "build_accessory_bundles",
    "greedy_budget_recommendations",
    "knapsack_dp_recommendations",
    "compare_greedy_vs_dp",
    "Graph",
    "get_default_store_graph",
]
