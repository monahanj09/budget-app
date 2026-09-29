import streamlit as st

from config import CATEGORIES
from database import get_setting
from recurring_ui import render_recurring_transactions


st.title("Recurring")
st.caption("Create and manage recurring transactions")


# Household size is needed for shared recurring expenses.
household_size_setting = get_setting("household_size")

if household_size_setting is None:
    household_size = 1
else:
    household_size = int(household_size_setting)


render_recurring_transactions(
    household_size,
    CATEGORIES
)