def analyze_cashflow(daily_balances):
    if (daily_balances["End Balance"] < 0).any():
        negative_days = daily_balances[daily_balances["End Balance"] < 0]

        first_negative_day = negative_days.iloc[0]
        first_negative_date = first_negative_day["Date"]

        lowest_balance = daily_balances["End Balance"].min()

        minimum_cash_needed = abs(lowest_balance)

        recovery_days = daily_balances[(daily_balances["Date"] > first_negative_date) 
                                       & 
                                       (daily_balances["End Balance"] >= 0)]

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