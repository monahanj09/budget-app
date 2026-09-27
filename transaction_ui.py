import streamlit as st
from datetime import date

from transactions import add_transaction


def render_add_transaction(household_size, categories):
    """Render the form for adding a transaction."""

    st.header("Add Transaction")

    # Shared transaction checkbox remains outside the form so the
    # shared-members input can update dynamically.
    transaction_shared = False
    transaction_shared_members = None

    if household_size > 1:

        transaction_shared = st.checkbox("Shared Expense")

        if transaction_shared:

            transaction_shared_members = st.number_input(
                "How many people split this transaction? (including you)",
                min_value=2,
                max_value=household_size,
                value=household_size,
                step=1
            )

    with st.form("transaction_form"):

        transaction_date = st.date_input(
            "Date:",
            value=date.today(),
            format="MM/DD/YYYY"
        )

        transaction_type = st.radio(
            "Transaction Type:",
            ["Expense", "Income", "Reimbursement"],
            horizontal=True
        )

        transaction_description = st.text_input(
            "Description:",
            ""
        )

        transaction_amount = st.number_input(
            "Amount:",
            min_value=0.00,
            step=1.0,
            format="%.2f"
        )

        transaction_category = st.selectbox(
            "Category:",
            categories
        )

        transaction_notes = st.text_area("Notes:")

        submitted = st.form_submit_button("Add Transaction")

    if submitted:

        if not transaction_description.strip():

            st.error("You must enter a transaction description.")

        elif transaction_amount <= 0:

            st.error("Transaction amount must be at least $0.01")

        else:

            add_transaction(
                date=transaction_date.isoformat(),
                name=transaction_description.strip(),
                amount=transaction_amount,
                transaction_type=transaction_type,
                category=transaction_category,
                shared=int(transaction_shared),
                notes=transaction_notes,
                shared_members=transaction_shared_members
            )

            st.success("Transaction submitted successfully.")