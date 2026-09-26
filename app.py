import streamlit as st
import pandas as pd
import calendar
from datetime import date

from database import (
    create_tables,
    set_starting_balance,
    get_starting_balance,
    get_setting,
    set_setting,
    set_category_budget,
    get_category_budgets
)

from transactions import(
    add_transaction,
    get_transactions,
    delete_transaction,
    update_transaction,
)

from recurring import(
    add_recurring_transaction,
    get_recurring_transactions,
    delete_recurring_transaction,
    set_recurring_transaction_active,
    generate_recurring_transactions
)

from cashflow import(
    analyze_cashflow
)

from reporting import(
    calculate_category_spending,
    calculate_budget_vs_actual,
    calculate_budget_summary
)

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

household_size_setting = get_setting("household_size")

if household_size_setting is None:

    st.header("Household Setup")

    household_size = st.number_input("Input your household size (include people who share household expenses)", 
                                     min_value=1, 
                                     step=1, 
                                     value=1)

    if st.button("Save Household Size"):

        set_setting("household_size", household_size)
        st.rerun()

else: 

    household_size=int(household_size_setting)    

    st.sidebar.header("Settings")

    update_household_size = st.sidebar.number_input(
        "Household Size",
        min_value=1,
        step=1,
        value=household_size
    )

    if st.sidebar.button("Save Settings"):
        set_setting("household_size", update_household_size)
        st.rerun()

st.header("Add Transaction")

## Create the add transaction form(s) and store all input in requisite variables
## Shared transaction checkbox outside normal form due to lack of dynamic form changes based on checkbox states

transaction_shared = False
transaction_shared_members = None

if household_size > 1:

    transaction_shared = st.checkbox("Shared Expense")

    if transaction_shared:

        transaction_shared_members = st.number_input("How many people split this transaction? (including you)", 
                        min_value=2, 
                        max_value=household_size, 
                        value=household_size,
                        step=1)

with st.form("transaction_form"):
    transaction_date = st.date_input("Date:", value=date.today(), format="MM/DD/YYYY")

    transaction_type = st.radio("Transaction Type:", ["Expense", "Income", "Reimbursement"], horizontal = True)

    transaction_description = st.text_input("Description:", "")

    transaction_amount = st.number_input("Amount:", min_value=0.00, step=1.0, format="%.2f")

    transaction_category = st.selectbox("Category:", categories)

    transaction_notes = st.text_area("Notes:")

    submitted = st.form_submit_button("Add Transaction")

## Shared transaction checkbox outside normal form due to lack of dynamic form changes based on checkbox states

st.header("Add Recurring Transaction")

recur_shared = False
recur_shared_members = None

if household_size > 1:

    recur_shared = st.checkbox("Shared Recurring Expense")

    if recur_shared:

        recur_shared_members = st.number_input("How many people split this transaction? (including you)", 
            min_value=2, 
            max_value=household_size, 
            value=household_size,
            step=1)

with st.form("recurring_transaction_form"):
    recur_name = st.text_input("Name of recurring transaction:", "")

    recur_amount = st.number_input("Recurring Amount:", min_value=0.00, step=1.0, format="%.2f")

    recur_type = st.radio("Recurring Type:", ["Expense", "Income", "Reimbursement"], horizontal = True)

    recur_category = st.selectbox("Category:", categories)

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
                        notes=transaction_notes,
                        shared_members = transaction_shared_members)
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
                                  shared_members=recur_shared_members,
                                  notes=recur_notes,
                                  start_date=recur_start_date.isoformat(),
                                  frequency=recur_frequency)
        st.success("Recurring transaction created successfully.")

## Recurring rule dataframe for displaying/managing recurring rules, rather than monthly generated transactions

st.header("Recurring Transactions")

recurring_transactions = get_recurring_transactions()

