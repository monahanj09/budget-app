import streamlit as st
import pandas as pd
import calendar
from datetime import date

from cashflow import analyze_cashflow


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

        dataframe = pd.DataFrame(
            transactions,
            columns=[
                "ID",
                "Date",
                "Description",
                "Amount ($)",
                "Type",
                "Category",
                "Shared",
                "Shared Members",
                "Notes",
                "Recurring Rule ID"
            ]
        )

        dataframe["Cash Flow"] = dataframe.apply(
            lambda row:
                -row["Amount ($)"]
                if row["Type"] == "Expense"
                else row["Amount ($)"],
            axis=1
        )

        dataframe = dataframe.sort_values(
            by=["Date", "ID"]
        ).reset_index(drop=True)

        dataframe["Date"] = pd.to_datetime(
            dataframe["Date"]
        )

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

    # Daily balance table.
    daily_display = daily_balances[
        ["Date", "Start Balance", "End Balance"]
    ].copy()

    daily_display["Date"] = (
        daily_display["Date"].dt.strftime("%m/%d/%Y")
    )

    st.dataframe(
        daily_display,
        hide_index=True,
        column_config={
            "Date": st.column_config.DateColumn(
                "Date",
                format="MM/DD/YYYY"
            ),
            "Start Balance": st.column_config.NumberColumn(
                "Start Balance",
                format="$%.2f"
            ),
            "End Balance": st.column_config.NumberColumn(
                "End Balance",
                format="$%.2f"
            )
        }
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

    if net_cash_flow < 0:

        formatted_net_cash_flow = (
            f"-${abs(net_cash_flow):,.2f}"
        )

    else:

        formatted_net_cash_flow = (
            f"${net_cash_flow:,.2f}"
        )

    # Summary metrics.
    column1, column2, column3, column4 = st.columns(4)
    column5, column6, column7 = st.columns(3)
    column8, column9 = st.columns(2)

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
                "recover before end of selected month"
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

    column1.metric(
        "Income:",
        f"${income:,.2f}"
    )

    column2.metric(
        "Reimbursements:",
        f"${reimbursements:,.2f}"
    )

    column3.metric(
        "Expenses:",
        f"${expenses:,.2f}"
    )

    column4.metric(
        "Net Cash Flow:",
        formatted_net_cash_flow
    )

    column5.metric(
        "Projected End Balance:",
        f"${projected_end_balance:,.2f}"
    )

    column6.metric(
        "Lowest Balance:",
        f"${lowest_balance:,.2f}"
    )

    column7.metric(
        "Lowest Balance Date:",
        lowest_balance_date.strftime("%m/%d/%Y")
    )

    column8.metric(
        "Shared Expenses:",
        f"${shared_expenses:,.2f}"
    )

    column9.metric(
        "Expected Reimbursement:",
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

        column.markdown(f"**{weekday}**")

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

                with column.container(
                    border=True,
                    height=250
                ):

                    st.markdown(f"**{day}**")

                    if transactions:

                        day_transactions = dataframe[
                            dataframe["Date"] == calendar_date
                        ]

                        for _, transaction in (
                            day_transactions.iterrows()
                        ):

                            if transaction["Type"] == "Expense":

                                transaction_amount = (
                                    transaction["Amount ($)"]
                                )

                                formatted_amount = (
                                    f"-${transaction_amount:,.2f}"
                                )

                                transaction_color = "red"

                            else:

                                transaction_amount = (
                                    transaction["Amount ($)"]
                                )

                                formatted_amount = (
                                    f"+${transaction_amount:,.2f}"
                                )

                                transaction_color = "green"

                            st.markdown(
                                f'<span style="color: '
                                f'{transaction_color};">'
                                f'{transaction["Description"]}: '
                                f'{formatted_amount}</span>',
                                unsafe_allow_html=True
                            )

                    if day_balance < 0:

                        st.markdown(
                            '<span style="color: red; '
                            'font-weight: bold;">'
                            f'Balance: -${abs(day_balance):,.2f}'
                            '</span>',
                            unsafe_allow_html=True
                        )

                    else:

                        st.markdown(
                            f"**Balance: ${day_balance:,.2f}**"
                        )

    return dataframe