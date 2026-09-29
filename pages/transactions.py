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
st.caption("Add, review, edit, and delete transactions")


# Household size is needed for shared expenses.
household_size_setting = get_setting("household_size")

if household_size_setting is None:
    household_size = 1
else:
    household_size = int(household_size_setting)


# Add transaction interface.
render_add_transaction(
    household_size,
    CATEGORIES
)


# Transaction history.
st.header("Transaction History")

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

dataframe = prepare_transaction_dataframe(
    transactions
)


render_transaction_management(
    dataframe,
    transactions,
    household_size,
    CATEGORIES
)