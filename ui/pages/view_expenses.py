# ui/pages/view_expenses.py
import streamlit as st
import requests
import pandas as pd

API_BASE = st.secrets.get("api_base", "http://127.0.0.1:8000")

def app():
    st.header("View Expenses")
    try:
        r = requests.get(f"{API_BASE}/expenses/", timeout=5)
        if r.status_code == 200:
            data = r.json()
            if not data:
                st.info("No expenses yet. Add one from 'Add Expense' page.")
                return
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['date']).dt.date
            st.dataframe(df.sort_values("date", ascending=False))
            # quick totals
            st.markdown(f"**Total expenses fetched:** {len(df)}")
            st.markdown(f"**Sum of amounts:** {df['amount'].sum():.2f}")
        else:
            st.error(f"Failed to fetch expenses: {r.status_code} {r.text}")
    except Exception as e:
        st.error(f"Request failed: {e}")
