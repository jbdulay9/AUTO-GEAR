"""
Sorting Algorithms Implementation for AUTO GEAR.
Includes Bubble Sort, Selection Sort, Insertion Sort, Merge Sort, and Quick Sort.

All algorithms are implemented manually in Python without using Python's built-in sort().
Each algorithm records comparisons, swaps/moves, and execution time for analysis.
"""

import time
from typing import Any, Callable, Dict, List, Tuple


def bubble_sort(
    items: List[Any],
    key_func: Callable[[Any], Any] = lambda x: x,
    reverse: bool = False
) -> Tuple[List[Any], Dict[str, Any]]:
    """
    Bubble Sort: Repeatedly steps through the list, compares adjacent elements,
    and swaps them if they are in the wrong order. Includes early termination optimization.

    Time Complexity: Best O(n), Average O(n^2), Worst O(n^2). Space: O(1) auxiliary.
    """
    arr = list(items)
    n = len(arr)
    comparisons = 0
    swaps = 0
    start_time = time.perf_counter()

    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            comparisons += 1
            val_a = key_func(arr[j])
            val_b = key_func(arr[j + 1])
            is_out_of_order = (val_a < val_b) if reverse else (val_a > val_b)

            if is_out_of_order:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swaps += 1
                swapped = True
        if not swapped:
            break

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0
    return arr, {
        "algorithm": "Bubble Sort",
        "classification": "Basic Sorting",
        "time_complexity": "O(n²)",
        "space_complexity": "O(1)",
        "comparisons": comparisons,
        "swaps": swaps,
        "time_ms": round(elapsed_ms, 4),
    }


def selection_sort(
    items: List[Any],
    key_func: Callable[[Any], Any] = lambda x: x,
    reverse: bool = False
) -> Tuple[List[Any], Dict[str, Any]]:
    """
    Selection Sort: Divides the list into a sorted and unsorted region,
    repeatedly selects the minimum (or maximum) from the unsorted region, and places it at the beginning.

    Time Complexity: Best O(n^2), Average O(n^2), Worst O(n^2). Space: O(1) auxiliary.
    """
    arr = list(items)
    n = len(arr)
    comparisons = 0
    swaps = 0
    start_time = time.perf_counter()

    for i in range(n):
        target_idx = i
        for j in range(i + 1, n):
            comparisons += 1
            val_j = key_func(arr[j])
            val_target = key_func(arr[target_idx])
            is_better = (val_j > val_target) if reverse else (val_j < val_target)
            if is_better:
                target_idx = j

        if target_idx != i:
            arr[i], arr[target_idx] = arr[target_idx], arr[i]
            swaps += 1

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0
    return arr, {
        "algorithm": "Selection Sort",
        "classification": "Basic Sorting",
        "time_complexity": "O(n²)",
        "space_complexity": "O(1)",
        "comparisons": comparisons,
        "swaps": swaps,
        "time_ms": round(elapsed_ms, 4),
    }


def insertion_sort(
    items: List[Any],
    key_func: Callable[[Any], Any] = lambda x: x,
    reverse: bool = False
) -> Tuple[List[Any], Dict[str, Any]]:
    """
    Insertion Sort: Iterates through the list, inserting each element into its
    correct position relative to previously sorted elements by shifting larger elements.

    Time Complexity: Best O(n), Average O(n^2), Worst O(n^2). Space: O(1) auxiliary.
    """
    arr = list(items)
    n = len(arr)
    comparisons = 0
    shifts = 0
    start_time = time.perf_counter()

    for i in range(1, n):
        key_item = arr[i]
        key_val = key_func(key_item)
        j = i - 1

        while j >= 0:
            comparisons += 1
            curr_val = key_func(arr[j])
            should_shift = (curr_val < key_val) if reverse else (curr_val > key_val)
            if should_shift:
                arr[j + 1] = arr[j]
                shifts += 1
                j -= 1
            else:
                break
        arr[j + 1] = key_item

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0
    return arr, {
        "algorithm": "Insertion Sort",
        "classification": "Basic Sorting",
        "time_complexity": "O(n²)",
        "space_complexity": "O(1)",
        "comparisons": comparisons,
        "swaps": shifts,
        "time_ms": round(elapsed_ms, 4),
    }


