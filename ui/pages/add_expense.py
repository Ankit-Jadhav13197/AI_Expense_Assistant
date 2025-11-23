# ui/pages/add_expense.py
import os
import streamlit as st
from datetime import date
import requests
from pydantic import BaseModel, ValidationError

API_BASE = st.secrets.get("api_base", "http://127.0.0.1:8000")  #ogg

# API_BASE = st.secrets["api_base"] if "api_base" in st.secrets else "http://127.0.0.1:8000"

# API_BASE = os.getenv("API_BASE", "http://127.0.0.1:8000")

def app():
    st.header("Add Expense")
    with st.form("add_expense_form"):
        d = st.date_input("Date", value=date.today())
        desc = st.text_input("Description")
        amount = st.number_input("Amount", min_value=0.01, format="%.2f")
        category = st.text_input("Category (optional)")
        submitted = st.form_submit_button("Add")
        if submitted:
            payload = {"date": d.isoformat(), "description": desc, "amount": amount, "category": category or None}
            try:
                r = requests.post(f"{API_BASE}/expenses/", json=payload, timeout=5)
                if r.status_code == 201:
                    st.success("Expense created.")
                else:
                    st.error(f"Failed: {r.status_code} {r.text}")
            except Exception as e:
                st.error(f"Request failed: {e}")
