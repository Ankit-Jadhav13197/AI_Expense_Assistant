import streamlit as st
import pandas as pd
import requests
from datetime import datetime

API_BASE = st.secrets.get("api_base", "http://127.0.0.1:8000")

def app():
    st.title("Forecast — Future Spending")

    col1, col2 = st.columns([3, 1])
    with col1:
        periods = st.selectbox(
            "Forecast horizon",
            [7, 15, 30, 60],
            index=2,
            format_func=lambda x: f"{x} days"
        )
    with col2:
        model = st.selectbox("Model", ["prophet", "lr"])

    freq = "D"

    if st.button("Get forecast"):
        url = f"{API_BASE}/forecast/?periods={periods}&freq=D&model={model}"
        with st.spinner("Fetching forecast..."):
            resp = requests.get(url, timeout=20)

        if resp.status_code != 200:
            st.error(f"Error {resp.status_code}: {resp.text}")
            return

        data = resp.json()

        if "error" in data:
            st.warning(data["error"])
            return

        forecast_rows = data["forecast"]
        df = pd.DataFrame(forecast_rows)
        df["date"] = pd.to_datetime(df["date"])
        df_sorted = df.sort_values("date")

        st.subheader("Predicted spending")
        st.line_chart(df_sorted.set_index("date")[["predicted"]])

        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        ax.plot(df_sorted["date"], df_sorted["predicted"], label="predicted")
        ax.fill_between(
            df_sorted["date"],
            df_sorted["lower"],
            df_sorted["upper"],
            alpha=0.2,
            label="confidence"
        )
        ax.set_ylabel("Amount")
        ax.set_xlabel("Date")
        ax.legend()
        st.pyplot(fig)

        st.dataframe(df_sorted.set_index("date").round(2))

        if data.get("metrics"):
            st.write("### Metrics")
            st.write(data["metrics"])
