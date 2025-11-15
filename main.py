import streamlit as st
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

# Main app with tabs
tab1, tab2 = st.tabs(["🐋 Whale Dashboard", "🚨 Alerts Center"])

with tab1:
    display_whale_dashboard(st.session_state.use_demo_data)

with tab2:
    display_alerts_history(st.session_state.use_demo_data)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>🔒 <em>Data is updated in real-time from multiple blockchain and exchange sources</em></p>
    <p>⚠️ <em>This tool is for educational purposes only. Always do your own research.</em></p>
</div>
""", unsafe_allow_html=True)
