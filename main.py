import streamlit as st
import pandas as pd  # Add this import
from whale_monitor import display_whale_dashboard, display_alerts_history

# Page configuration
st.set_page_config(
    page_title="Crypto Whale Monitor",
    page_icon="🐋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E90FF;
        text-align: center;
        margin-bottom: 1rem;
    }
    .whale-card {
        background-color: #0E1117;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #1E90FF;
    }
    .alert-high {
        background-color: #ff4444;
        color: white;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.2rem 0;
    }
    .alert-medium {
        background-color: #ffaa00;
        color: black;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.2rem 0;
    }
    .alert-low {
        background-color: #44ff44;
        color: black;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.2rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.markdown('<div class="main-header">🐋 Crypto Whale Monitor</div>', unsafe_allow_html=True)
st.markdown("### Track major cryptocurrency whales and their trading activity in real-time")

# Initialize session state for demo mode
if 'use_demo_data' not in st.session_state:
    st.session_state.use_demo_data = False

# Sidebar
with st.sidebar:
    st.title("Settings")
    
    # Demo mode toggle
    use_demo = st.toggle("Demo Mode", value=st.session_state.use_demo_data)
    if use_demo != st.session_state.use_demo_data:
        st.session_state.use_demo_data = use_demo
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 🔍 Data Sources")
    st.markdown("""
    - **Binance** - Spot & Futures
    - **Bybit** - Derivatives
    - **DEX** - Uniswap, PancakeSwap
    - **Whale Alert** - Large transactions
    """)
    
    st.markdown("---")
    st.markdown("### 📊 Metrics Tracked")
    st.markdown("""
    - Position Size
    - Leverage
    - PnL
    - Entry/Exit Prices
    - Trading Patterns
    - Risk Levels
    """)

# Main app with ALL tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🐋 Whale Dashboard", 
    "🚨 Alerts Center", 
    "📈 Market Overview", 
    "🔍 Whale Analytics", 
    "⚙️ Settings"
])

with tab1:
    display_whale_dashboard(st.session_state.use_demo_data)

with tab2:
    display_alerts_history(st.session_state.use_demo_data)

with tab3:
    st.header("📈 Market Overview")
    st.info("Market data and trends coming soon...")
    
    # Placeholder for market overview
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("BTC Dominance", "52.3%", "0.5%")
    with col2:
        st.metric("Total Crypto Market Cap", "$1.72T", "+2.3%")
    with col3:
        st.metric("Fear & Greed Index", "76 (Greed)", "-4")
    
    st.markdown("---")
    st.subheader("Top Movers (24h)")
    
    # Sample market movers
    movers_data = {
        "Coin": ["BTC", "ETH", "SOL", "XRP", "ADA", "DOT"],
        "Price": ["$43,500", "$2,300", "$95", "$0.62", "$0.52", "$7.80"],
        "Change 24h": ["+2.3%", "+1.8%", "+5.2%", "-0.8%", "+3.1%", "+2.7%"],
        "Volume": ["$28.4B", "$14.2B", "$3.8B", "$1.2B", "$0.8B", "$0.5B"]
    }
    
    movers_df = pd.DataFrame(movers_data)
    st.dataframe(movers_df, use_container_width=True, hide_index=True)

with tab4:
    st.header("🔍 Whale Analytics")
    st.info("Advanced whale behavior analysis and patterns")
    
    # Analytics metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Whales Tracked", "47")
    with col2:
        st.metric("Avg Position Size", "$2.8M")
    with col3:
        st.metric("Success Rate", "63.2%")
    with col4:
        st.metric("Avg Hold Time", "18.5 days")
    
    st.markdown("---")
    
    # Whale behavior insights
    st.subheader("📊 Whale Trading Patterns")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Most Active Whales**")
        active_whales = {
            "Whale": ["Singapore Whale", "Dubai Trader", "European Fund", "US Institution", "Asian Fund"],
            "Trades (7d)": [28, 19, 15, 12, 9],
            "Win Rate": ["68%", "72%", "61%", "58%", "65%"]
        }
        active_df = pd.DataFrame(active_whales)
        st.dataframe(active_df, use_container_width=True, hide_index=True)
    
    with col2:
        st.write("**Top Performing Assets**")
        top_assets = {
            "Asset": ["BTC", "ETH", "SOL", "AVAX", "LINK"],
            "Whale Interest": ["High", "High", "Medium", "Medium", "Low"],
            "Avg Return": ["+18.3%", "+12.7%", "+25.4%", "+32.1%", "+8.9%"]
        }
        assets_df = pd.DataFrame(top_assets)
        st.dataframe(assets_df, use_container_width=True, hide_index=True)
    
    # Risk analysis
    st.markdown("---")
    st.subheader("🎯 Risk Assessment")
    
    risk_col1, risk_col2, risk_col3 = st.columns(3)
    with risk_col1:
        st.metric("High Leverage Positions", "8", "3 new")
    with risk_col2:
        st.metric("At Risk Positions", "12", "-2")
    with risk_col3:
        st.metric("Liquidations Risk", "Medium", "Stable")

with tab5:
    st.header("⚙️ Settings & Configuration")
    
    st.subheader("Data Sources")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.checkbox("Binance API", value=True)
        st.checkbox("Bybit API", value=True)
        st.checkbox("Whale Alert", value=True)
        st.checkbox("Blockchain Scan", value=True)
    
    with col2:
        st.checkbox("Twitter Feed", value=False)
        st.checkbox("Telegram Channels", value=False)
        st.checkbox("News Sentiment", value=False)
    
    st.markdown("---")
    
    st.subheader("Alert Preferences")
    
    alert_col1, alert_col2 = st.columns(2)
    
    with alert_col1:
        st.checkbox("Large Positions (>$1M)", value=True)
        st.checkbox("High Leverage (>10x)", value=True)
        st.checkbox("Big Profits (>$500K)", value=True)
    
    with alert_col2:
        st.checkbox("Significant Losses", value=True)
        st.checkbox("New Whale Activity", value=True)
        st.checkbox("Market Moving Trades", value=True)
    
    st.markdown("---")
    
    st.subheader("App Settings")
    
    setting_col1, setting_col2 = st.columns(2)
    
    with setting_col1:
        st.selectbox("Refresh Interval", ["30 seconds", "1 minute", "5 minutes", "15 minutes"])
        st.selectbox("Default Timeframe", ["24 hours", "7 days", "30 days", "All time"])
    
    with setting_col2:
        st.selectbox("Theme", ["Dark", "Light", "Auto"])
        st.selectbox("Data Precision", ["Auto", "High", "Medium", "Low"])
    
    st.markdown("---")
    st.button("Save Settings", type="primary")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>🔒 <em>Data is updated in real-time from multiple blockchain and exchange sources</em></p>
    <p>⚠️ <em>This tool is for educational purposes only. Always do your own research.</em></p>
</div>
""", unsafe_allow_html=True)
