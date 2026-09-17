# Budget App

A personal cash-flow budgeting application built with Python and Streamlit.

Budget App is designed around forward-looking cash-flow planning rather than traditional expense tracking. It helps users see how scheduled income and expenses will affect their available balance throughout the month.

The project began as a replacement for a spreadsheet-based household budgeting system and is being developed into a more flexible budgeting application.

## Current Features

### Transaction Management
- Add, edit, and delete transactions
- Transaction types:
  - Expense
  - Income
  - Reimbursement
- Categorize transactions
- Add optional notes
- Mark expenses as shared

### Monthly Budgeting
- Set a starting balance for each month
- View transactions by month and year
- Calculate:
  - Total income
  - Total expenses
  - Total reimbursements
  - Net cash flow

### Cash-Flow Forecasting
- Calculate daily starting and ending balances
- Carry balances forward through days without transactions
- Project the end-of-month balance
- Identify the lowest projected balance and its date
- Display transactions and projected balances in a monthly calendar
- Color-code expenses and positive cash flow
- Highlight projected negative balances

### Shared Expenses
- Mark expenses as shared
- Calculate total shared expenses
- Calculate a 50% share of shared expenses
- Track reimbursements separately from income

## Technology

- Python
- Streamlit
- pandas
- SQLite

## Project Structure

```text
budget-app/
├── app.py          # Streamlit application and budgeting logic
├── database.py     # SQLite database operations
├── .gitignore
└── README.md
```

The local SQLite database is intentionally excluded from version control because it may contain personal financial data.

## Roadmap

### v0.5 — Recurring Transactions
- Recurring bills
- Recurring income/paychecks
- Automatic monthly transaction generation
- Support for fixed and variable recurring obligations

### Future Ideas
- Configurable shared-expense percentages
- Household/member configuration
- Improved reporting and visualization
- Budget categories and spending analysis
- Data import/export
- Optional financial-account integrations
- Deployment as a hosted application

## Development Status

The project is currently in active development.

Current version: **v0.4**

v0.4 introduced a monthly cash-flow calendar displaying scheduled transactions, projected daily balances, color-coded cash flow, and visual warnings for negative projected balances.

## Privacy

Financial data is stored locally in SQLite and the database file is excluded from this repository.

Do not commit personal financial databases, API credentials, or Streamlit secrets to version control.