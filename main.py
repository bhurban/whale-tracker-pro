import streamlit as st
from whale_monitor import display_whale_dashboard

# Page configuration
st.set_page_config(
    page_title="Whale Tracker Pro",
    page_icon="🐋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .whale-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 5px solid #1f77b4;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Main app header
st.markdown('<h1 class="main-header">🐋 Advanced Hyperliquid Whale Tracker</h1>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("Navigation")
    st.markdown("---")
    
    st.subheader("📊 Dashboard Features")
    st.markdown("""
    - **Live Whale Positions**
    - **Real-time P&L Tracking** 
    - **Leverage Monitoring**
    - **Cross-Exchange Data**
    - **Email Alert System**
    """)
    
    st.markdown("---")
    st.subheader("⚙️ Settings")
    
    # Refresh interval
    refresh_interval = st.selectbox(
        "Refresh Interval",
        ["30 seconds", "1 minute", "5 minutes", "10 minutes"],
        index=1
    )
    
    # Auto-refresh toggle
    auto_refresh = st.checkbox("Enable Auto-Refresh", value=True)
    
    if auto_refresh:
        st.info(f"Auto-refresh: {refresh_interval}")
    
    st.markdown("---")
    st.markdown("""
    **🔍 Tracking Features:**
    - Large position detection
    - Leverage change alerts
    - Cross-margin monitoring
    - Liquidation risk analysis
    """)

# Main content area - ONLY display the whale dashboard
display_whale_dashboard()

# Footer
st.markdown("---")
footer_col1, footer_col2, footer_col3 = st.columns(3)

with footer_col1:
    st.markdown("**Whale Tracker Pro**")
    st.markdown("Advanced Hyperliquid Monitoring")

with footer_col2:
    st.markdown("**Version** 1.0.0")
    st.markdown("**Last Updated** Recently")

with footer_col3:
    st.markdown("**Status** 🟢 Operational")
    st.markdown("**Data Source** Hyperliquid")
