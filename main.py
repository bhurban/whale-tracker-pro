import streamlit as st
import traceback

st.set_page_config(page_title="Whale Tracker Pro - Debug", layout="wide")
st.title("🐋 Whale Tracker Pro - Debug Mode")

try:
    st.success("✓ Basic imports working")
    
    # Test what's in hyperliquid package
    import hyperliquid
    st.success("✓ Hyperliquid package imported")
    
    # List available attributes in hyperliquid
    st.write("Available in hyperliquid package:")
    hyperliquid_attrs = [attr for attr in dir(hyperliquid) if not attr.startswith('_')]
    st.code(hyperliquid_attrs)
    
    # Try different import patterns
    st.write("Testing import patterns:")
    
    try:
        from hyperliquid.info import Info
        st.success("✓ Imported: from hyperliquid.info import Info")
        st.write(f"Info class: {Info}")
    except ImportError as e:
        st.warning(f"❌ from hyperliquid.info import Info failed: {e}")
        
    try:
        import hyperliquid.info as info
        st.success("✓ Imported: import hyperliquid.info")
        st.write(f"info module: {info}")
        st.write("Available in info:", [attr for attr in dir(info) if not attr.startswith('_')])
    except ImportError as e:
        st.warning(f"❌ import hyperliquid.info failed: {e}")
        
    try:
        from hyperliquid import Info
        st.success("✓ Imported: from hyperliquid import Info")
        st.write(f"Info: {Info}")
    except ImportError as e:
        st.warning(f"❌ from hyperliquid import Info failed: {e}")
    
    # Try to see if there are any submodules
    st.write("Checking for submodules:")
    try:
        import hyperliquid.exchange
        st.success("✓ Found: hyperliquid.exchange")
    except ImportError as e:
        st.warning(f"❌ hyperliquid.exchange: {e}")
        
    try:
        import hyperliquid.websocket
        st.success("✓ Found: hyperliquid.websocket")
    except ImportError as e:
        st.warning(f"❌ hyperliquid.websocket: {e}")
    
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
