import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
from config import WHALE_ADDRESSES, WHALE_GEO_DATA, ALERT_THRESHOLDS

def get_hyperliquid_user_state(wallet_address):
    """
    Fetch user state from Hyperliquid API
    """
    try:
        url = "https://api.hyperliquid.xyz/info"
        payload = {
            "type": "userState",
            "user": wallet_address
        }
        
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error for {wallet_address}: {response.status_code}")
            return None
            
    except Exception as e:
        st.error(f"Error fetching data for {wallet_address}: {e}")
        return None

def parse_hyperliquid_positions(user_state, wallet_address):
    """
    Parse Hyperliquid API response into standardized position format
    """
    positions = []
    
    try:
        if user_state and 'assetPositions' in user_state:
            for position in user_state['assetPositions']:
                position_data = position.get('position', {})
                
                # Extract position details
                symbol = position_data.get('coin', 'Unknown')
                size = float(position_data.get('szi', 0))
                entry_price = float(position_data.get('entryPx', 0))
                
                # Calculate market value (simplified)
                mark_price = get_market_price(symbol)
                
                if size != 0 and entry_price != 0:
                    side = "long" if size > 0 else "short"
                    leverage = calculate_leverage(position_data)
                    unrealized_pnl = calculate_unrealized_pnl(position_data, mark_price)
                    liq_price = calculate_liquidation_price(position_data)
                    margin = calculate_margin(position_data)
                    
                    positions.append({
                        'symbol': f"{symbol}/USD",
                        'side': side,
                        'size': abs(size) * mark_price,  # Convert to USD value
                        'entryPrice': entry_price,
                        'markPrice': mark_price,
                        'liqPrice': liq_price,
                        'leverage': leverage,
                        'unrealizedPnl': unrealized_pnl,
                        'margin': margin,
                        'raw_data': position_data
                    })
        
        return positions
        
    except Exception as e:
        st.error(f"Error parsing positions for {wallet_address}: {e}")
        return []

def get_market_price(symbol):
    """
    Get current market price for a symbol
    TODO: Implement real price fetching from Hyperliquid
    """
    # Mock prices - replace with real API call
    price_map = {
        'ETH': 2550.75,
        'BTC': 42050.00,
        'SOL': 102.25,
        'ARB': 1.92,
        'BNB': 325.50
    }
    return price_map.get(symbol, 100.0)

def calculate_leverage(position_data):
    """
    Calculate leverage from position data
    """
    try:
        size = abs(float(position_data.get('szi', 0)))
        entry_price = float(position_data.get('entryPx', 1))
        margin_used = float(position_data.get('marginUsed', 0))
        
        if margin_used > 0:
            return (size * entry_price) / margin_used
        return 1.0
    except:
        return 1.0

def calculate_unrealized_pnl(position_data, mark_price):
    """
    Calculate unrealized P&L
    """
    try:
        size = float(position_data.get('szi', 0))
        entry_price = float(position_data.get('entryPx', 0))
        
        if size > 0:  # Long
            return size * (mark_price - entry_price)
        else:  # Short
            return abs(size) * (entry_price - mark_price)
    except:
        return 0.0

def calculate_liquidation_price(position_data):
    """
    Calculate liquidation price
    Simplified calculation - replace with actual Hyperliquid formula
    """
    try:
        entry_price = float(position_data.get('entryPx', 0))
        leverage = calculate_leverage(position_data)
        
        if leverage > 1:
            # Simplified liquidation price calculation
            if position_data.get('szi', 0) > 0:  # Long
                return entry_price * (1 - 1/leverage)
            else:  # Short
                return entry_price * (1 + 1/leverage)
        return 0.0
    except:
        return 0.0

def calculate_margin(position_data):
    """
    Calculate margin used
    """
    try:
        return float(position_data.get('marginUsed', 0))
    except:
        return 0.0

def get_live_whale_data():
    """
    Fetch live whale data from Hyperliquid API
    """
    whale_data = {}
    
    st.info("🔄 Fetching live data from Hyperliquid...")
    
    for wallet, whale_name in WHALE_ADDRESSES.items():
        try:
            # Get user state from Hyperliquid
            user_state = get_hyperliquid_user_state(wallet)
            
            if user_state:
                # Parse positions
                positions = parse_hyperliquid_positions(user_state, wallet)
                
                whale_data[wallet] = {
                    'name': whale_name,
                    'positions': positions,
                    'geo': WHALE_GEO_DATA.get(wallet, {}),
                    'last_updated': datetime.now(),
                    'total_balance': float(user_state.get('marginSummary', {}).get('accountValue', 0)),
                    'free_collateral': float(user_state.get('marginSummary', {}).get('freeCollateral', 0))
                }
                
                st.success(f"✅ Live data for {whale_name}")
            else:
                # Fallback to demo data if API fails
                whale_data[wallet] = get_demo_whale_data(wallet, whale_name)
                st.warning(f"⚠️ Using demo data for {whale_name}")
                
        except Exception as e:
            st.error(f"❌ Error processing {whale_name}: {e}")
            # Fallback to demo data
            whale_data[wallet] = get_demo_whale_data(wallet, whale_name)
    
    return whale_data

