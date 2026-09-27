import streamlit as st
import calendar
from datetime import date

from database import (
    create_tables,
    set_starting_balance,
    get_starting_balance,
)

from transactions import get_transactions
from recurring import generate_recurring_transactions
from transaction_ui import render_add_transaction
from settings_ui import render_household_settings
from recurring_ui import render_recurring_transactions
from budget_ui import render_budget_reporting
from cashflow_ui import render_cashflow_dashboard
from transaction_management_ui import render_transaction_management

# Create database tables when the app starts
create_tables()


st.set_page_config(
    page_title="FlowAhead",
    page_icon="📈",
    layout="wide"
)


st.title("Budget App")
st.write("Personal household budget tracker")

if "editing" not in st.session_state:
    st.session_state["editing"] = False

categories = [
    "Paycheck",
    "Housing",
    "Utilities",
    "Groceries",
    "Dining",
    "Transportation",
    "Pets",
    "Credit Card",
    "Subscriptions",
    "Entertainment",
    "Shopping",
    "Healthcare",
    "Shared Contributions",
    "Other"
]

## Have user enter household size setting for future shared expense calculations

household_size = render_household_settings()

render_add_transaction(household_size, categories)

render_recurring_transactions(household_size, categories)

st.header("Monthly Transactions")

## Select month and year for viewing and possible updating of starting monthly balance

selected_month = st.selectbox("Month:", range(1, 13),
                                         format_func=lambda month: calendar.month_name[month],index=date.today().month - 1)

selected_year = st.number_input("Year:", min_value=2022, value=date.today().year)

## Define starting monthly balance

starting_balance = get_starting_balance(selected_year, selected_month)

## Update monthly balance

entered_starting_balance = st.number_input("Starting Balance ($):", value = float(starting_balance), step=1.00, format="%.2f")

save_starting_balance = st.button("Save Starting Balance")

if save_starting_balance:
    set_starting_balance(
        selected_year,
        selected_month,
        entered_starting_balance
    )
    st.rerun()

## Generate recurring transactions for currently displayed month

generate_recurring_transactions(selected_year, selected_month)

transactions = get_transactions(selected_year, selected_month)

render_budget_reporting(
    selected_year,
    selected_month,
    categories,
    transactions
)

dataframe = render_cashflow_dashboard(
    selected_year,
    selected_month,
    starting_balance,
    transactions
)

render_transaction_management(
    dataframe,
    transactions,
    household_size,
    categories
)