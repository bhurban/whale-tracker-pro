import streamlit as st
import traceback

st.set_page_config(page_title="Whale Tracker Pro - Debug", layout="wide")
st.title("🐋 Whale Tracker Pro - Debug Mode")

try:
    st.success("✓ Basic imports working")
    
    # Test HyperliquidSync without utils
    from hyperliquid import HyperliquidSync
    
    st.success("✓ HyperliquidSync imported")
    
    # Check available methods
    sync_methods = [method for method in dir(HyperliquidSync) if not method.startswith('_')]
    st.write("Available methods in HyperliquidSync:")
    st.code(sync_methods)
    
    # Test different instantiation methods
    st.write("Testing HyperliquidSync instantiation...")
    
    try:
        # Try with mainnet URL
        info = HyperliquidSync("https://api.hyperliquid.xyz")
        st.success("✓ HyperliquidSync with mainnet URL")
    except Exception as e:
        st.warning(f"❌ With mainnet URL: {e}")
    
    try:
        # Try with no parameters
        info = HyperliquidSync()
        st.success("✓ HyperliquidSync with no parameters")
    except Exception as e:
        st.warning(f"❌ With no parameters: {e}")
        
    try:
        # Try with skip_ws
        info = HyperliquidSync(skip_ws=True)
        st.success("✓ HyperliquidSync with skip_ws=True")
    except Exception as e:
        st.warning(f"❌ With skip_ws: {e}")
    
    # Now try to import your whale monitor
    st.write("Attempting to import whale_monitor...")
    from whale_monitor import display_whale_dashboard
    st.success("✓ Whale monitor imported successfully")
    display_whale_dashboard()
    
except Exception as e:
    st.error("🚨 ERROR FOUND:")
    st.write(f"Error type: {type(e).__name__}")
    st.write(f"Error message: {e}")
    st.code(traceback.format_exc())
