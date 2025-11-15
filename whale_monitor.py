import streamlit as st
import pandas as pd
from datetime import datetime

def get_whale_data():
    """Fetch whale data - using stable demo data"""
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
                }
            ],
            'geo': {'region': 'Asia', 'country': 'SG'},
            'last_updated': datetime.now()
        }
    }
    
    return demo_whales

def display_whale_dashboard(whale_data=None):
    """Display the main whale tracking dashboard"""
    if whale_data is None:
        whale_data = get_whale_data()
    
    # Dashboard header
    st.write(f"**📊 Tracking {len(whale_data)} active whales**")
    
    # Summary metrics
    total_positions = sum(len(data['positions']) for data in whale_data.values())
    total_value = sum(pos['size'] for data in whale_data.values() for pos in data['positions'])
    total_pnl = sum(pos['unrealizedPnl'] for data in whale_data.values() for pos in data['positions'])
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Active Whales", len(whale_data))
    with col2:
        st.metric("Total Positions", total_positions)
    with col3:
        st.metric("Total Value", f"${total_value:,.0f}")
    with col4:
        st.metric("Total PnL", f"${total_pnl:+,.0f}")
    
    st.markdown("---")
    
    # Display whale cards - SIMPLIFIED without expanders
    for wallet, data in whale_data.items():
        with st.container():
            # Whale header
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
            
            # Show positions as cards instead of expanders
            if data['positions']:
                st.write("**Active Positions:**")
                
                for position in data['positions']:
                    # Create a card for each position
                    with st.container():
                        st.markdown("---")
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.write(f"**{position['symbol']}**")
                            st.write(f"**Side:** {position['side'].upper()}")
                            st.write(f"**Size:** ${position['size']:,.0f}")
                            st.write(f"**Leverage:** {position['leverage']}x")
                        
                        with col2:
                            st.write("**Prices**")
                            st.write(f"Entry: ${position['entryPrice']:,.2f}")
                            st.write(f"Mark: ${position['markPrice']:,.2f}")
                            st.write(f"Liq: ${position['liqPrice']:,.2f}")
                        
                        with col3:
                            st.write("**Performance**")
                            pnl_color = "🟢" if position['unrealizedPnl'] >= 0 else "🔴"
                            st.write(f"PnL: {pnl_color} ${position['unrealizedPnl']:+,.0f}")
                            st.write(f"Margin: ${position['margin']:,.0f}")
                            
                            # Simple status indicator
                            if position['unrealizedPnl'] > 0:
                                status = "✅ Profitable"
                            else:
                                status = "⚠️ Down"
                            st.write(f"Status: {status}")
            
            st.markdown("<br>", unsafe_allow_html=True)
