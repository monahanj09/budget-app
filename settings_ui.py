import streamlit as st

from database import get_setting, set_setting


def render_household_settings():
    """Render household settings and return the current household size."""

    household_size_setting = get_setting("household_size")

    if household_size_setting is None:

        st.subheader("Household Setup")

        household_size = st.number_input(
            "Household Size",
            min_value=1,
            step=1,
            value=1,
            help="Include everyone who shares household expenses."
        )

        if st.button("Save Household Size"):

            set_setting("household_size", household_size)
            st.rerun()

    else:

        household_size = int(household_size_setting)

        st.subheader("Household")

        update_household_size = st.number_input(
            "Household Size",
            min_value=1,
            step=1,
            value=household_size,
            help="Include everyone who shares household expenses."
        )

        if st.button("Save Settings"):

            set_setting(
                "household_size",
                update_household_size
            )

            st.rerun()

    return household_size