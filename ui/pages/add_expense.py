import os
import streamlit as st
from datetime import date
import requests

API_BASE = st.secrets.get("api_base", "http://127.0.0.1:8000")

# Keep category in session so it persists after ML prediction
if "predicted_category" not in st.session_state:
    st.session_state["predicted_category"] = ""

def app():
    st.header("Add Expense")

    # INPUT FIELDS
    d = st.date_input("Date", value=date.today())
    desc = st.text_input("Description")

    # CATEGORY INPUT (auto-filled after prediction)
    category = st.text_input(
        "Category (optional)",
        value=st.session_state["predicted_category"]
    )

    amount = st.number_input("Amount", min_value=0.01, format="%.2f")

    # ---- AUTO CATEGORIZE BUTTON ----
    if st.button("Auto Categorize"):
        if not desc.strip():
            st.warning("Please enter a description first.")
        else:
            try:
                r = requests.post(f"{API_BASE}/ml/predict", json={"description": desc}, timeout=5)
                if r.ok:
                    data = r.json()
                    predicted = data["category"]
                    st.success(f"Predicted category: {predicted}")

                    # Save in session
                    st.session_state["predicted_category"] = predicted

                    # Show probabilities
                    st.write("Top predictions:")
                    for label, p in sorted(data["probabilities"], key=lambda x: x[1], reverse=True)[:5]:
                        st.write(f"- {label}: {p:.2f}")

                else:
                    st.error(f"Prediction failed: {r.text}")

            except Exception as e:
                st.error(f"Error contacting backend: {e}")

    # ---- SUBMIT FORM ----
    if st.button("Add Expense"):
        payload = {
            "date": d.isoformat(),
            "description": desc,
            "amount": amount,
            "category": category or None
        }

        try:
            r = requests.post(f"{API_BASE}/expenses/", json=payload, timeout=5)
            if r.status_code == 201:
                st.success("Expense created successfully!")

                # reset category after save
                st.session_state["predicted_category"] = ""
            else:
                st.error(f"Failed: {r.status_code} {r.text}")

        except Exception as e:
            st.error(f"Request failed: {e}")

