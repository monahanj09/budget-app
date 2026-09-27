import streamlit as st
import pandas as pd

from transactions import (
    delete_transaction,
    update_transaction
)


def render_transaction_management(
    dataframe,
    transactions,
    household_size,
    categories
):
    """Render transaction table, deletion controls, and transaction editing."""

    if transactions:

        table_event = st.dataframe(
            dataframe,
            hide_index=True,
            on_select="rerun",
            selection_mode="multi-row",
            column_config={
                "Date": st.column_config.DatetimeColumn(
                    "Date",
                    format="MM/DD/YYYY"
                ),
                "Amount ($)": st.column_config.NumberColumn(
                    "Amount ($)",
                    format="$%.2f"
                ),
                "Cash Flow": None,
                "ID": None,
                "Recurring Rule ID": None
            }
        )

        selected_rows = table_event.selection.rows

        selected_ids = []
        deletable_ids = []
        recurring_transaction_ids = []

        # Protect generated recurring transactions from deletion so
        # the recurring rule remains consistent.
        for row_position in selected_rows:

            transaction_id = int(
                dataframe.iloc[row_position]["ID"]
            )

            recurring_transaction_id = (
                dataframe.iloc[row_position]["Recurring Rule ID"]
            )

            selected_ids.append(transaction_id)

            if pd.isna(recurring_transaction_id):

                deletable_ids.append(transaction_id)

            else:

                recurring_transaction_ids.append(transaction_id)

        delete_clicked = st.button(
            "Delete Selected Transactions"
        )

        if delete_clicked:

            if not selected_ids:

                st.error(
                    "No transaction(s) selected for deletion"
                )

            else:

                for transaction_id in deletable_ids:

                    delete_transaction(transaction_id)

                if recurring_transaction_ids:

                    st.info(
                        "Recurring transactions were not deleted."
                    )

                st.rerun()

        # Edit entries.
        if len(selected_ids) == 1:

            edit_clicked = st.button(
                "Edit Selected Transaction"
            )

            if edit_clicked:

                st.session_state["editing"] = True
                st.session_state["edit_id"] = selected_ids[0]

        if st.session_state["editing"]:

            if st.session_state["edit_id"] not in selected_ids:

                st.session_state["editing"] = False

            else:

                edit_transaction = dataframe[
                    dataframe["ID"]
                    == st.session_state["edit_id"]
                ].iloc[0]

                # Protect older transactions from having their split
                # erroneously modified if household size changes.
                if pd.isna(
                    edit_transaction["Shared Members"]
                ):

                    current_shared_members = household_size

                else:

                    current_shared_members = int(
                        edit_transaction["Shared Members"]
                    )

                edit_shared_members_max = max(
                    household_size,
                    current_shared_members
                )

                edit_shared = (
                    edit_transaction["Shared"] == "Yes"
                )

                edit_shared_members = None

                if household_size > 1 or edit_shared:

                    edit_shared = st.checkbox(
                        "Shared Expense",
                        value=(
                            edit_transaction["Shared"] == "Yes"
                        )
                    )

                    if edit_shared:

                        edit_shared_members = st.number_input(
                            "How many people split this transaction? "
                            "(including you)",
                            min_value=2,
                            max_value=edit_shared_members_max,
                            value=current_shared_members,
                            step=1
                        )

                with st.form("edit_transaction_form"):

                    type_options = [
                        "Expense",
                        "Income",
                        "Reimbursement"
                    ]

                    current_type_index = type_options.index(
                        edit_transaction["Type"]
                    )

                    current_category_index = categories.index(
                        edit_transaction["Category"]
                    )

                    edit_date = st.date_input(
                        "Date:",
                        value=edit_transaction["Date"]
                    )

                    edit_description = st.text_input(
                        "Description:",
                        value=edit_transaction["Description"]
                    )

                    edit_amount = st.number_input(
                        "Amount ($):",
                        value=float(
                            edit_transaction["Amount ($)"]
                        )
                    )

                    edit_type = st.radio(
                        "Transaction Type:",
                        type_options,
                        index=current_type_index,
                        horizontal=True
                    )

                    edit_category = st.selectbox(
                        "Transaction Category:",
                        categories,
                        index=current_category_index
                    )

                    edit_notes = st.text_area(
                        "Notes:",
                        value=edit_transaction["Notes"]
                    )

                    save_changes = st.form_submit_button(
                        "Save Changes"
                    )

                if save_changes:

                    if not edit_description.strip():

                        st.error(
                            "You must enter a description "
                            "for this transaction."
                        )

                    elif edit_amount <= 0:

                        st.error(
                            "Transaction amount must be "
                            "at least $0.01"
                        )

                    else:

                        update_transaction(
                            st.session_state["edit_id"],
                            edit_date.isoformat(),
                            edit_description.strip(),
                            edit_amount,
                            edit_type,
                            edit_category,
                            int(edit_shared),
                            edit_shared_members,
                            edit_notes
                        )

                        st.session_state["editing"] = False

                        st.rerun()