def get_demo_whale_data(wallet, name):
    """
    Fallback demo data when live API is unavailable
    """
    demo_positions = {
        "0x742d35Cc6634C0532925a3b8D": [{
            'symbol': 'ETH/USD',
            'side': 'long',
            'size': 125000,
            'entryPrice': 2450.50,
            'markPrice': 2550.75,
            'liqPrice': 1950.25,
            'leverage': 5.2,
            'unrealizedPnl': 12500,
            'margin': 24038
        }],
        "0x8a4bC2349335b7D6a5d2f7A3b9": [{
            'symbol': 'BTC/USD', 
            'side': 'short',
            'size': 850000,
            'entryPrice': 42500,
            'markPrice': 42050,
            'liqPrice': 45200,
            'leverage': 3.8,
            'unrealizedPnl': -8500,
            'margin': 223684
        }],
        "0x3cBdF0D8f7C4a5b0eE2d7a3c1": [{
            'symbol': 'SOL/USD',
            'side': 'long', 
            'size': 75000,
            'entryPrice': 98.50,
            'markPrice': 102.25,
            'liqPrice': 75.00,
            'leverage': 4.5,
            'unrealizedPnl': 2812,
            'margin': 16667
        }]
    }
    
    return {
        'name': name,
        'positions': demo_positions.get(wallet, []),
        'geo': WHALE_GEO_DATA.get(wallet, {}),
        'last_updated': datetime.now(),
        'total_balance': 1000000,
        'free_collateral': 50000
    }

def display_whale_dashboard(use_demo_data=False):
    """
    Display the main whale tracking dashboard with live data
    """
    # Fetch data
    if use_demo_data:
        whale_data = {}
        for wallet, name in WHALE_ADDRESSES.items():
            whale_data[wallet] = get_demo_whale_data(wallet, name)
        st.warning("📊 Using demo data for display")
    else:
        whale_data = get_live_whale_data()
    
    if not whale_data:
        st.error("❌ No whale data available")
        return
    
    # Calculate summary metrics
    total_whales = len(whale_data)
    total_positions = sum(len(data['positions']) for data in whale_data.values())
    total_value = sum(pos['size'] for data in whale_data.values() for pos in data['positions'])
    total_pnl = sum(pos['unrealizedPnl'] for data in whale_data.values() for pos in data['positions'])
    
    # Display summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Active Whales", total_whales)
    with col2:
        st.metric("Total Positions", total_positions)
    with col3:
        st.metric("Total Exposure", f"${total_value:,.0f}")
    with col4:
        st.metric("Total PnL", f"${total_pnl:+,.0f}")
    
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
                if 'total_balance' in data:
                    st.write(f"**Total Balance:** ${data['total_balance']:,.0f}")
            
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
            
            # Display positions
            if data['positions']:
                st.write("**Active Positions:**")
                
                for position in data['positions']:
                    with st.container():
                        st.markdown("<div class='position-card'>", unsafe_allow_html=True)
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.write(f"**{position['symbol']}**")
                            st.write(f"**Side:** {position['side'].upper()}")
                            st.write(f"**Size:** ${position['size']:,.0f}")
                            st.write(f"**Leverage:** {position['leverage']}x")
                        
                        with col2:
                            st.write("**💰 Prices**")
                            st.write(f"Entry: ${position['entryPrice']:,.2f}")
                            st.write(f"Mark: ${position['markPrice']:,.2f}")
                            st.write(f"Liq: ${position['liqPrice']:,.2f}")
                        
                        with col3:
                            st.write("**📊 Performance**")
                            pnl_class = "positive-pnl" if position['unrealizedPnl'] >= 0 else "negative-pnl"
                            st.markdown(f"**PnL:** <span class='{pnl_class}'>${position['unrealizedPnl']:+,.0f}</span>", unsafe_allow_html=True)
                            st.write(f"**Margin:** ${position['margin']:,.0f}")
                            
                            # Risk assessment
                            if position['leverage'] > ALERT_THRESHOLDS['high_leverage']:
                                status = "🚨 High Risk"
                            elif position['unrealizedPnl'] < -ALERT_THRESHOLDS['pnl_alert']:
                                status = "⚠️ Large Loss"
                            else:
                                status = "✅ Normal"
                            st.write(f"**Status:** {status}")
                        
                        st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
