# FlowAhead

A forward-looking personal cash-flow budgeting application built with Python and Streamlit.

FlowAhead is designed around forward-looking cash-flow planning rather than traditional expense tracking. It helps users see how scheduled income and expenses will affect their available balance throughout the month.

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

### Recurring Transactions
- Create recurring expenses, income, and reimbursements
- Support weekly, biweekly, and monthly schedules
- Automatically generate recurring transactions when viewing a month
- Prevent duplicate recurring transaction generation
- Activate and deactivate recurring rules
- Edit individual generated transactions without modifying the recurring rule
- Adjust generated transaction dates while preserving their scheduled occurrence
- Delete recurring rules and their associated generated transactions

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
- Detect projected cash shortfalls
- Identify the first projected negative-balance date
- Calculate the minimum additional cash needed to avoid a shortfall
- Identify when the account is projected to recover to a non-negative balance
- Warn when the account does not recover before the end of the selected month

### Shared Expenses
- Configure household size
- Mark expenses as shared
- Specify how many household members share each expense
- Calculate the user's share of each shared expense
- Calculate expected reimbursements from other household members
- Support different split sizes across individual transactions
- Preserve historical split information when household size changes
- Detect legacy shared transactions with missing split information
- Track reimbursements separately from income

## Technology

- Python
- Streamlit
- pandas
- SQLite

## Project Structure

```text
budget-app/
├── app.py          # Streamlit application and UI
├── database.py     # Database setup, settings, and monthly balances
├── transactions.py # Transaction CRUD operations
├── recurring.py    # Recurring transaction rules and generation
├── cashflow.py     # Cash-flow shortfall analysis
├── .gitignore
└── README.md

The local SQLite database is intentionally excluded from version control because it may contain personal financial data.

## Roadmap

### v0.7 — Budgets, Reporting & Analysis
- Category budgets
- Budget-versus-actual reporting
- Spending analysis
- Improved financial summaries and visualizations
- Historical/month-over-month analysis

### v0.8 — UI Overhaul & Refactor
- Redesign and polish the Streamlit interface
- Improve navigation and information hierarchy
- Refactor application structure as needed
- Improve maintainability and separation of concerns
- Prepare the application for the v1.0 release

### v1.0 — Initial Stable Release
- Complete core budgeting workflow
- Final testing and documentation
- Deployment as a hosted application

### Post-v1.0
- Explore redevelopment as a dedicated mobile application
- Data import/export
- Optional financial-account integrations

## Development Status

The project is currently in active development.

Current version: **v0.6**

### v0.6 — Cash-Flow Intelligence

v0.6 expands FlowAhead's forecasting capabilities and household budgeting support. The application can detect projected cash shortfalls, identify the first negative-balance date, calculate the minimum additional cash required, and determine whether and when the account is projected to recover.

Household expense handling was also expanded beyond fixed 50/50 splits. Users can configure household size and specify the number of people sharing individual and recurring expenses. FlowAhead calculates expected reimbursements based on each transaction's actual split while preserving historical split information when household settings change.

## Privacy

Financial data is stored locally in SQLite and the database file is excluded from this repository.

Do not commit personal financial databases, API credentials, or Streamlit secrets to version control.