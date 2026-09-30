import streamlit as st
import calendar
from datetime import date

from budget_ui import render_budget_reporting
from transactions import get_transactions
from config import CATEGORIES


st.title("Budgets & Reports")

st.caption(
    "Manage category budgets and review monthly spending"
)


# ---------------------------------------------------------
# Reporting Period
# ---------------------------------------------------------

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
        value=date.today().year,
        step=1
    )


# ---------------------------------------------------------
# Retrieve Transactions
# ---------------------------------------------------------

transactions = get_transactions(
    selected_year,
    selected_month
)


# ---------------------------------------------------------
# Budget Reporting
# ---------------------------------------------------------

render_budget_reporting(
    selected_year,
    selected_month,
    CATEGORIES,
    transactions
)