# This will COMPLETELY REPLACE your main.py file
echo import streamlit as st > main.py
echo import traceback >> main.py
echo. >> main.py
echo st.set_page_config(page_title="Whale Tracker Pro - Debug", layout="wide") >> main.py
echo st.title("🐋 Whale Tracker Pro - Debug Mode") >> main.py
echo. >> main.py
echo try: >> main.py
echo     st.success("✓ Basic imports working") >> main.py
echo     from whale_monitor import display_whale_dashboard >> main.py
echo     st.success("✓ Whale monitor imported successfully") >> main.py
echo     display_whale_dashboard() >> main.py
echo     st.success("✓ Dashboard displayed successfully") >> main.py
echo except Exception as e: >> main.py
echo     st.error("🚨 ERROR FOUND:") >> main.py
echo     st.write(f"Error type: {type(e).__name__}") >> main.py
echo     st.write(f"Error message: {e}") >> main.py
echo     st.code(traceback.format_exc()) >> main.py
