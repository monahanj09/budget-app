import streamlit as st

from database import get_setting, set_setting

def render_household_settings():
    """Render household settings and return the current household size."""
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

    return household_size