import streamlit as st
import requests
import json
from datetime import datetime

def test_hyperliquid_addresses():
    """Test if these addresses return real data from Hyperliquid"""
    
    test_addresses = {
        "0x5b5d51203a0f9079f8aeb098a6523a13f298c060": "🦁 Singapore Whale",
        "0xc2a30212a8ddac9e123944d6e29faddce994e5f2": "🦅 US Whale", 
        "0x4044570e13b5184f7eb2709de25a4eb766a4794c": "👑 UK Whale",
        "0x6a56d5665bae79056207c8605c7fa5421737711b": "🕌 Emirates Whale",
        "0xd83cff88a32ffbf3951f2b13e4a0a37103b3193d": "🐉 Hong Kong Whale"
    }
    
    st.header("🔍 Testing Real Wallet Addresses")
    
    for wallet, name in test_addresses.items():
        st.write(f"**Testing:** {name}")
        st.write(f"**Address:** `{wallet}`")
        
        try:
            url = "https://api.hyperliquid.xyz/info"
            payload = {
                "type": "clearinghouseState",
                "user": wallet
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data and 'assetPositions' in data:
                    positions_count = len(data['assetPositions'])
                    if positions_count > 0:
                        st.success(f"✅ **REAL DATA FOUND!** {positions_count} positions")
                        # Show some actual data
                        for i, pos in enumerate(data['assetPositions'][:2]):  # Show first 2 positions
                            position_data = pos.get('position', {})
                            st.write(f"  Position {i+1}: {position_data.get('coin', 'Unknown')} - Size: {position_data.get('szi', 0)}")
                    else:
                        st.info("ℹ️ Address valid but no active positions")
                else:
                    st.warning("⚠️ No position data in response")
            else:
                st.error(f"❌ API Error: {response.status_code}")
                
        except Exception as e:
            st.error(f"💥 Error: {str(e)}")
        
        st.markdown("---")

def display_whale_dashboard(use_demo_data=False):
    """Test the real addresses first"""
    test_hyperliquid_addresses()
    
    # Then show realistic data as fallback
    st.info("📊 If no real data found above, showing realistic simulation below...")
    
    # ... [rest of your realistic data code] ...

# For quick testing, you can temporarily replace your display_whale_dashboard function
# with this test version to see if these addresses work
