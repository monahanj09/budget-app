from datetime import date
from dateutil.relativedelta import relativedelta

from database import (
    get_initial_balance,
    get_initial_balance_month
)
from transactions import get_transactions
from recurring import generate_recurring_transactions


def analyze_cashflow(daily_balances):

    ## Any negative EOD balance constitutes a shortfall

    if (daily_balances["End Balance"] < 0).any():

        negative_days = daily_balances[
            daily_balances["End Balance"] < 0
        ]

        ## Calculate date when shortfall occurs

        first_negative_day = negative_days.iloc[0]
        first_negative_date = first_negative_day["Date"]

        lowest_balance = daily_balances["End Balance"].min()

        minimum_cash_needed = abs(lowest_balance)

        ## Recovery refers to date on which initial shortfall will
        ## naturally correct itself by account balance returning
        ## to 0 or higher.

        recovery_days = daily_balances[
            (daily_balances["Date"] > first_negative_date)
            &
            (daily_balances["End Balance"] >= 0)
        ]

        if not recovery_days.empty:

            recovery_day = recovery_days.iloc[0]
            recovery_date = recovery_day["Date"]

        else:

            recovery_date = None

        return {
            "has_shortfall": True,
            "first_negative_date": first_negative_date,
            "lowest_balance": lowest_balance,
            "minimum_cash_needed": minimum_cash_needed,
            "recovery_date": recovery_date
        }

    else:

        return {
            "has_shortfall": False,
            "first_negative_date": None,
            "lowest_balance": daily_balances["End Balance"].min(),
            "minimum_cash_needed": 0.0,
            "recovery_date": None
        }


def calculate_month_starting_balance(year, month):
    """Calculate a month's starting balance from the initial balance."""

    initial_balance = get_initial_balance()
    initial_balance_month = get_initial_balance_month()

    if initial_balance is None or initial_balance_month is None:

        return None

    initial_year, initial_month = initial_balance_month

    anchor_date = date(
        initial_year,
        initial_month,
        1
    )

    selected_date = date(
        year,
        month,
        1
    )

    if selected_date < anchor_date:

        return None

    running_balance = initial_balance
    current_date = anchor_date

    while current_date < selected_date:

        # Ensure recurring transactions exist before calculating
        # this month's contribution to the rolling balance.
        generate_recurring_transactions(
            current_date.year,
            current_date.month
        )

        transactions = get_transactions(
            current_date.year,
            current_date.month
        )

        for transaction in transactions:

            amount = float(transaction[3])
            transaction_type = transaction[4]

            if transaction_type == "Expense":

                running_balance -= amount

            elif transaction_type in (
                "Income",
                "Reimbursement"
            ):

                running_balance += amount

        current_date += relativedelta(months=1)

    return running_balance