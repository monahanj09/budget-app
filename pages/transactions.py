import streamlit as st
import calendar
from datetime import date

from config import CATEGORIES
from database import get_setting
from transactions import (
    get_transactions,
    prepare_transaction_dataframe
)
from recurring import generate_recurring_transactions
from transaction_ui import render_add_transaction
from transaction_management_ui import render_transaction_management


st.title("Transactions")

st.caption(
    "Add, review, edit, and delete transactions"
)


# ---------------------------------------------------------
# Household Settings
# ---------------------------------------------------------

household_size = get_setting(
    "household_size"
)

if household_size is None:
    household_size = 1

household_size = int(
    household_size
)


# ---------------------------------------------------------
# Add Transaction
# ---------------------------------------------------------

render_add_transaction(
    household_size,
    CATEGORIES
)


# ---------------------------------------------------------
# Transaction History
# ---------------------------------------------------------

st.header("Transaction History")

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
# Generate Recurring Transactions
# ---------------------------------------------------------

generate_recurring_transactions(
    selected_year,
    selected_month
)


# ---------------------------------------------------------
# Retrieve Transactions
# ---------------------------------------------------------

transactions = get_transactions(
    selected_year,
    selected_month
)

dataframe = prepare_transaction_dataframe(
    transactions
)


# ---------------------------------------------------------
# Transaction Management
# ---------------------------------------------------------

render_transaction_management(
    dataframe,
    transactions,
    household_size,
    CATEGORIES
)