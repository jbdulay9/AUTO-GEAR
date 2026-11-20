from typing import Any, Dict, List


def build_accessory_bundles(
    products_by_category: Dict[str, List[Dict[str, Any]]],
    category_sequence: List[str],
    max_budget: float,
    max_results: int = 10
) -> List[Dict[str, Any]]:
    """
    Finds valid product bundles choosing exactly one product per category in category_sequence
    such that the total price is <= max_budget.

    :param products_by_category: Mapping from category name to list of product dicts.
    :param category_sequence: Ordered list of categories required in the bundle.
    :param max_budget: Upper spending limit in PHP.
    :param max_results: Maximum number of bundle solutions to return.
    :return: List of valid bundle dictionaries.
    """
    valid_bundles: List[Dict[str, Any]] = []
    current_bundle: List[Dict[str, Any]] = []

    def backtrack(stage_idx: int, current_cost: float):
        # Base condition: Found a valid item for each required category
        if stage_idx == len(category_sequence):
            valid_bundles.append({
                "bundle_id": len(valid_bundles) + 1,
                "items": list(current_bundle),
                "total_cost": round(current_cost, 2),
                "budget": max_budget,
                "savings": round(max_budget - current_cost, 2),
                "items_count": len(current_bundle),
            })
            return

        # Prune if max requested solutions reached
        if len(valid_bundles) >= max_results:
            return

        cat_name = category_sequence[stage_idx]
        candidate_products = products_by_category.get(cat_name, [])

        for product in candidate_products:
            price = float(product.get("price", 0))

            # Constraint check & pruning: if adding exceeds max_budget, prune branch
            if current_cost + price <= max_budget:
                # 1. Choose
                current_bundle.append(product)

                # 2. Explore deeper
                backtrack(stage_idx + 1, current_cost + price)

                # 3. Un-choose (Backtrack)
                current_bundle.pop()

                if len(valid_bundles) >= max_results:
                    break

    # Begin recursive search from index 0 with 0.0 initial cost
    backtrack(0, 0.0)

    # Sort generated bundles by total cost descending (maximizing budget utilization)
    valid_bundles.sort(key=lambda b: b["total_cost"], reverse=True)
    return valid_bundles
