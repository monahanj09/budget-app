import streamlit as st

from settings_ui import render_household_settings


st.title("Settings")
st.caption("Configure household settings")


render_household_settings()