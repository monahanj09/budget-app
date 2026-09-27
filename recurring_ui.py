import streamlit as st
import pandas as pd
from datetime import date

from recurring import (
    add_recurring_transaction,
    get_recurring_transactions,
    delete_recurring_transaction,
    set_recurring_transaction_active
)


def render_recurring_transactions(household_size, categories):
    """Render recurring transaction creation and management."""

    st.header("Recurring Transactions")

    recur_shared = False
    recur_shared_members = None

    if household_size > 1:

        recur_shared = st.checkbox(
            "Shared Recurring Expense",
            key="recur_shared"
        )

        if recur_shared:

            recur_shared_members = st.number_input(
                "How many people split this recurring transaction? (including you)",
                min_value=2,
                max_value=household_size,
                value=household_size,
                step=1,
                key="recur_shared_members"
            )

    with st.form("recurring_transaction_form"):

        recur_name = st.text_input("Name:")

        recur_amount = st.number_input(
            "Recurring Amount:",
            min_value=0.00,
            step=1.0,
            format="%.2f"
        )

        recur_type = st.radio(
            "Recurring Type:",
            ["Expense", "Income", "Reimbursement"],
            horizontal=True
        )

        recur_category = st.selectbox(
            "Category:",
            categories,
            key="recur_category"
        )

        recur_notes = st.text_area("Notes:", key="recur_notes")

        recur_start_date = st.date_input(
            "Start Date:",
            value=date.today(),
            format="MM/DD/YYYY"
        )

        recur_frequency = st.selectbox(
            "Frequency:",
            ["Monthly", "Weekly", "Bi-weekly"]
        )

        recur_submitted = st.form_submit_button(
            "Add Recurring Transaction"
        )

    if recur_submitted:

        if not recur_name.strip():

            st.error(
                "You must enter a name for a recurring transaction."
            )

        elif recur_amount <= 0:

            st.error(
                "Recurring transaction amount must be at least $0.01"
            )

        else:

            add_recurring_transaction(
                name=recur_name.strip(),
                expected_amount=recur_amount,
                type=recur_type,
                category=recur_category,
                shared=int(recur_shared),
                shared_members=recur_shared_members,
                notes=recur_notes,
                start_date=recur_start_date.isoformat(),
                frequency=recur_frequency
            )

            st.success(
                "Recurring transaction created successfully."
            )

    # Display and manage existing recurring rules.
    recurring_transactions = get_recurring_transactions()

    if recurring_transactions:

        recurring_dataframe = pd.DataFrame(
            recurring_transactions,
            columns=[
                "ID",
                "Name",
                "Expected Amount",
                "Type",
                "Category",
                "Shared",
                "Shared Members",
                "Notes",
                "Start Date",
                "Frequency",
                "Active"
            ]
        )

        recurring_dataframe["Start Date"] = pd.to_datetime(
            recurring_dataframe["Start Date"]
        )

        recurring_dataframe["Shared"] = recurring_dataframe["Shared"].map(
            {
                0: "No",
                1: "Yes"
            }
        )

        recurring_dataframe["Active"] = recurring_dataframe["Active"].map(
            {
                0: "No",
                1: "Yes"
            }
        )

        recurring_table = st.dataframe(
            recurring_dataframe,
            hide_index=True,
            on_select="rerun",
            selection_mode="multi-row",
            column_config={
                "Expected Amount": st.column_config.NumberColumn(
                    "Expected Amount",
                    format="$%.2f"
                ),
                "Start Date": st.column_config.DateColumn(
                    "Start Date",
                    format="MM/DD/YYYY"
                ),
                "ID": None
            }
        )

        if recurring_table.selection.rows:

            selected_recur_rows = recurring_table.selection.rows
            selected_rules = recurring_dataframe.iloc[selected_recur_rows]
            selected_rule_ids = selected_rules["ID"].tolist()

            if st.button("Delete Selected"):

                for rule_id in selected_rule_ids:
                    delete_recurring_transaction(rule_id)

                st.rerun()

            if st.button("Deactivate Selected"):

                for rule_id in selected_rule_ids:
                    set_recurring_transaction_active(rule_id, 0)

                st.rerun()

            if st.button("Reactivate Selected"):

                for rule_id in selected_rule_ids:
                    set_recurring_transaction_active(rule_id, 1)

                st.rerun()

    else:

        st.info("No recurring transactions have been created.")