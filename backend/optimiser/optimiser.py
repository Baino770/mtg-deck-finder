"""
MTG Card Purchase Optimiser
============================
Finds the cheapest combination of vendors to buy a set of Magic: The Gathering
cards, accounting for per-vendor shipping costs.

Uses Integer Linear Programming (ILP) via the PuLP library.

Dependencies:
    pulp

Problem formulation:
    - Decision variable x[card][vendor]: 1 if card is bought from vendor, else 0
    - Binary variable y[vendor]: 1 if any card is bought from vendor (triggers shipping), else 0
    - Objective: minimise sum of card prices + sum of shipping costs for used vendors i.e. sum(x[c][v] * price[c][v]) + sum(y[v] * shipping[v])
    - Constraint 1: each card must be bought from exactly one vendor, sum over v of x[c][v] == 1 
    - Constraint 2: if x[card][vendor] == 1, then y[vendor] must also be 1, x[c][v] <= y[v]
"""

import pulp


def optimise_card_purchases(cards: list[str], vendors: dict, prices: dict) -> dict:
    """
    Find the cheapest way to buy all cards across a set of vendors.

    Args:
        cards:
            List of card names you want to buy.
            Example: ["Black Lotus", "Counterspell", "Sol Ring"]

        vendors:
            Dict mapping vendor name -> shipping cost (float).
            Example: {"CardShark": 2.50, "MagicMadhouse": 1.99}

        prices:
            Nested dict: prices[card][vendor] = price (float).
            If a vendor doesn't stock a card, omit it or set to None.
            Example: {"Black Lotus": {"CardShark": 12.00, "MagicMadhouse": 14.50}}

    Returns:
        A dict with keys:
            "status":       "Optimal", "Infeasible", etc.
            "total_cost":   Total spend including shipping (float)
            "assignments":  Dict mapping card -> {"vendor": str, "price": float}
            "vendors_used": Dict mapping vendor -> {"shipping": float, "cards": list}
    """

    # --- Validate that every card has at least one vendor offering it ---
    vendor_names = list(vendors.keys())
    for card in cards:
        available = [v for v in vendor_names if prices.get(card, {}).get(v) is not None]
        if not available:
            raise ValueError(
                f"Card '{card}' has no vendors offering it. "
                "Add at least one price entry before solving."
            )

    # --- Build the ILP problem ---
    prob = pulp.LpProblem("MTG_Card_Optimiser", pulp.LpMinimize)

    # x[card][vendor] = 1 if we buy 'card' from 'vendor', else 0
    x = {
        card: {
            vendor: pulp.LpVariable(
                f"x_{card.replace(' ', '_')}_{vendor.replace(' ', '_')}",
                cat="Binary"
            )
            for vendor in vendor_names
            if prices.get(card, {}).get(vendor) is not None  # only where stocked
        }
        for card in cards
    }

    # y[vendor] = 1 if we buy anything from 'vendor' (pay shipping), else 0
    y = {
        vendor: pulp.LpVariable(f"y_{vendor.replace(' ', '_')}", cat="Binary")
        for vendor in vendor_names
    }

    # --- Objective: minimise card prices + shipping ---
    card_cost = pulp.lpSum(
        prices[card][vendor] * x[card][vendor]
        for card in cards
        for vendor in x[card]
    )
    shipping_cost = pulp.lpSum(
        vendors[vendor] * y[vendor]
        for vendor in vendor_names
    )
    prob += card_cost + shipping_cost, "Total_Cost"

    # --- Constraint 1: each card must be bought from exactly one vendor ---
    for card in cards:
        prob += (
            pulp.lpSum(x[card][vendor] for vendor in x[card]) == 1,
            f"buy_{card.replace(' ', '_')}_once"
        )

    # --- Constraint 2: buying a card from a vendor activates that vendor's shipping ---
    # If x[card][vendor] == 1, then y[vendor] must also be 1.
    # Enforced by: x[card][vendor] <= y[vendor] for all card, vendor pairs.
    for card in cards:
        for vendor in x[card]:
            prob += (
                x[card][vendor] <= y[vendor],
                f"activate_{vendor.replace(' ', '_')}_for_{card.replace(' ', '_')}"
            )

    # --- Solve ---
    # Using CBC solve
    # msg=0 suppresses solver output; set msg=1 to see solver logs.
    solver = pulp.PULP_CBC_CMD(msg=0)
    prob.solve(solver)

    status = pulp.LpStatus[prob.status]

    if status != "Optimal":
        return {"status": status, "total_cost": None, "assignments": {}, "vendors_used": {}}

    # --- Extract results ---
    assignments = {}
    for card in cards:
        for vendor in x[card]:
            if pulp.value(x[card][vendor]) > 0.5:  # treat as 1 (float safety)
                assignments[card] = {
                    "vendor": vendor,
                    "price": prices[card][vendor],
                }
                break

    vendors_used = {}
    for vendor in vendor_names:
        if pulp.value(y[vendor]) > 0.5:
            cards_from_vendor = [
                card for card, info in assignments.items()
                if info["vendor"] == vendor
            ]
            vendors_used[vendor] = {
                "shipping": vendors[vendor],
                "cards": cards_from_vendor,
            }

    return {
        "status": status,
        "total_cost": round(pulp.value(prob.objective), 2),
        "assignments": assignments,
        "vendors_used": vendors_used,
    }


def print_results(result: dict) -> None:
    """Pretty-print the optimisation results."""
    print(f"\nStatus: {result['status']}")

    if result["status"] != "Optimal":
        print("No optimal solution found.")
        return

    print(f"Total cost: £{result['total_cost']:.2f}\n")

    print("Vendor breakdown:")
    for vendor, info in result["vendors_used"].items():
        cards_subtotal = sum(
            result["assignments"][card]["price"]
            for card in info["cards"]
        )
        print(f"  {vendor} (shipping: £{info['shipping']:.2f})")
        for card in info["cards"]:
            price = result["assignments"][card]["price"]
            print(f"    • {card}: £{price:.2f}")
        print(f"    Subtotal: £{cards_subtotal + info['shipping']:.2f}")

    print(f"\nGrand total: £{result['total_cost']:.2f}")


# =============================================================================
# Example usage
# =============================================================================

if __name__ == "__main__":

    # Cards you want to buy
    cards = [
        "Black Lotus",
        "Counterspell",
        "Lightning Bolt",
        "Sol Ring",
        "Brainstorm",
    ]

    # Vendors and their shipping costs (in £)
    vendors = {
        "CardShark":     2.50,
        "MagicMadhouse": 1.99,
        "TCGPlayer":     3.99,
    }

    # Prices: prices[card][vendor] = price in £
    # If a vendor doesn't stock a card, leave it out of the inner dict.
    prices = {
        "Black Lotus": {
            "CardShark":     12.00,
            "MagicMadhouse": 14.50,
            "TCGPlayer":     11.00,
        },
        "Counterspell": {
            "CardShark":     1.20,
            "MagicMadhouse": 0.99,
            "TCGPlayer":     1.50,
        },
        "Lightning Bolt": {
            "CardShark":     0.50,
            "MagicMadhouse": 0.75,
            "TCGPlayer":     0.40,
        },
        "Sol Ring": {
            "CardShark":     2.00,
            "MagicMadhouse": 1.80,
            # TCGPlayer doesn't stock this one
        },
        "Brainstorm": {
            "CardShark":     0.30,
            "MagicMadhouse": 0.25,
            "TCGPlayer":     0.20,
        },
    }

    result = optimise_card_purchases(cards, vendors, prices)
    print_results(result)