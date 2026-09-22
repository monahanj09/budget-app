import streamlit as st
import pandas as pd
import calendar
from datetime import date

from database import (
    create_tables,
    add_transaction,
    get_transactions,
    delete_transaction,
    update_transaction,
    set_starting_balance,
    get_starting_balance,
    add_recurring_transaction,
    get_recurring_transactions,
    delete_recurring_transaction,
    set_recurring_transaction_active
)


# Create database tables when the app starts
create_tables()


st.set_page_config(
    page_title="Budget App",
    page_icon="💰",
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

st.header("Add Transaction")

## Create the add transaction form(s) and store all input in requisite variables

with st.form("transaction_form"):
    transaction_date = st.date_input("Date:", value=date.today(), format="MM/DD/YYYY")

    transaction_type = st.radio("Transaction Type:", ["Expense", "Income", "Reimbursement"], horizontal = True)

    transaction_description = st.text_input("Description:", "")

    transaction_amount = st.number_input("Amount:", min_value=0.00, step=1.0, format="%.2f")

    transaction_category = st.selectbox("Category:", categories)

    transaction_shared = st.checkbox("Shared Expense")

    transaction_notes = st.text_area("Notes:")

    submitted = st.form_submit_button("Add Transaction")

st.header("Add Recurring Transaction")

with st.form("recurring_transaction_form"):
    recur_name = st.text_input("Name of recurring transaction:", "")

    recur_amount = st.number_input("Recurring Amount:", min_value=0.00, step=1.0, format="%.2f")

    recur_type = st.radio("Recurring Type:", ["Expense", "Income", "Reimbursement"], horizontal = True)

    recur_category = st.selectbox("Category:", categories)

    recur_shared = st.checkbox("Shared Recurring Expense")

    recur_notes = st.text_area("Notes:")

    recur_start_date = st.date_input("Start Date:", value=date.today(), format="MM/DD/YYYY")

    recur_frequency = st.radio("Frequency of Recurrence:", ["Weekly", "Biweekly", "Monthly"], index=2, horizontal=True)

    recur_submitted = st.form_submit_button("Add Recurring Transaction")

if submitted:

    ## Error checking for input data
    if not transaction_description.strip():
        st.error("You must enter a description for the transaction.")

    elif transaction_amount <= 0:
        st.error("Transaction amount must be at least $0.01")

    else:
        add_transaction(date=transaction_date.isoformat(), 
                        name=transaction_description.strip(), 
                        amount=transaction_amount, 
                        transaction_type=transaction_type, 
                        category=transaction_category, 
                        shared=int(transaction_shared), 
                        notes=transaction_notes)
        st.success("Transaction submitted successfully.")

if recur_submitted:

    if not recur_name.strip():
        st.error("You must enter a name for a recurring transaction.")
    elif recur_amount <= 0:
        st.error("Recurring transaction amount must be at least $0.01")
    else:
        add_recurring_transaction(name=recur_name.strip(),
                                  expected_amount=recur_amount,
                                  type=recur_type,
                                  category=recur_category,
                                  shared=int(recur_shared),
                                  notes=recur_notes,
                                  start_date=recur_start_date.isoformat(),
                                  frequency=recur_frequency)
        st.success("Recurring transaction created successfully.")

st.header("Recurring Transactions")

recurring_transactions = get_recurring_transactions()

if recurring_transactions:
    recurring_dataframe = pd.DataFrame(
        recurring_transactions,
        columns=["ID", "Name", "Expected Amount", "Type", "Category", "Shared", "Notes", "Start Date", "Frequency", "Active"]
    )

    recurring_dataframe["Start Date"] = pd.to_datetime(
        recurring_dataframe["Start Date"]
    )

    recurring_dataframe["Shared"] = recurring_dataframe["Shared"].map({
                        0: "No",
                        1: "Yes"})
    recurring_dataframe["Active"] = recurring_dataframe["Active"].map({
                        0: "No",
                        1: "Yes"})
    
    recurring_table = st.dataframe(recurring_dataframe, hide_index=True, on_select="rerun", selection_mode="multi-row", column_config={
        "Expected Amount": st.column_config.NumberColumn(
        "Expected Amount",
        format="$%.2f"
        ),
        "Start Date": st.column_config.DateColumn(
            "Start Date",
            format="MM/DD/YYYY"
        ),
        "ID": None
    })

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

transactions = get_transactions(selected_year, selected_month)

last_day = calendar.monthrange(selected_year, selected_month)[1]
month_start = date(selected_year, selected_month, 1)
month_end = date(selected_year, selected_month, last_day)
all_dates = pd.date_range(start=month_start, end=month_end)

daily_balances = pd.DataFrame({"Date": all_dates})

if transactions:

    ## Calculate and display monthly totals/transactions

    dataframe = pd.DataFrame(
        transactions,
        columns=["ID", "Date", "Description", "Amount ($)", "Type", "Category", "Shared", "Notes"]
    )

    dataframe["Cash Flow"] = dataframe.apply(
        lambda row: -row["Amount ($)"] if row["Type"] == "Expense" else row["Amount ($)"],
        axis=1
    )

    dataframe = dataframe.sort_values(
        by=["Date", "ID"]
    ).reset_index(drop=True)

    dataframe["Date"] = pd.to_datetime(dataframe["Date"])

    daily_transaction_totals = (dataframe.groupby("Date")["Cash Flow"].sum().reset_index())

    daily_balances = daily_balances.merge(daily_transaction_totals, on="Date", how="left")
    daily_balances["Cash Flow"] = daily_balances["Cash Flow"].fillna(0)

else:

    daily_balances["Cash Flow"] = 0.0

daily_balances["End Balance"] = starting_balance + daily_balances["Cash Flow"].cumsum()

daily_balances["Start Balance"] = daily_balances["End Balance"].shift(1).fillna(starting_balance)

daily_display = daily_balances[["Date", "Start Balance", "End Balance"]].copy()

daily_display["Date"] = daily_display["Date"].dt.strftime("%m/%d/%Y")

st.dataframe(daily_display, hide_index=True, column_config={
    "Date": st.column_config.DateColumn(
        "Date",
        format="MM/DD/YYYY"
    ),
    "Start Balance": st.column_config.NumberColumn(
        "Start Balance",
        format="$%.2f"
    ),
    "End Balance": st.column_config.NumberColumn(
        "End Balance",
        format="$%.2f"
    )
})

if transactions:

    dataframe["Shared"] = dataframe["Shared"].map({
                        0: "No",
                        1: "Yes"})

    income = dataframe[dataframe["Type"] == "Income"] ["Amount ($)"].sum()
    expenses = dataframe[dataframe["Type"] == "Expense"] ["Amount ($)"].sum()
    reimbursements = dataframe[dataframe["Type"] == "Reimbursement"]["Amount ($)"].sum()

    shared_expense_dataframe = dataframe[
        (dataframe["Type"] == "Expense") &
        (dataframe["Shared"] == "Yes")
    ]

    shared_expenses = shared_expense_dataframe["Amount ($)"].sum()

else:

    income = 0.0
    expenses = 0.0
    reimbursements = 0.0
    shared_expenses = 0.0

net_cash_flow = income + reimbursements - expenses


## Establish lowest balance

projected_end_balance = daily_balances["End Balance"].iloc[-1]
lowest_balance = daily_balances["End Balance"].min()
lowest_balance_index = daily_balances["End Balance"].idxmin()
lowest_balance_date = daily_balances.loc[lowest_balance_index, "Date"]

## Formatting for negative numbers

if net_cash_flow < 0:
    formatted_net_cash_flow = f"-${abs(net_cash_flow):,.2f}"
else:
    formatted_net_cash_flow = f"${net_cash_flow:,.2f}"

## Summary reporting

column1, column2, column3, column4 = st.columns(4)
column5, column6, column7 = st.columns(3)
column8, column9 = st.columns(2)

column1.metric("Income:", f"${income:,.2f}")
column2.metric("Reimbursements:", f"${reimbursements:,.2f}")
column3.metric("Expenses:", f"${expenses:,.2f}")
column4.metric("Net Cash Flow:", formatted_net_cash_flow)
column5.metric("Projected End Balance:", f"${projected_end_balance:,.2f}")
column6.metric("Lowest Balance:", f"${lowest_balance:,.2f}")
column7.metric("Lowest Balance Date:", lowest_balance_date.strftime("%m/%d/%Y"))
column8.metric("Shared Expenses:", f"${shared_expenses:,.2f}")
column9.metric("50% of Shared Expenses:", f"${shared_expenses/2:,.2f}")

## Build and pass data to calendar for easier visual tracking

st.header("Cash Flow Calendar")

weekday_columns = st.columns(7)

weekdays = [
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday"
]

for column, weekday in zip(weekday_columns, weekdays):
    column.markdown(f"**{weekday}**")

month_calendar = calendar.Calendar(firstweekday=6)

calendar_weeks = month_calendar.monthdayscalendar(
    selected_year,
    selected_month
)

for week in calendar_weeks:

    week_columns = st.columns(7)

    for column, day in zip(week_columns, week):

        if day != 0:
            calendar_date = pd.Timestamp(
            year=selected_year,
            month=selected_month,
            day=day
        )

            day_balance = daily_balances.loc[
            daily_balances["Date"] == calendar_date,
            "End Balance"
            ].iloc[0]

            with column.container(border=True, height=250):

                st.markdown(f"**{day}**")


                if transactions:

                    day_transactions = dataframe[dataframe["Date"] == calendar_date]

                    for _, transaction in day_transactions.iterrows():

                        if transaction["Type"] == "Expense":
                            transaction_amount = transaction["Amount ($)"]
                            formatted_amount = f"-${transaction_amount:,.2f}"
                            transaction_color = "red"
                        else: 
                            transaction_amount = transaction["Amount ($)"]
                            formatted_amount = f"+${transaction_amount:,.2f}"
                            transaction_color = "green"

                        st.markdown(
                            f'<span style="color: {transaction_color};">{transaction["Description"]}: {formatted_amount}</span>',
                            unsafe_allow_html=True
                            )

                if day_balance < 0:
                    st.markdown(
                        f'<span style="color: red; font-weight: bold;">Balance: -${abs(day_balance):,.2f}</span>',
                        unsafe_allow_html=True)
                else:
                    st.markdown(f"**Balance: ${day_balance:,.2f}**")

if transactions:

    ## Table formatting for lower table

    table_event = st.dataframe(dataframe, hide_index=True, on_select="rerun",selection_mode="multi-row",column_config={
        "Date": st.column_config.DatetimeColumn(
            "Date",
            format="MM/DD/YYYY"
        ),
        "Amount ($)": st.column_config.NumberColumn(
            "Amount ($)",
            format="$%.2f"
        ),
        "Cash Flow": None,
        "ID": None
        
    })

    selected_rows = table_event.selection.rows

    selected_ids = []

    ## Delete unnecessary entries

    for row_position in selected_rows:
        transaction_id = int(dataframe.iloc[row_position]["ID"])
        selected_ids.append(transaction_id)

    delete_clicked = st.button("Delete Selected Transactions")

    if delete_clicked:

        if selected_ids == []:
            st.error("No transaction(s) selected for deletion")
        else:
            for transaction_id in selected_ids:
                delete_transaction(transaction_id)
            st.rerun()

    ## Edit entries

    if len(selected_ids) == 1:

        edit_clicked = st.button("Edit Selected Transaction")

        if edit_clicked:

            st.session_state["editing"] = True
            st.session_state["edit_id"] = selected_ids[0]

    if st.session_state["editing"]:

        if st.session_state["edit_id"] not in selected_ids:
            st.session_state["editing"] = False

        else:

            edit_transaction = dataframe[dataframe["ID"] == st.session_state["edit_id"]].iloc[0]

            with st.form("edit_transaction_form"):

                type_options = ["Expense", "Income", "Reimbursement"]
                current_type_index = type_options.index(edit_transaction["Type"])

                current_category_index = categories.index(edit_transaction["Category"])

                edit_date = st.date_input("Date:", value=edit_transaction["Date"])
                edit_description = st.text_input("Description:", value=edit_transaction["Description"])
                edit_amount = st.number_input("Amount ($):", value=float(edit_transaction["Amount ($)"]))
                edit_type = st.radio("Transaction Type:", type_options, index=current_type_index, horizontal=True)
                edit_category = st.selectbox("Transaction Category:", categories, index=current_category_index)
                edit_shared = st.checkbox("Shared Expense", value=edit_transaction["Shared"] == "Yes")
                edit_notes = st.text_area("Notes:", value=edit_transaction["Notes"])

                save_changes = st.form_submit_button("Save Changes")

            if save_changes:

                ## Proper input checking

                if not edit_description.strip():

                    st.error("You must enter a description for this transaction.")

                elif edit_amount <= 0:

                    st.error("Transaction amount must be at least $0.01")

                else:

                    update_transaction(st.session_state["edit_id"],
                                   edit_date.isoformat(),
                                   edit_description.strip(),
                                   edit_amount,
                                   edit_type,
                                   edit_category,
                                   int(edit_shared),
                                   edit_notes)
                    st.session_state["editing"] = False
                    st.rerun()