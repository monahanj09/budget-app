import streamlit as st
import calendar
from datetime import date

from config import CATEGORIES
from transactions import get_transactions
from recurring import generate_recurring_transactions
from budget_ui import render_budget_reporting


st.title("Budgets & Reports")
st.caption("Manage category budgets and review monthly spending")


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


# Ensure recurring transactions exist for the selected month.
generate_recurring_transactions(
    selected_year,
    selected_month
)

transactions = get_transactions(
    selected_year,
    selected_month
)


render_budget_reporting(
    selected_year,
    selected_month,
    CATEGORIES,
    transactions
)