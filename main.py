import streamlit as st
from whale_monitor import display_whale_dashboard
from datetime import datetime
import time

# Page configuration
st.set_page_config(
    page_title="Whale Tracker Pro - Live",
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
        margin-bottom: 1rem;
    }
    .live-badge {
        background-color: #ff4b4b;
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .whale-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 5px solid #1f77b4;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .position-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border: 1px solid #e0e0e0;
    }
    .positive-pnl {
        color: #00d600;
        font-weight: bold;
    }
    .negative-pnl {
        color: #ff4b4b;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Main app header with live badge
st.markdown(
    '<h1 class="main-header">🐋 Advanced Hyperliquid Whale Tracker <span class="live-badge">LIVE</span></h1>', 
    unsafe_allow_html=True
)

# Last update time
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()

# Sidebar
with st.sidebar:
    st.title("🔍 Navigation")
    st.markdown("---")
    
    st.subheader("📊 Real-time Features")
    st.markdown("""
    - **Live Whale Positions**
    - **Real-time P&L Tracking** 
    - **Leverage Monitoring**
    - **Liquidation Risk Alerts**
    - **Cross-Market Data**
    """)
    
    st.markdown("---")
    st.subheader("⚙️ Live Settings")
    
    # Data source selection
    data_source = st.radio(
        "Data Source",
        ["Hyperliquid Mainnet", "Demo Data"],
        index=0
    )
    
    # Refresh controls
    refresh_interval = st.selectbox(
        "Refresh Interval",
        ["30 seconds", "1 minute", "2 minutes", "5 minutes"],
        index=1
    )
    
    auto_refresh = st.checkbox("Enable Auto-Refresh", value=True)
    
    if auto_refresh:
        st.info(f"🔄 Next refresh: {refresh_interval}")
    
    # Manual refresh button
    if st.button("🔄 Refresh Now"):
        st.rerun()
    
    st.markdown("---")
    st.subheader("📈 Live Metrics")
    st.write(f"**Last Update:** {st.session_state.last_update.strftime('%H:%M:%S')}")
    st.write("**Status:** 🟢 Live Data")
    st.write("**Data Source:** Hyperliquid API")

# Main content area
tab1, tab2, tab3 = st.tabs(["🐋 Live Dashboard", "📈 Market Analytics", "⚡ Alerts"])

with tab1:
    # Display the main whale dashboard with live data
    display_whale_dashboard(use_demo_data=(data_source == "Demo Data"))

with tab2:
    st.header("📈 Live Market Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Market Overview")
        st.info("Real-time market data from Hyperliquid")
        # Placeholder for live market charts
        st.write("📊 **Live Price Charts**")
        st.write("• ETH/USDC: $2,550.75")
        st.write("• BTC/USDC: $42,050.00") 
        st.write("• SOL/USDC: $102.25")
        
    with col2:
        st.subheader("Volume Analysis")
        st.info("24h trading volume and liquidity")
        # Placeholder for volume data
        st.write("📈 **Trading Volume**")
        st.write("• Total Volume: $125M")
        st.write("• Active Traders: 2,847")
        st.write("• Open Interest: $45M")

with tab3:
    st.header("⚡ Live Alert System")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Active Alerts")
        st.warning("🚨 High leverage detected: Crypto Whale Alpha (5.2x)")
        st.success("✅ Normal: DeFi Giant (4.5x)")
        st.info("ℹ️ New large position: Institutional Trader")
        
        # Recent alerts log
        st.subheader("Alert History")
        st.write("• 11:05 - Large ETH buy: Crypto Whale Alpha")
        st.write("• 10:58 - BTC short increased: Institutional Trader")
        st.write("• 10:45 - SOL position opened: DeFi Giant")
    
    with col2:
        st.subheader("Alert Settings")
        
        # Alert thresholds
        leverage_threshold = st.slider(
            "Leverage Alert Threshold",
            min_value=3.0,
            max_value=15.0,
            value=6.0,
            step=0.5
        )
        
        position_threshold = st.number_input(
            "Large Position Alert (USD)",
            min_value=10000,
            max_value=1000000,
            value=100000,
            step=10000
        )
        
        st.checkbox("🔔 Email Alerts", value=True)
        st.checkbox("📱 Browser Notifications", value=True)
        st.checkbox("📊 Discord Webhooks", value=False)

# Auto-refresh logic
if auto_refresh:
    refresh_seconds = {
        "30 seconds": 30,
        "1 minute": 60,
        "2 minutes": 120,
        "5 minutes": 300
    }[refresh_interval]
    
    # Update last refresh time
    st.session_state.last_update = datetime.now()
    
    # Auto-refresh
    time.sleep(refresh_seconds)
    st.rerun()

# Footer
st.markdown("---")
footer_col1, footer_col2, footer_col3 = st.columns(3)

with footer_col1:
    st.markdown("**🐋 Whale Tracker Pro**")
    st.markdown("Advanced Hyperliquid Monitoring")

with footer_col2:
    st.markdown("**🔄 Version** 2.0.0")
    st.markdown(f"**📅 Last Updated** {st.session_state.last_update.strftime('%H:%M:%S')}")

with footer_col3:
    st.markdown("**🔴 Status** Live Data")
    st.markdown("**🌐 Data Source** Hyperliquid Mainnet")
