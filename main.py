import streamlit as st
import traceback

st.set_page_config(page_title="Whale Tracker Pro - Debug", layout="wide")
st.title("🐋 Whale Tracker Pro - Debug Mode")

try:
    st.success("✓ Basic imports working")
    from whale_monitor import display_whale_dashboard
    st.success("✓ Whale monitor imported successfully")
    display_whale_dashboard()
    st.success("✓ Dashboard displayed successfully")
except Exception as e:
    st.error("🚨 ERROR FOUND:")
    st.write(f"Error type: {type(e).__name__}")
    st.write(f"Error message: {e}")
    st.code(traceback.format_exc())
