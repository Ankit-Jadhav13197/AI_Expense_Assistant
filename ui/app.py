import streamlit as st
import requests

st.title("AI Smart Expense Assistant")

api_url = "http://127.0.0.1:8000/"

response = requests.get(api_url)

st.write("Backend Response:", response.json())
