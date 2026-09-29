import streamlit as st
import calendar
from datetime import date

from database import (
    get_starting_balance,
    set_starting_balance
)

from transactions import get_transactions
from recurring import generate_recurring_transactions
from cashflow_ui import render_cashflow_dashboard

st.title("Dashboard")

st.caption("Cash-flow forecast and monthly overview")

selected_month = st.selectbox(
    "Month:",
    range(1, 13),
    format_func=lambda month: calendar.month_name[month],
    index=date.today().month - 1
)

selected_year = st.number_input(
    "Year:",
    min_value=2022,
    value=date.today().year
)

starting_balance = get_starting_balance(
    selected_year,
    selected_month
)

entered_starting_balance = st.number_input(
    "Starting Balance ($):",
    value=float(starting_balance),
    step=1.00,
    format="%.2f"
)

save_starting_balance = st.button(
    "Save Starting Balance"
)

if save_starting_balance:

    set_starting_balance(
        selected_year,
        selected_month,
        entered_starting_balance
    )

    st.rerun()

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