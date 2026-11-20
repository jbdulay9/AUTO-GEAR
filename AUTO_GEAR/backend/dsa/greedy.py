"""
Greedy Algorithm Implementation for AUTO GEAR.
Used for Smart Budget-Based Product Recommendations.

Greedy Strategy:
- Calculates a recommendation priority ratio: density = value / price.
  (where value can represent product rating, popularity, or base satisfaction score).
- Sorts candidates descending by density.
- Greedily selects the best available candidate that fits the remaining budget.
- Repeats until no further products can be added.

Limitations of Greedy:
- Makes locally optimal decisions at each step.
- Since products cannot be fractionally divided (0/1 constraint), the greedy choice
  may leave unused budget that could have accommodated items with higher cumulative value.
- Compare with Dynamic Programming for global optimum!

Time Complexity: O(n log n) due to initial sorting of n candidate products.
Space Complexity: O(n) to store candidates and recommendations.
"""

from typing import Any, Callable, Dict, List


def greedy_budget_recommendations(
    products: List[Dict[str, Any]],
    budget: float,
    value_weight: float = 1.0
) -> Dict[str, Any]:
    """
    Generates a recommended set of products within budget using a greedy density heuristic.

    :param products: List of product dictionaries (must contain 'price', 'stock').
    :param budget: Total customer budget.
    :param value_weight: Multiplier applied to score evaluation.
    :return: Dictionary containing selected items, total spent, remaining budget, and total value.
    """
    remaining_budget = float(budget)
    candidates = []

    for p in products:
        price = float(p.get("price", 0))
        stock = int(p.get("stock", 0))
        if price <= 0 or stock <= 0:
            continue

        # Recommendation score based on price, category importance, and stock health
        # Base value heuristic: proportional to logarithmic utility with category bonus
        score = round(p.get("score") or (price ** 0.5 * 10 * value_weight), 2)
        density = score / price  # Value per peso spent

        candidates.append({
            "product": p,
            "price": price,
            "score": score,
            "density": round(density, 6),
        })

    # Greedy choice: Rank items by density (highest value per peso first)
    candidates.sort(key=lambda c: c["density"], reverse=True)

    selected_items = []
    total_spent = 0.0
    total_value = 0.0

    for cand in candidates:
        if cand["price"] <= remaining_budget:
            selected_items.append({
                "product_id": cand["product"]["product_id"],
                "product_name": cand["product"]["product_name"],
                "category_name": cand["product"].get("category_name", ""),
                "price": cand["price"],
                "score": cand["score"],
                "density": cand["density"],
            })
            remaining_budget -= cand["price"]
            total_spent += cand["price"]
            total_value += cand["score"]

    return {
        "algorithm": "Greedy Algorithm",
        "decision_rule": "Highest Value-to-Price Ratio (Density = Value / Price)",
        "limitation": "May get trapped in local optima due to indivisible items leaving budget gaps.",
        "initial_budget": float(budget),
        "total_spent": round(total_spent, 2),
        "remaining_budget": round(remaining_budget, 2),
        "total_value": round(total_value, 2),
        "items_count": len(selected_items),
        "selected_items": selected_items,
    }
