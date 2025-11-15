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
    if whale_data is None:
        whale_data = get_whale_data()

# In your display_whale_dashboard function, add:
    if not whale_data:
        st.warning("No whale data available. Using demo data.")

    # Show demo data or instructions

    # Rest of your function with proper indentation
    st.title("🐋 Live Whale Positions")

    
    """Display the main whale tracking dashboard"""
    st.markdown("## 🐋 Live Whale Positions")
    
    for whale_name, data in whale_data.items():
        status = "🟢" if data['total_value'] > 1000 else "🔴"
        
        with st.expander(f"{status} {whale_name} - ${data['total_value']:,.2f} | {data['position_count']} Positions", 
                        expanded=data['total_value'] > 1000):
            
            # Whale info columns
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📍 Country", data['country'])
            with col2:
                st.metric("🌍 Region", data['region'])
            with col3:
                pnl_percent = (data['total_pnl'] / data['total_value']) * 100 if data['total_value'] > 0 else 0
                st.metric("💸 Total P&L", f"${data['total_pnl']:+,.2f}", 
                         delta=f"{pnl_percent:+.1f}%" if data['total_value'] > 0 else "0%")
            with col4:
                st.metric("🎯 Risk Level", data['risk_level'])
            
            # Positions table
            if data['positions']:
                positions_df = pd.DataFrame(data['positions'])
                
                # Format display dataframe
                display_df = positions_df.copy()
                display_df['Value'] = display_df['Value'].apply(lambda x: f"${x:,.2f}")
                display_df['P&L'] = display_df['P&L'].apply(lambda x: f"${x:+,.2f}")
                display_df['P&L %'] = display_df['P&L %'].apply(lambda x: f"{x:+.1f}%")
                display_df['Entry Price'] = display_df['Entry Price'].apply(
                    lambda x: f"${x:,.2f}" if x > 1 else f"${x:.4f}")
                display_df['Leverage'] = display_df['Leverage_Display']  # Use the display version
                
                # Remove the temporary column for display
                display_df_display = display_df.drop('Leverage_Display', axis=1)
                
                # FIXED: Streamlit warning by using width='stretch'
                st.dataframe(display_df_display, width='stretch')
                
                # Position value chart
                if len(positions_df) > 0:
                    fig_bar = px.bar(positions_df, x='Coin', y='Value', 
                                    color='Type',
                                    title=f'{whale_name} - Position Values',
                                    color_discrete_map={'SHORT 🔴': '#FF6B6B', 'LONG 🟢': '#4ECDC4'})
                    st.plotly_chart(fig_bar, use_container_width=True)
                    
                # Leverage and position stats
                col1, col2 = st.columns(2)
                with col1:
                    if len(positions_df) > 0:
                        # Use the numeric leverage column directly
                        avg_leverage = positions_df['Leverage'].mean()
                        st.metric("📊 Average Leverage", f"{avg_leverage:.1f}x")
                    else:
                        st.metric("📊 Average Leverage", "0x")
                
                with col2:
                    st.metric("🔄 Position Types", f"🟢{data['long_count']} 🔴{data['short_count']}")
            else:
                st.info("No active positions for this whale")
