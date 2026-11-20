from typing import Any, Dict, List


def knapsack_dp_recommendations(
    products: List[Dict[str, Any]],
    budget: float,
    scale_factor: int = 50
) -> Dict[str, Any]:
    """
    Computes the globally optimal product bundle using 0/1 Knapsack Dynamic Programming tabulation.

    :param products: Available product dictionaries (containing 'price' and optional 'score').
    :param budget: Total customer budget in PHP.
    :param scale_factor: Discretization unit for price to keep DP table size optimal.
    :return: Optimal selection dictionary with items, total value, and comparison metrics.
    """
    # 1. Filter eligible in-stock products
    candidates = []
    for p in products:
        price = float(p.get("price", 0))
        stock = int(p.get("stock", 0))
        if price > 0 and stock > 0 and price <= budget:
            score = round(p.get("score") or (price ** 0.5 * 10), 2)
            candidates.append({
                "product": p,
                "price": price,
                "weight": max(1, int(round(price / scale_factor))),
                "score": score,
            })

    n = len(candidates)
    W = int(round(budget / scale_factor))

    # If no items fit budget
    if n == 0 or W <= 0:
        return {
            "algorithm": "Dynamic Programming (0/1 Knapsack)",
            "technique": "Tabulation",
            "initial_budget": budget,
            "total_spent": 0.0,
            "remaining_budget": budget,
            "total_value": 0.0,
            "items_count": 0,
            "selected_items": [],
            "dp_table_dimensions": f"0 x 0",
        }

    # 2. Construct DP table: dp[i][w] = max value using subset of first i items with capacity w
    dp = [[0.0 for _ in range(W + 1)] for _ in range(n + 1)]

    for i in range(1, n + 1):
        wt = candidates[i - 1]["weight"]
        val = candidates[i - 1]["score"]
        for w in range(W + 1):
            if wt <= w:
                dp[i][w] = max(dp[i - 1][w], dp[i - 1][w - wt] + val)
            else:
                dp[i][w] = dp[i - 1][w]

    # 3. Reconstruct the optimal solution
    selected_items = []
    w_curr = W
    total_spent = 0.0

    for i in range(n, 0, -1):
        # If value differs from cell above, item i-1 was included in optimal knapsack
        if dp[i][w_curr] != dp[i - 1][w_curr]:
            item_data = candidates[i - 1]
            selected_items.append({
                "product_id": item_data["product"]["product_id"],
                "product_name": item_data["product"]["product_name"],
                "category_name": item_data["product"].get("category_name", ""),
                "price": item_data["price"],
                "score": item_data["score"],
            })
            w_curr -= item_data["weight"]
            total_spent += item_data["price"]

    # Re-order to original sequence
    selected_items.reverse()
    total_value = dp[n][W]

    return {
        "algorithm": "Dynamic Programming (0/1 Knapsack)",
        "technique": "Tabulation (Optimal Substructure & Overlapping Subproblems)",
        "initial_budget": float(budget),
        "total_spent": round(total_spent, 2),
        "remaining_budget": round(budget - total_spent, 2),
        "total_value": round(total_value, 2),
        "items_count": len(selected_items),
        "selected_items": selected_items,
        "dp_table_dimensions": f"{n + 1} x {W + 1}",
    }


def compare_greedy_vs_dp(
    products: List[Dict[str, Any]],
    budget: float
) -> Dict[str, Any]:
    """
    Runs both Greedy heuristic and 0/1 Knapsack Dynamic Programming on the same catalog
    and budget, producing an algorithmic comparison report.
    """
    from backend.dsa.greedy import greedy_budget_recommendations

    greedy_res = greedy_budget_recommendations(products, budget)
    dp_res = knapsack_dp_recommendations(products, budget)

    value_diff = round(dp_res["total_value"] - greedy_res["total_value"], 2)
    spent_diff = round(dp_res["total_spent"] - greedy_res["total_spent"], 2)

    return {
        "budget": budget,
        "greedy": greedy_res,
        "dynamic_programming": dp_res,
        "comparison": {
            "value_difference": value_diff,
            "dp_superior_by_value": value_diff > 0,
            "analysis": (
                "Dynamic programming explored all subproblems to achieve global optimality, "
                f"yielding {value_diff} more value units than the greedy heuristic."
                if value_diff > 0
                else "Both algorithms found equally performant item sets for this specific budget constraint."
            ),
        },
    }
