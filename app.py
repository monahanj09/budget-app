import streamlit as st

from database import create_tables


# Create database tables when the app starts.
create_tables()


st.set_page_config(
    page_title="FlowAhead",
    page_icon="📈",
    layout="wide"
)


dashboard_page = st.Page(
    "pages/dashboard.py",
    title="Dashboard",
    icon=":material/dashboard:",
    default=True
)

transactions_page = st.Page(
    "pages/transactions.py",
    title="Transactions",
    icon=":material/receipt_long:"
)

recurring_page = st.Page(
    "pages/recurring.py",
    title="Recurring",
    icon=":material/repeat:"
)

budgets_page = st.Page(
    "pages/budgets.py",
    title="Budgets & Reports",
    icon=":material/bar_chart:"
)

settings_page = st.Page(
    "pages/settings.py",
    title="Settings",
    icon=":material/settings:"
)


navigation = st.navigation(
    {
        "FlowAhead": [
            dashboard_page,
            transactions_page,
            recurring_page,
            budgets_page
        ],
        "": [
            settings_page
        ]
    }
)


navigation.run()