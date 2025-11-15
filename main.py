import streamlit as st
import traceback

st.set_page_config(page_title="Whale Tracker Pro - Debug", layout="wide")
st.title("🐋 Whale Tracker Pro - Debug Mode")

try:
    st.success("✓ Basic imports working")
    
    # Test what's in hyperliquid package
    import hyperliquid
    st.success(f"✓ Hyperliquid version: {hyperliquid.__version__}")
    
    # List available attributes in hyperliquid
    st.write("Available in hyperliquid package:")
    st.code([attr for attr in dir(hyperliquid) if not attr.startswith('_')])
    
    # Try different import patterns
    try:
        from hyperliquid.info import Info
        st.success("✓ Imported: from hyperliquid.info import Info")
    except ImportError as e:
        st.warning("❌ from hyperliquid.info import Info failed")
        
    try:
        import hyperliquid.info
        st.success("✓ Imported: import hyperliquid.info")
    except ImportError as e:
        st.warning("❌ import hyperliquid.info failed")
        
    try:
        from hyperliquid import Info
        st.success("✓ Imported: from hyperliquid import Info")
    except ImportError as e:
        st.warning("❌ from hyperliquid import Info failed")
    
    # Now try to import your whale monitor
    from whale_monitor import display_whale_dashboard
    st.success("✓ Whale monitor imported successfully")
    display_whale_dashboard()
    
except Exception as e:
    st.error("🚨 ERROR FOUND:")
    st.write(f"Error type: {type(e).__name__}")
    st.write(f"Error message: {e}")
    st.code(traceback.format_exc())