def merge_sort(
    items: List[Any],
    key_func: Callable[[Any], Any] = lambda x: x,
    reverse: bool = False
) -> Tuple[List[Any], Dict[str, Any]]:
    """
    Merge Sort: Divide-and-conquer algorithm that divides the array in halves,
    sorts each half recursively, and merges the sorted halves.

    Time Complexity: Best O(n log n), Average O(n log n), Worst O(n log n). Space: O(n).
    """
    comparisons = [0]
    start_time = time.perf_counter()

    def _merge(left: List[Any], right: List[Any]) -> List[Any]:
        merged = []
        i = j = 0
        while i < len(left) and j < len(right):
            comparisons[0] += 1
            val_l = key_func(left[i])
            val_r = key_func(right[j])
            choose_left = (val_l >= val_r) if reverse else (val_l <= val_r)

            if choose_left:
                merged.append(left[i])
                i += 1
            else:
                merged.append(right[j])
                j += 1

        merged.extend(left[i:])
        merged.extend(right[j:])
        return merged

    def _sort(lst: List[Any]) -> List[Any]:
        if len(lst) <= 1:
            return lst
        mid = len(lst) // 2
        left = _sort(lst[:mid])
        right = _sort(lst[mid:])
        return _merge(left, right)

    sorted_arr = _sort(list(items))
    elapsed_ms = (time.perf_counter() - start_time) * 1000.0

    return sorted_arr, {
        "algorithm": "Merge Sort",
        "classification": "Divide and Conquer",
        "time_complexity": "O(n log n)",
        "space_complexity": "O(n)",
        "comparisons": comparisons[0],
        "swaps": comparisons[0],  # Auxiliary merge operations
        "time_ms": round(elapsed_ms, 4),
    }


def quick_sort(
    items: List[Any],
    key_func: Callable[[Any], Any] = lambda x: x,
    reverse: bool = False
) -> Tuple[List[Any], Dict[str, Any]]:
    """
    Quick Sort: Divide-and-conquer algorithm that selects a pivot element,
    partitions the array around the pivot, and sorts partitions recursively.

    Time Complexity: Best O(n log n), Average O(n log n), Worst O(n^2). Space: O(log n).
    """
    arr = list(items)
    comparisons = [0]
    swaps = [0]
    start_time = time.perf_counter()

    def _partition(low: int, high: int) -> int:
        pivot_val = key_func(arr[high])
        i = low - 1

        for j in range(low, high):
            comparisons[0] += 1
            curr_val = key_func(arr[j])
            condition = (curr_val > pivot_val) if reverse else (curr_val < pivot_val)
            if condition:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
                swaps[0] += 1

        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        swaps[0] += 1
        return i + 1

    def _quick_sort(low: int, high: int):
        if low < high:
            pi = _partition(low, high)
            _quick_sort(low, pi - 1)
            _quick_sort(pi + 1, high)

    if len(arr) > 1:
        _quick_sort(0, len(arr) - 1)

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0

    return arr, {
        "algorithm": "Quick Sort",
        "classification": "Divide and Conquer",
        "time_complexity": "O(n log n)",
        "space_complexity": "O(log n)",
        "comparisons": comparisons[0],
        "swaps": swaps[0],
        "time_ms": round(elapsed_ms, 4),
    }


def benchmark_all_sorts(
    items: List[Any],
    key_func: Callable[[Any], Any] = lambda x: x,
    reverse: bool = False
) -> Dict[str, Any]:
    """
    Runs all 5 manual sorting algorithms on duplicate copies of items and returns a comparison.
    """
    algorithms = [
        bubble_sort,
        selection_sort,
        insertion_sort,
        merge_sort,
        quick_sort,
    ]
    results = []
    sorted_sample = None

    for alg in algorithms:
        sorted_list, metrics = alg(items, key_func=key_func, reverse=reverse)
        results.append(metrics)
        if sorted_sample is None:
            sorted_sample = sorted_list

    return {
        "total_items": len(items),
        "results": results,
        "sorted_items": sorted_sample,
    }
