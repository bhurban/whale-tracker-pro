import streamlit as st
import traceback

st.set_page_config(page_title="Whale Tracker Pro - Debug", layout="wide")
st.title("🐋 Whale Tracker Pro - Debug Mode")

try:
    st.success("✓ Basic imports working")
    
    # Test HyperliquidSync
    from hyperliquid import HyperliquidSync
    from hyperliquid.utils import constants
    
    st.success("✓ HyperliquidSync imported")
    
    # Check available methods
    sync_methods = [method for method in dir(HyperliquidSync) if not method.startswith('_')]
    st.write("Available methods in HyperliquidSync:")
    st.code(sync_methods)
    
    # Test instantiation
    st.write("Testing HyperliquidSync instantiation...")
    try:
        info = HyperliquidSync(constants.MAINNET_API_URL, skip_ws=True)
        st.success("✓ HyperliquidSync instantiated successfully")
        
        # Test user_state method
        st.write("Testing user_state method...")
        # Use a test address instead of your whale addresses for now
        test_address = "0x0000000000000000000000000000000000000000"
        try:
            user_state = info.user_state(test_address)
            st.success(f"✓ user_state method works: {type(user_state)}")
            st.write(f"Response: {user_state}")
        except Exception as e:
            st.warning(f"❌ user_state failed: {e}")
            
    except Exception as e:
        st.error(f"❌ HyperliquidSync instantiation failed: {e}")
    
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
