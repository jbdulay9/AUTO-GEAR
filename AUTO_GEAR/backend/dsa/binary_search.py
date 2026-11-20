import time
from typing import Any, Callable, Dict, List, Optional, Tuple


def linear_search(
    items: List[Any],
    key_func: Callable[[Any], Any],
    target: Any
) -> Dict[str, Any]:
    """
    Performs a sequential Linear Search over items.
    Returns dictionary with match index, found item, comparisons made, and elapsed time in ms.
    """
    start_time = time.perf_counter()
    comparisons = 0
    found_index = -1
    found_item = None

    for idx, item in enumerate(items):
        comparisons += 1
        val = key_func(item)
        if val == target:
            found_index = idx
            found_item = item
            break
        # Optional string substring match if target is a string
        elif isinstance(val, str) and isinstance(target, str) and target.lower() in val.lower():
            found_index = idx
            found_item = item
            break

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0

    return {
        "algorithm": "Linear Search",
        "found": found_index != -1,
        "index": found_index,
        "item": found_item,
        "comparisons": comparisons,
        "time_ms": round(elapsed_ms, 4),
        "complexity": "O(n)",
    }


def binary_search(
    sorted_items: List[Any],
    key_func: Callable[[Any], Any],
    target: Any
) -> Dict[str, Any]:
    """
    Performs divide-and-conquer Binary Search on a SORTED collection.
    Returns dictionary with match index, found item, comparisons made, and elapsed time in ms.
    """
    start_time = time.perf_counter()
    comparisons = 0
    low = 0
    high = len(sorted_items) - 1
    found_index = -1
    found_item = None

    while low <= high:
        comparisons += 1
        mid = (low + high) // 2
        mid_val = key_func(sorted_items[mid])

        if mid_val == target:
            found_index = mid
            found_item = sorted_items[mid]
            break
        elif mid_val < target:
            low = mid + 1
        else:
            high = mid - 1

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0

    return {
        "algorithm": "Binary Search",
        "found": found_index != -1,
        "index": found_index,
        "item": found_item,
        "comparisons": comparisons,
        "time_ms": round(elapsed_ms, 4),
        "complexity": "O(log n)",
    }


def compare_searches(
    items: List[Any],
    key_func: Callable[[Any], Any],
    target: Any
) -> Dict[str, Any]:
    """
    Executes both Linear and Binary Search on the dataset to benchmark comparisons and latency.
    Ensures Binary Search runs on a sorted snapshot of the data.
    """
    # 1. Linear search on raw data
    linear_res = linear_search(items, key_func, target)

    # 2. Sort snapshot by key for Binary Search
    sorted_items = sorted(items, key=key_func)
    binary_res = binary_search(sorted_items, key_func, target)

    return {
        "target": target,
        "total_items": len(items),
        "linear_search": linear_res,
        "binary_search": binary_res,
        "efficiency_ratio": (
            round(linear_res["comparisons"] / max(1, binary_res["comparisons"]), 2)
            if binary_res["comparisons"] > 0 else 1.0
        ),
    }
