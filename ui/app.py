# import streamlit as st
# import requests

# st.title("AI Smart Expense Assistant")

# api_url = "http://127.0.0.1:8000/"

# response = requests.get(api_url)

# st.write("Backend Response:", response.json())

# ui/app.py

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from ui.app_pages import add_expense, view_expenses, forecast


PAGES = {
    "Add Expense": add_expense,
    "View Expenses": view_expenses,
    "Forecast": forecast,
}

st.set_page_config(page_title="AI Expense Assistant", layout="centered")

st.title("AI Expense Assistant")

page = st.sidebar.radio("Pages", list(PAGES.keys()))
PAGES[page].app()

