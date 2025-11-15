import streamlit as st
import pandas as pd
import plotly.express as px  # ← ADD THIS IMPORT
from datetime import datetime
import time
from hyperliquid.info import Info
from hyperliquid.utils import constants

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
    """Fetch live whale data from Hyperliquid API"""
    from config import WHALE_ADDRESSES, WHALE_GEO_DATA
    
    info = Info(constants.MAINNET_API_URL, skip_ws=True)
    whale_data = {}
    
    for wallet, whale_name in WHALE_ADDRESSES.items():
        try:
            user_state = info.user_state(wallet)
            positions = user_state.get("assetPositions", [])
            
            total_value = sum(safe_float(p.get("position", {}).get("positionValue", 0)) for p in positions)
            total_pnl = sum(safe_float(p.get("position", {}).get("unrealizedPnl", 0)) for p in positions)
            
            formatted_positions = []
            for pos in positions:
                position = pos.get("position", {})
                size = safe_float(position.get("szi", 0))
                position_type = "LONG 🟢" if size > 0 else "SHORT 🔴"
                leverage = safe_float(position.get("leverage", {}).get("value", 1))
                value = safe_float(position.get("positionValue", 0))
                pnl = safe_float(position.get("unrealizedPnl", 0))
                
                pnl_percent = calculate_pnl_percent(pnl, value)
                
                formatted_positions.append({
                    'Coin': position.get('coin', 'UNKNOWN'),
                    'Type': position_type,
                    'Value': value,
                    'Leverage': leverage,
                    'P&L': pnl,
                    'P&L %': pnl_percent,
                    'Entry Price': safe_float(position.get('entryPx', 0)),
                    'Size': abs(size),
                    'Leverage_Display': f"{leverage:.1f}x"
                })
            
            geo_data = WHALE_GEO_DATA.get(wallet, {})
            
            whale_data[whale_name] = {
                'wallet': wallet,
                'display_wallet': wallet[:8] + '...' + wallet[-6:],
                'country': geo_data.get('country', 'Unknown'),
                'region': geo_data.get('region', 'Unknown'),
                'risk_level': geo_data.get('risk_level', 'Unknown'),
                'total_value': total_value,
                'total_pnl': total_pnl,
                'position_count': len(positions),
                'positions': formatted_positions,
                'long_count': sum(1 for p in formatted_positions if p['Type'] == 'LONG 🟢'),
                'short_count': sum(1 for p in formatted_positions if p['Type'] == 'SHORT 🔴'),
                'avg_leverage': safe_float(sum(p['Leverage'] for p in formatted_positions) / len(formatted_positions) if formatted_positions else 0)
            }
            
        except Exception as e:
            print(f"❌ Error fetching data for {whale_name}: {str(e)}")
            geo_data = WHALE_GEO_DATA.get(wallet, {})
            whale_data[whale_name] = {
                'wallet': wallet,
                'display_wallet': wallet[:8] + '...' + wallet[-6:],
                'country': geo_data.get('country', 'Unknown'),
                'region': geo_data.get('region', 'Unknown'),
                'risk_level': geo_data.get('risk_level', 'Unknown'),
                'total_value': 0,
                'total_pnl': 0,
                'position_count': 0,
                'positions': [],
                'long_count': 0,
                'short_count': 0,
                'avg_leverage': 0
            }
    
    return whale_data

def display_whale_dashboard(whale_data):
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