if recurring_transactions:
    recurring_dataframe = pd.DataFrame(
        recurring_transactions,
        columns=["ID", "Name", "Expected Amount", "Type", "Category", "Shared", "Shared Members", "Notes", "Start Date", "Frequency", "Active"]
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

## Category budget management

st.subheader("Category Budgets")

category_budgets = get_category_budgets(selected_year, selected_month)

budget_categories = [
    category for category in categories
    if category not in ["Paycheck", "Shared Contributions"]
]

selected_budget_category = st.selectbox("Budget Category:", budget_categories)

current_budget_amount = category_budgets.get(selected_budget_category, 0.0)

entered_budget_amount = st.number_input("Monthly Budget ($):",
                                        min_value=0.0,
                                        value=float(current_budget_amount),
                                        step=10.0,
                                        format="%.2f")

save_category_budget = st.button("Save Category Budget")

if save_category_budget:

    if entered_budget_amount <= 0:

        st.error("Category budget must be at least $0.01")

    else:

        set_category_budget(selected_year, selected_month, selected_budget_category, entered_budget_amount)

        st.rerun()

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

category_spending = calculate_category_spending(transactions)

budget_report = calculate_budget_vs_actual(category_budgets, category_spending)

budget_summary = calculate_budget_summary(budget_report)

if budget_report:

    budget_dataframe = pd.DataFrame.from_dict(
        budget_report,
        orient="index"
    )

    budget_dataframe = budget_dataframe.reset_index()

    budget_dataframe = budget_dataframe.rename(
        columns={
            "index": "Category",
            "budget": "Budget",
            "actual": "Actual",
            "remaining": "Remaining"
        }
    )

    budget_dataframe["% Used"] = (budget_dataframe["Actual"]/budget_dataframe["Budget"])*100

    st.subheader("Budget Overview")

    budget_column1, budget_column2, budget_column3, budget_column4 = st.columns(4)

    if budget_summary["remaining"] < 0:
        formatted_budget_remaining = f"-${abs(budget_summary['remaining']):,.2f}"
    else:
        formatted_budget_remaining = f"${budget_summary['remaining']:,.2f}"

    st.dataframe(
        budget_dataframe,
        hide_index=True,
        column_config={
            "Budget": st.column_config.NumberColumn(
                "Budget",
                format="$%.2f"
            ),
            "Actual": st.column_config.NumberColumn(
                "Actual",
                format="$%.2f"
            ),
            "Remaining": st.column_config.NumberColumn(
                "Remaining",
                format="$%.2f"
            ),
            "% Used": st.column_config.NumberColumn(
                "% Used",
                format="$%.1f%%"
            )
        }
    )

    budget_column1.metric(
    "Total Budget:",
    f"${budget_summary['total_budget']:,.2f}"
    )

    budget_column2.metric(
    "Budgeted Spending:",
    f"${budget_summary['total_actual']:,.2f}"
    )

    budget_column3.metric(
    "Budget Remaining:",
    formatted_budget_remaining
    )

    budget_column4.metric(
    "Categories Over Budget:",
    budget_summary["categories_over_budget"]
    )



else:

    st.info("No category budgets have been established for this month.")

last_day = calendar.monthrange(selected_year, selected_month)[1]
month_start = date(selected_year, selected_month, 1)
month_end = date(selected_year, selected_month, last_day)
all_dates = pd.date_range(start=month_start, end=month_end)

## Construct calendar, aggregate transaction cash flow by date, merge, and cum-sum from starting balance

daily_balances = pd.DataFrame({"Date": all_dates})

if transactions:

    ## Calculate and display monthly totals/transactions

    dataframe = pd.DataFrame(
        transactions,
        columns=["ID", "Date", "Description", "Amount ($)", "Type", "Category", "Shared", "Shared Members", "Notes", "Recurring Rule ID"]
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

cashflow_analysis = analyze_cashflow(daily_balances)

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

    ## Legacy datahandling for transactions before shared_members was created

    incomplete_shared_expenses = dataframe[
        (dataframe["Type"] == "Expense") & 
        (dataframe["Shared"] == "Yes") &
        (dataframe["Shared Members"].isna())
    ]

    incomplete_shared_count = len(incomplete_shared_expenses)

    if incomplete_shared_count > 0:

        if incomplete_shared_count == 1:
            transaction_word = "transaction"
        else:
            transaction_word = "transactions"

        st.warning(
            f"{incomplete_shared_count} shared {transaction_word} are missing split information. "
            f"Edit these {transaction_word} and specify how many people shared the expense. "
            f"They are excluded from Shared Expenses and Expected Reimbursement calculations until corrected."
        )

    shared_expense_dataframe = dataframe[
        (dataframe["Type"] == "Expense") &
        (dataframe["Shared"] == "Yes") &
        (dataframe["Shared Members"] > 1)
    ].copy()

    ## User share represents share of shared expenses belonging to user of app, Others share represents money owed to User

    shared_expense_dataframe["User Share"] = shared_expense_dataframe["Amount ($)"] / shared_expense_dataframe["Shared Members"]
    shared_expense_dataframe["Others Share"] = shared_expense_dataframe["Amount ($)"] - shared_expense_dataframe["User Share"]
    expected_reimbursement = shared_expense_dataframe["Others Share"].sum()

    shared_expenses = shared_expense_dataframe["Amount ($)"].sum()

else:

    income = 0.0
    expenses = 0.0
    reimbursements = 0.0
    shared_expenses = 0.0
    expected_reimbursement = 0.0

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

## Converts results from analyze_cashflow() into user-facing warning with different output depending on account recovery

if cashflow_analysis["has_shortfall"]:

    first_negative_date = cashflow_analysis["first_negative_date"]
    minimum_cash_needed = cashflow_analysis["minimum_cash_needed"]
    recovery_date = cashflow_analysis["recovery_date"]

    if recovery_date is not None:

        additional_warning = (f"Projected recovery date: "
                              f"{recovery_date.strftime('%m/%d/%Y')}."
        )

    else:

        additional_warning = "Projected recovery date: Account does not recover before end of selected month"

    warning_message = (
    f"Projected cash shortfall detected.\n\n "
    f"First negative balance: {first_negative_date.strftime('%m/%d/%Y')}.\n\n "
    f"Minimum additional cash needed: ${minimum_cash_needed:,.2f}.\n\n "
    )
    warning_message += additional_warning

    st.warning(warning_message)

column1.metric("Income:", f"${income:,.2f}")
column2.metric("Reimbursements:", f"${reimbursements:,.2f}")
column3.metric("Expenses:", f"${expenses:,.2f}")
column4.metric("Net Cash Flow:", formatted_net_cash_flow)
column5.metric("Projected End Balance:", f"${projected_end_balance:,.2f}")
column6.metric("Lowest Balance:", f"${lowest_balance:,.2f}")
column7.metric("Lowest Balance Date:", lowest_balance_date.strftime("%m/%d/%Y"))
column8.metric("Shared Expenses:", f"${shared_expenses:,.2f}")
column9.metric("Expected Reimbursement:", f"${expected_reimbursement:,.2f}")

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
        "ID": None,
        "Recurring Rule ID": None
        
    })

    selected_rows = table_event.selection.rows

    selected_ids = []
    deletable_ids = []
    recurring_transaction_ids = []

    ## Delete unnecessary entries, protect generated recurring transactions from deletion so the recurring-rule remains consistent

    for row_position in selected_rows:
        transaction_id = int(dataframe.iloc[row_position]["ID"])
        recurring_transaction_id = dataframe.iloc[row_position]["Recurring Rule ID"]

        selected_ids.append(transaction_id)

        if pd.isna(recurring_transaction_id):
            deletable_ids.append(transaction_id)
        else:
            recurring_transaction_ids.append(transaction_id)

    delete_clicked = st.button("Delete Selected Transactions")

    if delete_clicked:

        if not selected_ids and not recurring_transaction_ids:
            st.error("No transaction(s) selected for deletion")
        else:
            for transaction_id in deletable_ids:
                delete_transaction(transaction_id)
            if recurring_transaction_ids:
                st.info("Recurring transactions were not deleted.")
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

            ## Protect old transactions from having their split erroneously modified if household size changes

            if pd.isna(edit_transaction["Shared Members"]):
                current_shared_members = household_size
            else:
                current_shared_members = int(edit_transaction["Shared Members"])

            edit_shared_members_max = max(household_size, current_shared_members)

            edit_shared = edit_transaction["Shared"] == "Yes"
            edit_shared_members = None

            if household_size > 1 or edit_shared:

                edit_shared = st.checkbox("Shared Expense", value=edit_transaction["Shared"] == "Yes")

                if edit_shared:

                    edit_shared_members = st.number_input("How many people split this transaction? (including you)", 
                        min_value=2, 
                        max_value=edit_shared_members_max, 
                        value=current_shared_members,
                        step=1)

            with st.form("edit_transaction_form"):

                type_options = ["Expense", "Income", "Reimbursement"]
                current_type_index = type_options.index(edit_transaction["Type"])

                current_category_index = categories.index(edit_transaction["Category"])
                edit_date = st.date_input("Date:", value=edit_transaction["Date"])
                edit_description = st.text_input("Description:", value=edit_transaction["Description"])
                edit_amount = st.number_input("Amount ($):", value=float(edit_transaction["Amount ($)"]))
                edit_type = st.radio("Transaction Type:", type_options, index=current_type_index, horizontal=True)
                edit_category = st.selectbox("Transaction Category:", categories, index=current_category_index)
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
                                   edit_shared_members,
                                   edit_notes)
                    st.session_state["editing"] = False
                    st.rerun()