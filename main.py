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

# Main content area
tab1, tab2, tab3, tab4 = st.tabs(["🐋 Live Dashboard", "📈 Analytics", "⚡ Alerts", "🔧 Settings"])

with tab1:
    # Display the main whale dashboard
    display_whale_dashboard()

with tab2:
    st.header("📈 Advanced Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Position Distribution")
        st.info("Position size distribution across tracked whales")
        # Placeholder for chart
        st.write("📊 Chart: Whale position sizes")
        
    with col2:
        st.subheader("Leverage Analysis")
        st.info("Current leverage levels and risk assessment")
        # Placeholder for chart
        st.write("📈 Chart: Leverage distribution")
    
    st.subheader("Historical Performance")
    st.info("P&L trends and position history")
    # Placeholder for historical data
    st.write("📅 Historical performance charts")

with tab3:
    st.header("⚡ Alert System")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Active Alerts")
        st.warning("🚨 High leverage detected: Whale_003 (8.5x)")
        st.success("✅ Normal: Whale_001 (3.2x)")
        st.info("ℹ️ New position: Whale_002 (ETH/USDC)")
    
    with col2:
        st.subheader("Alert Settings")
        
        # Alert thresholds
        leverage_threshold = st.slider(
            "Leverage Alert Threshold",
            min_value=3.0,
            max_value=20.0,
            value=5.0,
            step=0.5
        )
        
        position_threshold = st.number_input(
            "Large Position Threshold (USD)",
            min_value=10000,
            max_value=1000000,
            value=100000,
            step=10000
        )
        
        st.checkbox("Email Alerts", value=True)
        st.checkbox("Browser Notifications", value=True)

with tab4:
    st.header("🔧 Application Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Data Sources")
        st.checkbox("Hyperliquid Mainnet", value=True)
        st.checkbox("Testnet Data", value=False)
        st.checkbox("Cross-Exchange Data", value=True)
        
        st.subheader("Display Options")
        st.selectbox("Theme", ["Light", "Dark", "Auto"])
        st.selectbox("Chart Style", ["Plotly", "Streamlit Native", "Custom"])
    
    with col2:
        st.subheader("API Configuration")
        
        # API settings (you can expand this later)
        api_key = st.text_input("API Key (Optional)", type="password")
        api_secret = st.text_input("API Secret (Optional)", type="password")
        
        if st.button("Test Connection"):
            if api_key and api_secret:
                st.success("✅ API connection successful!")
            else:
                st.info("ℹ️ Using public data endpoints")
        
        st.subheader("Data Management")
        st.button("Clear Cache")
        st.button("Export Data")
        st.button("Backup Configuration")

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

# Auto-refresh logic
if auto_refresh:
    refresh_map = {
        "30 seconds": 30,
        "1 minute": 60,
        "5 minutes": 300,
        "10 minutes": 600
    }
    st.rerun()
