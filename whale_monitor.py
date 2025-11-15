import streamlit as st
import pandas as pd
from datetime import datetime
from hyperliquid import HyperliquidSync

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
    """Fetch whale data - currently using demo data"""
    try:
        # For now, return demo data
        # In the future, you can integrate real Hyperliquid API here
        demo_whales = {
            '0x742d35Cc6634C0532925a3b8D': {
                'name': 'Crypto Whale Alpha',
                'positions': [{
                    'symbol': 'ETH/USDC',
                    'side': 'long',
                    'size': 125000,
                    'entryPrice': 2450.50,
                    'markPrice': 2550.75,
                    'liqPrice': 1950.25,
                    'leverage': 5.2,
                    'unrealizedPnl': 12500,
                    'margin': 24038
                }],
                'geo': {'region': 'North America', 'country': 'US'},
                'last_updated': datetime.now()
            },
            '0x8a4bC2349335b7D6a5d2f7A3b9': {
                'name': 'Institutional Trader',
                'positions': [{
                    'symbol': 'BTC/USDC', 
                    'side': 'short',
                    'size': 850000,
                    'entryPrice': 42500,
                    'markPrice': 42050,
                    'liqPrice': 45200,
                    'leverage': 3.8,
                    'unrealizedPnl': -8500,
                    'margin': 223684
                }],
                'geo': {'region': 'Europe', 'country': 'UK'},
                'last_updated': datetime.now()
            },
            '0x3cBdF0D8f7C4a5b0eE2d7a3c1': {
                'name': 'DeFi Giant',
                'positions': [
                    {
                        'symbol': 'SOL/USDC',
                        'side': 'long', 
                        'size': 75000,
                        'entryPrice': 98.50,
                        'markPrice': 102.25,
                        'liqPrice': 75.00,
                        'leverage': 4.5,
                        'unrealizedPnl': 2812,
                        'margin': 16667
                    },
                    {
                        'symbol': 'ARB/USDC',
                        'side': 'long',
                        'size': 45000,
                        'entryPrice': 1.85,
                        'markPrice': 1.92,
                        'liqPrice': 1.45,
                        'leverage': 6.2,
                        'unrealizedPnl': 1701,
                        'margin': 7258
                    }
                ],
                'geo': {'region': 'Asia', 'country': 'SG'},
                'last_updated': datetime.now()
            }
        }
        
        return demo_whales
        
    except Exception as e:
        st.error(f"Error fetching whale data: {e}")
        return {}

def display_whale_dashboard(whale_data=None):
    """Display the main whale tracking dashboard"""
    if whale_data is None:
        whale_data = get_whale_data()
    
    # Show warning if using demo data
    if not whale_data:
        st.warning("No whale data available. Using demo data.")
        whale_data = get_whale_data()  # Get demo data
    
    # Dashboard header
    st.write(f"**📊 Tracking {len(whale_data)} active whales**")
    
    # Summary metrics
    total_positions = sum(len(data['positions']) for data in whale_data.values())
    total_value = sum(pos['size'] for data in whale_data.values() for pos in data['positions'])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Active Whales", len(whale_data))
    with col2:
        st.metric("Total Positions", total_positions)
    with col3:
        st.metric("Total Value", f"${total_value:,.0f}")
    
    st.markdown("---")
    
    # Display whale cards
    for wallet, data in whale_data.items():
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.subheader(f"🐋 {data['name']}")
                st.write(f"**Wallet:** `{wallet[:12]}...{wallet[-6:]}`")
                st.write(f"**Region:** {data['geo'].get('region', 'Unknown')}")
                st.write(f"**Last Updated:** {data['last_updated'].strftime('%Y-%m-%d %H:%M:%S')}")
            
            with col2:
                if data['positions']:
                    total_whale_value = sum(pos['size'] for pos in data['positions'])
                    total_whale_pnl = sum(pos['unrealizedPnl'] for pos in data['positions'])
                    pnl_delta = f"${total_whale_pnl:+,.0f} PnL"
                    st.metric(
                        label="Total Exposure",
                        value=f"${total_whale_value:,.0f}",
                        delta=pnl_delta
                    )
                else:
                    st.info("No active positions")
            
            # Show all positions with expanders
            if data['positions']:
                for i, position in enumerate(data['positions']):
                    # Use a unique key for each expander
                    with st.expander(f"📈 {position['symbol']} - {position['side'].upper()} (${position['size']:,.0f})", key=f"{wallet}_{i}"):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.write("**💰 Position Details**")
                            st.write(f"**Size:** ${position['size']:,.0f}")
                            st.write(f"**Entry Price:** ${position['entryPrice']:,.2f}")
                            st.write(f"**Mark Price:** ${position['markPrice']:,.2f}")
                            st.write(f"**Liquidation:** ${position['liqPrice']:,.2f}")
                        
                        with col2:
                            st.write("**⚡ Risk Metrics**")
                            st.write(f"**Leverage:** {position['leverage']}x")
                            st.write(f"**Margin:** ${position['margin']:,.0f}")
                            
                            # Distance to liquidation
                            if position['side'] == 'long':
                                liq_distance = ((position['markPrice'] - position['liqPrice']) / position['markPrice']) * 100
                            else:
                                liq_distance = ((position['liqPrice'] - position['markPrice']) / position['markPrice']) * 100
                            
                            st.write(f"**Liq Distance:** {liq_distance:.1f}%")
                        
                        with col3:
                            st.write("**📊 Performance**")
                            pnl_color = "green" if position['unrealizedPnl'] >= 0 else "red"
                            st.write(f"**Unrealized PnL:** :{pnl_color}[${position['unrealizedPnl']:+,.0f}]")
                            
                            # Calculate PnL percentage
                            pnl_percent = calculate_pnl_percent(position['unrealizedPnl'], position['size'])
                            st.write(f"**PnL %:** :{pnl_color}[{pnl_percent:+.1f}%]")
                            
                            # Position status
                            if abs(pnl_percent) > 20:
                                status = "🔥 High Volatility"
                            elif abs(pnl_percent) > 10:
                                status = "⚡ Active"
                            else:
                                status = "✅ Stable"
                            st.write(f"**Status:** {status}")
            
            st.markdown("---")
