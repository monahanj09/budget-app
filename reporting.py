def calculate_category_spending(transactions):
    """Calculate total expense spending by category."""

    category_spending = {}

    for transaction in transactions:

        if transaction[4] == "Expense":

            amount = transaction[3]
            category = transaction[5]

            if category in category_spending:

                category_spending[category] += amount

            else:

                category_spending[category] = amount

    return category_spending

def calculate_budget_vs_actual(category_budgets, category_spending):
    """Compare category budgets against actual spending."""

    budget_report = {}

    for category in category_budgets:

        budget_amount = category_budgets[category]
        actual_spending = category_spending.get(category, 0.0)

        spending_difference = budget_amount - actual_spending

        budget_report[category] = {
            "budget": budget_amount,
            "actual": actual_spending,
            "remaining": spending_difference
        }

    return budget_report

def calculate_budget_summary(budget_report):
    """Calculate overall monthly category budget totals."""

    total_budget = 0.0
    total_actual = 0.0
    categories_over_budget = 0

    for category in budget_report:

        category_report = budget_report[category]

        total_budget += category_report["budget"]
        total_actual += category_report["actual"]

        if category_report["remaining"] < 0:

            categories_over_budget += 1

    overall_remaining_budget = total_budget - total_actual

    budget_summary = {
        "total_budget": total_budget,
        "total_actual": total_actual,
        "remaining": overall_remaining_budget,
        "categories_over_budget": categories_over_budget
    }

    return budget_summary