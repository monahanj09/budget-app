import streamlit as st
import pandas as pd
from datetime import date, timedelta

from database import (
    set_category_budget,
    get_category_budgets
)

from transactions import get_transactions

from reporting import (
    calculate_category_spending,
    calculate_budget_vs_actual,
    calculate_budget_summary,
    compare_monthly_spending
)

from ui_components import render_metric_card


def render_budget_reporting(
    selected_year,
    selected_month,
    categories,
    transactions
):
    """Render category budget management and monthly spending reports."""

    # ---------------------------------------------------------
    # Retrieve budget and spending data
    # ---------------------------------------------------------

    category_budgets = get_category_budgets(
        selected_year,
        selected_month
    )

    budget_categories = [
        category for category in categories
        if category not in [
            "Paycheck",
            "Shared Contributions"
        ]
    ]

    category_spending = calculate_category_spending(
        transactions
    )

    # Compare established category budgets against actual spending.
    budget_report = calculate_budget_vs_actual(
        category_budgets,
        category_spending
    )

    budget_summary = calculate_budget_summary(
        budget_report
    )

    # ---------------------------------------------------------
    # Budget Overview
    # ---------------------------------------------------------

    st.subheader("Budget Overview")

    if budget_report:

        budget_dataframe = pd.DataFrame.from_dict(
            budget_report,
            orient="index"
        )

        budget_dataframe = (
            budget_dataframe.reset_index()
        )

        budget_dataframe = budget_dataframe.rename(
            columns={
                "index": "Category",
                "budget": "Budget",
                "actual": "Actual",
                "remaining": "Remaining"
            }
        )

        budget_dataframe["% Used"] = (
            budget_dataframe["Actual"]
            / budget_dataframe["Budget"]
        ) * 100

        if budget_summary["remaining"] < 0:

            formatted_budget_remaining = (
                f"-${abs(budget_summary['remaining']):,.2f}"
            )

        else:

            formatted_budget_remaining = (
                f"${budget_summary['remaining']:,.2f}"
            )

        (
            budget_column1,
            budget_column2,
            budget_column3,
            budget_column4
        ) = st.columns(4)

        with budget_column1:

            render_metric_card(
                "Total Budget",
                f"${budget_summary['total_budget']:,.2f}"
            )

        with budget_column2:

            render_metric_card(
                "Actual Spending",
                f"${budget_summary['total_actual']:,.2f}"
            )

        with budget_column3:

            render_metric_card(
                "Budget Remaining",
                formatted_budget_remaining
            )

        with budget_column4:

            render_metric_card(
                "Categories Over Budget",
                budget_summary["categories_over_budget"]
            )

        st.dataframe(
            budget_dataframe,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Budget": st.column_config.NumberColumn(
                    "Budget",
                    format="$%.2f"
                ),
                "Actual": st.column_config.NumberColumn(
                    "Actual",
                    format="$%.2f"
                ),
                "Remaining": st.column_config.NumberColumn(
                    "Remaining",
                    format="$%.2f"
                ),
                "% Used": st.column_config.NumberColumn(
                    "% Used",
                    format="%.1f%%"
                )
            }
        )

    else:

        st.info(
            "No category budgets have been established "
            "for this month."
        )

    # ---------------------------------------------------------
    # Category Budgets
    # ---------------------------------------------------------

    st.subheader("Category Budgets")

    with st.container(border=True):

        category_column, amount_column = st.columns(2)

        with category_column:

            selected_budget_category = st.selectbox(
                "Budget Category:",
                budget_categories
            )

        current_budget_amount = category_budgets.get(
            selected_budget_category,
            0.0
        )

        with amount_column:

            entered_budget_amount = st.number_input(
                "Monthly Budget ($):",
                min_value=0.0,
                value=float(current_budget_amount),
                step=10.0,
                format="%.2f"
            )

        save_category_budget = st.button(
            "Save Category Budget"
        )

    if save_category_budget:

        if entered_budget_amount <= 0:

            st.error(
                "Category budget must be at least $0.01"
            )

        else:

            set_category_budget(
                selected_year,
                selected_month,
                selected_budget_category,
                entered_budget_amount
            )

            st.rerun()

    # ---------------------------------------------------------
    # Month-over-Month Spending
    # ---------------------------------------------------------

    st.subheader("Month-over-Month Spending")

    current_month_start = date(
        selected_year,
        selected_month,
        1
    )

    previous_month_date = (
        current_month_start
        - timedelta(days=1)
    )

    previous_transactions = get_transactions(
        previous_month_date.year,
        previous_month_date.month
    )

    previous_category_spending = (
        calculate_category_spending(
            previous_transactions
        )
    )

    monthly_comparison = compare_monthly_spending(
        category_spending,
        previous_category_spending
    )

    if monthly_comparison:

        monthly_comparison_dataframe = (
            pd.DataFrame.from_dict(
                monthly_comparison,
                orient="index"
            )
        )

        monthly_comparison_dataframe = (
            monthly_comparison_dataframe.reset_index()
        )

        monthly_comparison_dataframe = (
            monthly_comparison_dataframe.rename(
                columns={
                    "index": "Category",
                    "current": "Current Month",
                    "previous": "Previous Month",
                    "change": "Change",
                    "percent_change": "% Change"
                }
            )
        )

        st.dataframe(
            monthly_comparison_dataframe,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Current Month":
                    st.column_config.NumberColumn(
                        "Current Month",
                        format="$%.2f"
                    ),
                "Previous Month":
                    st.column_config.NumberColumn(
                        "Previous Month",
                        format="$%.2f"
                    ),
                "Change":
                    st.column_config.NumberColumn(
                        "Change",
                        format="$%.2f"
                    ),
                "% Change":
                    st.column_config.NumberColumn(
                        "% Change",
                        format="%.1f%%"
                    )
            }
        )

    else:

        st.info(
            "No spending data is available for comparison."
        )