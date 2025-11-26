import streamlit as st
import requests
import pandas as pd
from datetime import date

API_BASE = st.secrets.get("api_base", "http://127.0.0.1:8000")

def app():
    st.header("View Expenses")

    # -----------------------------
    # Fetch expenses
    # -----------------------------
    try:
        r = requests.get(f"{API_BASE}/expenses/", timeout=5)
        if r.status_code != 200:
            st.error(f"Failed to fetch expenses: {r.status_code} {r.text}")
            return

        data = r.json()

    except Exception as e:
        st.error(f"Request failed: {e}")
        return

    if not data:
        st.info("No expenses yet. Add one from 'Add Expense' page.")
        return

    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"]).dt.date

    st.subheader("All Expenses")
    st.dataframe(df.sort_values("date", ascending=False))

    st.markdown(f"**Total expenses fetched:** {len(df)}")
    st.markdown(f"**Sum of amounts:** ₹ {df['amount'].sum():.2f}")

    st.write("---")
    st.subheader("Edit / Delete Expense")

    # -----------------------------
    # Select Expense
    # -----------------------------
    selected_id = st.selectbox(
        "Select an expense ID",
        df["id"].tolist(),
        format_func=lambda x: f"ID {x} | {df[df.id == x].iloc[0].description}",
    )

    selected_exp = df[df.id == selected_id].iloc[0]

    # -----------------------------
    # Edit Form
    # -----------------------------
    st.write("### ✏️ Update Expense")
    with st.form("edit_form"):
        col1, col2 = st.columns(2)

        with col1:
            new_date = st.date_input("Date", value=selected_exp.date)
            new_amount = st.number_input("Amount", value=float(selected_exp.amount))

        with col2:
            new_desc = st.text_input("Description", value=selected_exp.description)
            new_cat = st.text_input("Category", value=selected_exp.category or "")

        update_btn = st.form_submit_button("Update Expense")

    if update_btn:
        payload = {
            "date": str(new_date),
            "amount": new_amount,
            "description": new_desc,
            "category": new_cat,
        }

        try:
            res = requests.put(f"{API_BASE}/expenses/{selected_id}", json=payload)
            if res.status_code == 200:
                st.success("Expense updated successfully!")
                st.rerun()
            else:
                st.error(f"Update failed: {res.status_code} {res.text}")
        except Exception as e:
            st.error(f"Error updating: {e}")

    st.write("---")

    # -----------------------------
    # DELETE
    # -----------------------------
    st.write("### 🗑 Delete Expense")

    if st.button("Delete Selected Expense"):
        try:
            res = requests.delete(f"{API_BASE}/expenses/{selected_id}")
            if res.status_code == 204:
                st.success("Expense deleted successfully!")
                st.rerun()
            else:
                st.error(f"Delete failed: {res.status_code} {res.text}")
        except Exception as e:
            st.error(f"Error deleting: {e}")
