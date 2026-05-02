# streamlit_app.py
import streamlit as st
import os

st.title("Smoke test — agriguard-ai")
st.write("Environment PORT:", os.environ.get("PORT"))
st.write("If you see this page, the app is serving correctly.")
