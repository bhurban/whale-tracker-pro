import streamlit as st
import time
from whale_monitor import display_whale_dashboard

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
    .whale-card {
        background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">🐋 Whale Tracker Pro</h1>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("⚙️ Configuration")
    
    # Auto-refresh toggle
    auto_refresh = st.sidebar.checkbox("🔄 Auto Refresh (30s)", value=False)
    if auto_refresh:
        refresh_countdown = st.sidebar.empty()
        for i in range(30, 0, -1):
            refresh_countdown.text(f"🕐 Refreshing in {i}s...")
            time.sleep(1)
        st.runtime.legacy_caching.clear_cache()
        st.experimental_rerun()
    
    # Data source selection
    data_source = st.sidebar.radio("📊 Data Source:", ["Live Data", "Demo Data"])
    
    # Alert settings
    st.sidebar.markdown("---")
    st.sidebar.subheader("🚨 Alert Settings")
    alert_leverage = st.sidebar.slider("High Leverage Alert", 3, 20, 5)
    alert_size = st.sidebar.slider("Large Trade Alert ($)", 50000, 500000, 100000, step=50000)
    
    # Display dashboard
    use_demo_data = (data_source == "Demo Data")
    display_whale_dashboard(use_demo_data=use_demo_data)
    
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
