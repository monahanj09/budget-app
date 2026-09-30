import streamlit as st
import calendar
from datetime import date

from transactions import get_transactions
from recurring import generate_recurring_transactions
from cashflow_ui import render_cashflow_dashboard
from cashflow import calculate_month_starting_balance


st.title("Dashboard")

st.caption("Cash-flow forecast and monthly overview")


month_column, year_column = st.columns(2)

with month_column:

    selected_month = st.selectbox(
        "Month:",
        range(1, 13),
        format_func=lambda month: calendar.month_name[month],
        index=date.today().month - 1
    )

with year_column:

    selected_year = st.number_input(
        "Year:",
        min_value=2022,
        value=date.today().year
    )


starting_balance = calculate_month_starting_balance(
    selected_year,
    selected_month
)

if starting_balance is None:

    st.warning(
        "The selected month is before your initial balance month, "
        "or an initial balance has not been configured."
    )

    st.stop()


st.metric(
    "Starting Balance",
    (
        f"-${abs(starting_balance):,.2f}"
        if starting_balance < 0
        else f"${starting_balance:,.2f}"
    )
)


generate_recurring_transactions(
    selected_year,
    selected_month
)

transactions = get_transactions(
    selected_year,
    selected_month
)


render_cashflow_dashboard(
    selected_year,
    selected_month,
    starting_balance,
    transactions
)