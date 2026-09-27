# FlowAhead

A forward-looking personal cash-flow budgeting application built with Python, Streamlit, pandas, and SQLite.

FlowAhead is designed around **cash-flow forecasting and overdraft prevention** rather than detailed purchase tracking. It helps users understand how scheduled income and expenses will affect their available balance throughout the month, identify potential cash shortfalls before they occur, and compare planned category budgets against actual spending.

The project began as a replacement for a spreadsheet-based household budgeting system and is being developed into a more flexible personal budgeting application.

## Current Features

### Transaction Management

* Add, edit, and delete transactions
* Transaction types:

  * Expense
  * Income
  * Reimbursement
* Categorize transactions
* Add optional notes
* Mark expenses as shared
* Track the number of household members splitting a shared expense
* Protect generated recurring transactions from accidental deletion

### Recurring Transactions

* Create recurring expenses, income, and reimbursements
* Support weekly, biweekly, and monthly schedules
* Automatically generate recurring transactions when viewing a month
* Prevent duplicate recurring transaction generation
* Activate and deactivate recurring rules
* Edit individual generated transactions without modifying the recurring rule
* Adjust generated transaction dates while preserving their scheduled occurrence
* Delete recurring rules and their associated generated transactions
* Handle monthly recurrence dates that do not exist in shorter months

### Monthly Cash-Flow Planning

* Set a starting balance for each month
* View transactions by month and year
* Calculate:

  * Total income
  * Total expenses
  * Total reimbursements
  * Net cash flow
  * Projected end-of-month balance
  * Lowest projected balance
  * Date of lowest projected balance

### Cash-Flow Forecasting

* Calculate daily starting and ending balances
* Carry balances forward through days without transactions
* Detect projected negative account balances
* Identify the first projected shortfall date
* Calculate the minimum additional cash required to avoid a projected shortfall
* Identify when the account is projected to recover
* Display transactions and projected balances in a monthly calendar
* Color-code expenses and positive cash flow
* Highlight projected negative balances

### Shared Expenses

* Configure household size
* Mark expenses as shared
* Specify how many people split an individual expense
* Calculate the user's share of a shared expense
* Calculate the amount owed by other household members
* Calculate expected reimbursement
* Track reimbursements separately from income
* Preserve compatibility with transactions created before per-transaction split information was introduced

### Category Budgets

* Set monthly budgets for individual expense categories
* Store category budgets independently for each month and year
* Update existing category budgets
* Compare budgeted amounts against actual spending
* Calculate remaining budget by category
* Calculate percentage of each category budget used
* Identify how many categories are over budget
* Calculate total budget, total actual spending, and overall remaining budget

### Spending Analysis

* Aggregate expense spending by category
* Compare category spending with the previous month
* Calculate dollar changes in spending
* Calculate percentage changes in spending
* Handle categories that appear in only one of the compared months
* Handle months with no previous spending without division-by-zero errors
* Correctly compare January against December of the previous year

## Technology

* Python
* Streamlit
* pandas
* SQLite

## Project Structure

```text
budget-app/
├── app.py           # Streamlit application and user interface
├── database.py      # SQLite schema, settings, balances, and category budgets
├── transactions.py  # Transaction CRUD operations
├── recurring.py     # Recurring transaction rules and generation
├── cashflow.py      # Cash-flow shortfall analysis
├── reporting.py     # Category budgets and spending analysis
├── .gitignore
└── README.md
```

The local SQLite database is intentionally excluded from version control because it may contain personal financial data.

## Development Status

The project is currently in active development.

Current version: **v0.7**

### v0.7 — Category Budgets & Reporting

v0.7 adds category-level budgeting and spending analysis to FlowAhead. Users can establish monthly category budgets, compare those budgets against actual expenses, view overall budget utilization, and identify categories that have exceeded their planned spending.

The reporting layer also adds month-over-month category spending comparisons, including dollar and percentage changes.

The v0.7 reporting and existing application functionality were regression-tested across transaction management, category budgets, recurring transactions, shared expenses, cash-flow analysis, month boundaries, empty-data conditions, and other edge cases before completion.

### v0.6 — Household & Shared Expense Improvements

v0.6 expanded shared-expense support beyond a fixed two-person split. Household size can be configured, and individual shared expenses can specify how many household members participated in the transaction. Expected reimbursements are calculated from the user's proportional share while maintaining compatibility with legacy shared transactions.

### v0.5 — Recurring Transactions

v0.5 introduced recurring transaction rules with weekly, biweekly, and monthly schedules. Recurring transactions are generated automatically as months are viewed while preventing duplicate occurrences. Rules can be activated, deactivated, or deleted, and individual generated transactions can be edited independently.

## Roadmap

### v0.8 — UI Overhaul & Refactor

Planned work includes:

* Redesign the Streamlit interface around the application's major workflows
* Improve dashboard organization and navigation
* Improve category-budget presentation
* Add category spending visualizations
* Add clearer over-budget and budget-utilization indicators
* Improve month-over-month reporting presentation
* Use actual month names in comparison reporting
* Refactor `app.py` into smaller modules where appropriate
* Reduce UI logic mixed directly with application logic
* Preserve existing functionality while improving maintainability

### Future Ideas

* Additional reporting and historical analysis
* Annual and additional recurring frequencies
* Data import/export
* More configurable categories
* Additional household/shared-expense options
* Optional financial-account integrations
* Deployment as a hosted application

## Privacy

Financial data is stored locally in SQLite. The database file is excluded from the repository and should not be committed to version control.

Do not commit personal financial databases, API credentials, or Streamlit secrets.