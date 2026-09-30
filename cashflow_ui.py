import streamlit as st
import pandas as pd
import calendar
from datetime import date

from cashflow import analyze_cashflow
from transactions import prepare_transaction_dataframe
from ui_components import (
    render_metric_card,
    render_calendar_day
)


def render_cashflow_dashboard(
    selected_year,
    selected_month,
    starting_balance,
    transactions
):
    """Render monthly cash-flow analysis, metrics, and calendar."""

    last_day = calendar.monthrange(
        selected_year,
        selected_month
    )[1]

    month_start = date(
        selected_year,
        selected_month,
        1
    )

    month_end = date(
        selected_year,
        selected_month,
        last_day
    )

    all_dates = pd.date_range(
        start=month_start,
        end=month_end
    )

    # Construct calendar and aggregate transaction cash flow by date.
    daily_balances = pd.DataFrame({
        "Date": all_dates
    })

    dataframe = None

    if transactions:

        dataframe = prepare_transaction_dataframe(transactions)

        daily_transaction_totals = (
            dataframe.groupby("Date")["Cash Flow"]
            .sum()
            .reset_index()
        )

        daily_balances = daily_balances.merge(
            daily_transaction_totals,
            on="Date",
            how="left"
        )

        daily_balances["Cash Flow"] = (
            daily_balances["Cash Flow"].fillna(0)
        )

    else:

        daily_balances["Cash Flow"] = 0.0

    daily_balances["End Balance"] = (
        starting_balance
        + daily_balances["Cash Flow"].cumsum()
    )

    daily_balances["Start Balance"] = (
        daily_balances["End Balance"]
        .shift(1)
        .fillna(starting_balance)
    )

    cashflow_analysis = analyze_cashflow(
        daily_balances
    )

    # Calculate monthly totals and shared expenses.
    if transactions:

        dataframe["Shared"] = dataframe["Shared"].map({
            0: "No",
            1: "Yes"
        })

        income = dataframe[
            dataframe["Type"] == "Income"
        ]["Amount ($)"].sum()

        expenses = dataframe[
            dataframe["Type"] == "Expense"
        ]["Amount ($)"].sum()

        reimbursements = dataframe[
            dataframe["Type"] == "Reimbursement"
        ]["Amount ($)"].sum()

        # Legacy handling for transactions created before
        # shared_members was added.
        incomplete_shared_expenses = dataframe[
            (dataframe["Type"] == "Expense")
            & (dataframe["Shared"] == "Yes")
            & (dataframe["Shared Members"].isna())
        ]

        incomplete_shared_count = len(
            incomplete_shared_expenses
        )

        if incomplete_shared_count > 0:

            st.warning(
                f"{incomplete_shared_count} shared expense(s) are "
                "missing split information. Add the number of people "
                "sharing each expense to include them in shared expense "
                "and reimbursement calculations."
            )

        shared_expense_dataframe = dataframe[
            (dataframe["Type"] == "Expense")
            & (dataframe["Shared"] == "Yes")
            & (dataframe["Shared Members"] > 1)
        ].copy()

        shared_expense_dataframe["User Share"] = (
            shared_expense_dataframe["Amount ($)"]
            / shared_expense_dataframe["Shared Members"]
        )

        shared_expense_dataframe["Others Share"] = (
            shared_expense_dataframe["Amount ($)"]
            - shared_expense_dataframe["User Share"]
        )

        expected_reimbursement = (
            shared_expense_dataframe["Others Share"].sum()
        )

        shared_expenses = (
            shared_expense_dataframe["Amount ($)"].sum()
        )

    else:

        income = 0.0
        expenses = 0.0
        reimbursements = 0.0
        shared_expenses = 0.0
        expected_reimbursement = 0.0

    net_cash_flow = (
        income
        + reimbursements
        - expenses
    )

    projected_end_balance = (
        daily_balances["End Balance"].iloc[-1]
    )

    lowest_balance = (
        daily_balances["End Balance"].min()
    )

    lowest_balance_index = (
        daily_balances["End Balance"].idxmin()
    )

    lowest_balance_date = daily_balances.loc[
        lowest_balance_index,
        "Date"
    ]

    # Format values that may be negative consistently.
    if net_cash_flow < 0:

        formatted_net_cash_flow = (
            f"-${abs(net_cash_flow):,.2f}"
        )

    else:

        formatted_net_cash_flow = (
            f"${net_cash_flow:,.2f}"
        )

    if projected_end_balance < 0:

        formatted_projected_end_balance = (
            f"-${abs(projected_end_balance):,.2f}"
        )

    else:

        formatted_projected_end_balance = (
            f"${projected_end_balance:,.2f}"
        )

    if lowest_balance < 0:

        formatted_lowest_balance = (
            f"-${abs(lowest_balance):,.2f}"
        )

    else:

        formatted_lowest_balance = (
            f"${lowest_balance:,.2f}"
        )

    # Cash-flow warning.
    if cashflow_analysis["has_shortfall"]:

        first_negative_date = (
            cashflow_analysis["first_negative_date"]
        )

        minimum_cash_needed = (
            cashflow_analysis["minimum_cash_needed"]
        )

        recovery_date = (
            cashflow_analysis["recovery_date"]
        )

        if recovery_date is not None:

            additional_warning = (
                "Projected recovery date: "
                f"{recovery_date.strftime('%m/%d/%Y')}."
            )

        else:

            additional_warning = (
                "Projected recovery date: Account does not "
                "recover before end of selected month."
            )

        warning_message = (
            "Projected cash shortfall detected.\n\n"
            f"First negative balance: "
            f"{first_negative_date.strftime('%m/%d/%Y')}.\n\n"
            f"Minimum additional cash needed: "
            f"${minimum_cash_needed:,.2f}.\n\n"
        )

        warning_message += additional_warning

        st.warning(warning_message)

    # Monthly cash-flow summary.
    st.subheader("Monthly Cash Flow")

    column1, column2, column3, column4 = st.columns(4)

    with column1:

        render_metric_card(
            "Income",
            f"${income:,.2f}"
        )

    with column2:

        render_metric_card(
            "Reimbursements",
            f"${reimbursements:,.2f}"
        )

    with column3:

        render_metric_card(
            "Expenses",
            f"${expenses:,.2f}"
        )

    with column4:

        render_metric_card(
            "Net Cash Flow",
            formatted_net_cash_flow
        )

    # Balance forecast.
    st.subheader("Balance Forecast")

    column5, column6, column7 = st.columns(3)

    with column5:

        render_metric_card(
            "Projected End Balance",
            formatted_projected_end_balance
        )

    with column6:

        render_metric_card(
            "Lowest Balance",
            formatted_lowest_balance
        )

    with column7:

        render_metric_card(
            "Lowest Balance Date",
            lowest_balance_date.strftime("%m/%d/%Y")
        )

    # Shared-expense summary.
    st.subheader("Shared Expenses")

    column8, column9 = st.columns(2)

    with column8:

        render_metric_card(
            "Shared Expenses",
            f"${shared_expenses:,.2f}"
        )

    with column9:

        render_metric_card(
            "Expected Reimbursement",
            f"${expected_reimbursement:,.2f}"
        )

    # Cash-flow calendar.
    st.header("Cash Flow Calendar")

    weekday_columns = st.columns(7)

    weekdays = [
        "Sunday",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday"
    ]

    for column, weekday in zip(
        weekday_columns,
        weekdays
    ):

        column.markdown(
            f"""
            <div style="
                text-align: center;
                font-weight: bold;
                margin-bottom: 4px;
            ">
                {weekday}
            </div>
            """,
            unsafe_allow_html=True
        )

    month_calendar = calendar.Calendar(
        firstweekday=6
    )

    calendar_weeks = month_calendar.monthdayscalendar(
        selected_year,
        selected_month
    )

    for week in calendar_weeks:

        week_columns = st.columns(7)

        for column, day in zip(
            week_columns,
            week
        ):

            if day != 0:

                calendar_date = pd.Timestamp(
                    year=selected_year,
                    month=selected_month,
                    day=day
                )

                day_balance = daily_balances.loc[
                    daily_balances["Date"] == calendar_date,
                    "End Balance"
                ].iloc[0]

                if transactions:

                    day_transactions = dataframe[
                        dataframe["Date"] == calendar_date
                    ]

                else:

                    day_transactions = None

                with column:

                    render_calendar_day(
                        day,
                        day_balance,
                        day_transactions
                    )

    return dataframe