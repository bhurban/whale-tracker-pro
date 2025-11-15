import streamlit as st
import time
#from whale_monitor import display_whale_dashboard, display_alerts_history, display_analytics, display_whale_profiles
from whale_monitor import display_whale_dashboard, display_alerts_history
def main():
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
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .nav-tabs {
        background: #f0f2f6;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .whale-card {
        background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
    }
    
    /* Style the tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 8px 8px 0px 0px;
        gap: 8px;
        padding-top: 10px;
        padding-bottom: 10px;
        font-weight: bold;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #1E88E5;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">🐋 Whale Tracker Pro</h1>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("⚙️ Configuration")
    
    # Auto-refresh toggle
    auto_refresh = st.sidebar.checkbox("🔄 Auto Refresh (30s)", value=False)
    
    # Data source selection
    data_source = st.sidebar.radio("📊 Data Source:", ["Live Data", "Demo Data"])
    
    # Alert settings
    st.sidebar.markdown("---")
    st.sidebar.subheader("🚨 Alert Settings")
    alert_leverage = st.sidebar.slider("High Leverage Alert", 3, 20, 5)
    alert_size = st.sidebar.slider("Large Trade Alert ($)", 50000, 500000, 100000, step=50000)
    
    # Navigation Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Live Dashboard", 
        "🚨 Alerts Center", 
        "📈 Analytics", 
        "🐋 Whale Profiles"
    ])
    
    use_demo_data = (data_source == "Demo Data")
    
    with tab1:
        st.subheader("🌐 Real-Time Whale Positions")
        display_whale_dashboard(use_demo_data=use_demo_data)
    
    with tab2:
        st.subheader("🚨 Trading Alerts & Signals")
        display_alerts_history(use_demo_data=use_demo_data)
    
    with tab3:
        st.subheader("📈 Market Analytics")
        display_analytics(use_demo_data=use_demo_data)
    
    with tab4:
        st.subheader("🐋 Whale Profiles & History")
        display_whale_profiles(use_demo_data=use_demo_data)
    
    # Auto-refresh logic (simplified)
    if auto_refresh:
        refresh_placeholder = st.sidebar.empty()
        refresh_placeholder.info("🔄 Auto-refresh enabled - page will refresh in 30s")
        time.sleep(30)
        st.experimental_rerun()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Data Sources")
    st.sidebar.info("""
    - **Hyperliquid API**: Real whale positions
    - **CoinGecko**: Live market prices
    - **Real Addresses**: Verified whale wallets
    """)

if __name__ == "__main__":
    main()
