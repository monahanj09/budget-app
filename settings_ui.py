import streamlit as st
import calendar
from datetime import date

from database import (
    get_setting,
    set_setting,
    get_initial_balance,
    get_initial_balance_month,
    set_initial_balance
)


def render_household_settings():
    """Render household settings and return the current household size."""

    household_size_setting = get_setting(
        "household_size"
    )

    # ---------------------------------------------------------
    # Household Settings
    # ---------------------------------------------------------

    if household_size_setting is None:

        st.subheader("Household Setup")

        household_column, _, _ = st.columns(3)

        with household_column:

            household_size = st.number_input(
                "Household Size",
                min_value=1,
                step=1,
                value=1,
                help=(
                    "Include everyone who shares "
                    "household expenses."
                )
            )

            if st.button("Save Household Size"):

                set_setting(
                    "household_size",
                    household_size
                )

                st.rerun()

    else:

        household_size = int(
            household_size_setting
        )

        st.subheader("Household")

        household_column, _, _ = st.columns(3)

        with household_column:

            update_household_size = st.number_input(
                "Household Size",
                min_value=1,
                step=1,
                value=household_size,
                help=(
                    "Include everyone who shares "
                    "household expenses."
                )
            )

            if st.button("Save Settings"):

                set_setting(
                    "household_size",
                    update_household_size
                )

                st.rerun()

    # ---------------------------------------------------------
    # Initial Balance
    # ---------------------------------------------------------

    st.divider()

    st.subheader("Initial Balance")

    st.caption(
        "Get the account balance FlowAhead should use as the "
        "starting point for rolling monthly balance calculations."
    )

    initial_balance = get_initial_balance()

    initial_balance_month = (
        get_initial_balance_month()
    )

    if initial_balance is None:

        initial_balance = 0.0

    if initial_balance_month is None:

        initial_year = date.today().year
        initial_month = date.today().month

    else:

        initial_year, initial_month = (
            initial_balance_month
        )

    balance_column, month_column, year_column = (
        st.columns(3)
    )

    with balance_column:

        updated_initial_balance = st.number_input(
            "Initial Balance ($)",
            value=float(initial_balance),
            step=1.00,
            format="%.2f"
        )

    with month_column:

        updated_initial_month = st.selectbox(
            "Initial Month",
            range(1, 13),
            format_func=lambda month: (
                calendar.month_name[month]
            ),
            index=initial_month - 1
        )

    with year_column:

        updated_initial_year = st.number_input(
            "Initial Year",
            min_value=2022,
            value=initial_year,
            step=1
        )

    if st.button("Save Initial Balance"):

        set_initial_balance(
            updated_initial_year,
            updated_initial_month,
            updated_initial_balance
        )

        st.success(
            "Initial balance saved."
        )

    return household_size