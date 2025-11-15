import streamlit as st
import pandas as pd
import plotly.express as px  # ← ADD THIS IMPORT
from datetime import datetime
import time
from hyperliquid import HyperliquidSync  # For synchronous operations


def safe_float(value, default=0.0):
    """Safely convert value to float"""
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default

def calculate_pnl_percent(pnl, value):
    """Calculate P&L percentage correctly for both long and short positions"""
    if pnl == 0:
        return 0
    
    initial_value = value - pnl
    if initial_value == 0:
        return 0
    
    return (pnl / abs(initial_value)) * 100


def get_whale_data():
    """Fetch real whale data using CCXT methods"""
    from config import WHALE_ADDRESSES, WHALE_GEO_DATA
    
    try:
        exchange = HyperliquidSync()
        whale_data = {}
        
        # Load markets first (required by CCXT)
        markets = exchange.load_markets()
        
        for wallet, whale_name in WHALE_ADDRESSES.items():
            try:
                # Try to fetch positions (this might require API keys for private data)
                positions = exchange.fetch_positions()
                
                # For public data, you might need to use different endpoints
                # or use the official Hyperliquid API directly
                
                whale_data[wallet] = {
                    'name': whale_name,
                    'positions': positions or [],
                    'geo': WHALE_GEO_DATA.get(wallet, {}),
                    'last_updated': datetime.now()
                }
                
            except Exception as e:
                print(f"Error for {whale_name}: {e}")
                continue
                
        return whale_data
        
    except Exception as e:
        print(f"Exchange error: {e}")
        return {}


def display_whale_dashboard(whale_data=None):
    """Display the main whale tracking dashboard"""
    from datetime import datetime
    import streamlit as st
    
    if whale_data is None:
        whale_data = get_whale_data()
    
    # Show warning if using demo data
    if not whale_data:
        st.warning("No whale data available. Using demo data.")
        # Create demo data
        whale_data = {
            'demo_wallet_1': {
                'name': 'Demo Whale 1',
                'positions': [{
                    'symbol': 'ETH/USDC',
                    'side': 'long',
                    'size': 12500,
                    'entryPrice': 2450,
                    'markPrice': 2550,
                    'liqPrice': 2000,
                    'leverage': 5.2,
                    'unrealizedPnl': 1250,
                    'margin': 2400
                }],
                'geo': {'region': 'North America'},
                'last_updated': datetime.now()
            },
            'demo_wallet_2': {
                'name': 'Demo Whale 2', 
                'positions': [{
                    'symbol': 'BTC/USDC',
                    'side': 'short',
                    'size': 85000,
                    'entryPrice': 42500,
                    'markPrice': 42000,
                    'liqPrice': 45000,
                    'leverage': 3.8,
                    'unrealizedPnl': 1000,
                    'margin': 22368
                }],
                'geo': {'region': 'Europe'},
                'last_updated': datetime.now()
            }
        }
    
    # Dashboard header
    st.write(f"**Tracking {len(whale_data)} active whales**")
    
    # Display whale cards
    for wallet, data in whale_data.items():
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.subheader(f"🐋 {data['name']}")
                st.write(f"**Wallet:** `{wallet[:8]}...{wallet[-6:]}`")
                st.write(f"**Region:** {data['geo'].get('region', 'Unknown')}")
                st.write(f"**Last Updated:** {data['last_updated'].strftime('%Y-%m-%d %H:%M:%S')}")
            
            with col2:
                if data['positions']:
                    position = data['positions'][0]  # Show first position
                    pnl_delta = f"${position['unrealizedPnl']:+,.0f} PnL"
                    st.metric(
                        label=f"{position['symbol']} {position['side'].upper()}",
                        value=f"${position['size']:,.0f}",
                        delta=pnl_delta
                    )
                else:
                    st.info("No active positions")
            
            # Show all positions with expanders
            if data['positions']:
                for i, position in enumerate(data['positions']):
                    # Use a unique key for each expander
                    with st.expander(f"📊 {position['symbol']} - {position['side']} Position", key=f"{wallet}_{i}"):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.write("**Position Details**")
                            st.write(f"Size: ${position['size']:,.0f}")
                            st.write(f"Entry: ${position['entryPrice']:,.0f}")
                            st.write(f"Mark: ${position['markPrice']:,.0f}")
                        
                        with col2:
                            st.write("**Risk Metrics**")
                            st.write(f"Leverage: {position['leverage']}x")
                            st.write(f"Margin: ${position['margin']:,.0f}")
                            st.write(f"Liq Price: ${position['liqPrice']:,.0f}")
                        
                        with col3:
                            st.write("**Performance**")
                            pnl_color = "green" if position['unrealizedPnl'] >= 0 else "red"
                            st.write(f"Unrealized PnL: :{pnl_color}[${position['unrealizedPnl']:+,.0f}]")
                            
                            # Calculate PnL percentage
                            initial_value = position['size'] - position['unrealizedPnl']
                            if initial_value != 0:
                                pnl_percent = (position['unrealizedPnl'] / abs(initial_value)) * 100
                                st.write(f"PnL %: :{pnl_color}[{pnl_percent:+.1f}%]")
            
            st.divider()
