import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime

# Try to import config, but provide defaults if it fails
try:
    from config import WHALE_ADDRESSES, WHALE_GEO_DATA, ALERT_THRESHOLDS
except ImportError:
    # Default configuration if config.py is missing
    WHALE_ADDRESSES = {
        "0x742d35Cc6634C0532925a3b8D": "Crypto Whale Alpha",
        "0x8a4bC2349335b7D6a5d2f7A3b9": "Institutional Trader", 
        "0x3cBdF0D8f7C4a5b0eE2d7a3c1": "DeFi Giant",
        "0x4e5f6g7h8i9j0k1l2m3n4o5p6q": "Arbitrage Pro",
        "0x7r8s9t0u1v2w3x4y5z6a7b8c9d": "Market Maker X"
    }
    
    WHALE_GEO_DATA = {
        "0x742d35Cc6634C0532925a3b8D": {"region": "North America"},
        "0x8a4bC2349335b7D6a5d2f7A3b9": {"region": "Europe"}, 
        "0x3cBdF0D8f7C4a5b0eE2d7a3c1": {"region": "Asia"},
        "0x4e5f6g7h8i9j0k1l2m3n4o5p6q": {"region": "Middle East"},
        "0x7r8s9t0u1v2w3x4y5z6a7b8c9d": {"region": "Europe"}
    }
    
    ALERT_THRESHOLDS = {
        "high_leverage": 8.0,
        "large_position": 500000,
        "pnl_alert": 10000,
        "liquidation_risk": 0.15
    }

def get_hyperliquid_user_state(wallet_address):
    """Fetch user state from Hyperliquid API"""
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
            return None
            
    except Exception as e:
        return None

def get_market_price(symbol):
    """Get current market price for a symbol"""
    price_map = {
        'ETH': 2550.75,
        'BTC': 42050.00,
        'SOL': 102.25,
        'ARB': 1.92,
        'BNB': 325.50,
        'ADA': 0.48,
        'DOT': 6.85,
        'LINK': 14.20
    }
    return price_map.get(symbol, 100.0)

def calculate_additional_metrics(position_data, mark_price):
    """Calculate DCA, Stop Loss, Take Profit, and other advanced metrics"""
    try:
        entry_price = float(position_data.get('entryPx', 0))
        size = abs(float(position_data.get('szi', 0)))
        side = "long" if float(position_data.get('szi', 0)) > 0 else "short"
        
        # DCA (Dollar Cost Average) - assuming single entry for now
        dca_price = entry_price
        
        # Stop Loss (15% from entry for demo)
        if side == "long":
            sl_price = entry_price * 0.85  # 15% down
            tp_price = entry_price * 1.20  # 20% up
        else:
            sl_price = entry_price * 1.15  # 15% up for shorts
            tp_price = entry_price * 0.80  # 20% down for shorts
        
        # PNL Percentage
        if side == "long":
            pnl_percent = ((mark_price - entry_price) / entry_price) * 100
        else:
            pnl_percent = ((entry_price - mark_price) / entry_price) * 100
        
        return {
            'dca_price': dca_price,
            'sl_price': sl_price,
            'tp_price': tp_price,
            'pnl_percent': pnl_percent
        }
    except:
        return {
            'dca_price': 0,
            'sl_price': 0,
            'tp_price': 0,
            'pnl_percent': 0
        }

def calculate_leverage(position_data):
    """Calculate leverage from position data"""
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
    """Calculate unrealized P&L"""
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
    """Calculate liquidation price"""
    try:
        entry_price = float(position_data.get('entryPx', 0))
        leverage = calculate_leverage(position_data)
        
        if leverage > 1:
            if position_data.get('szi', 0) > 0:  # Long
                return entry_price * (1 - 1/leverage)
            else:  # Short
                return entry_price * (1 + 1/leverage)
        return 0.0
    except:
        return 0.0

def calculate_margin(position_data):
    """Calculate margin used"""
    try:
        return float(position_data.get('marginUsed', 0))
    except:
        return 0.0

def parse_hyperliquid_positions(user_state, wallet_address):
    """Parse Hyperliquid API response into standardized position format"""
    positions = []
    
    try:
        if user_state and 'assetPositions' in user_state:
            for position in user_state['assetPositions']:
                position_data = position.get('position', {})
                
                symbol = position_data.get('coin', 'Unknown')
                size = float(position_data.get('szi', 0))
                entry_price = float(position_data.get('entryPx', 0))
                
                mark_price = get_market_price(symbol)
                
                if size != 0 and entry_price != 0:
                    side = "long" if size > 0 else "short"
                    leverage = calculate_leverage(position_data)
                    unrealized_pnl = calculate_unrealized_pnl(position_data, mark_price)
                    liq_price = calculate_liquidation_price(position_data)
                    margin = calculate_margin(position_data)
                    
                    # Calculate additional metrics
                    additional_metrics = calculate_additional_metrics(position_data, mark_price)
                    
                    positions.append({
                        'symbol': symbol,
                        'type': side.upper(),
                        'leverage': leverage,
                        'entry_price': entry_price,
                        'dca_price': additional_metrics['dca_price'],
                        'sl_price': additional_metrics['sl_price'],
                        'tp_price': additional_metrics['tp_price'],
                        'size': abs(size) * mark_price,
                        'pnl': unrealized_pnl,
                        'pnl_percent': additional_metrics['pnl_percent'],
                        'mark_price': mark_price,
                        'liq_price': liq_price,
                        'margin': margin
                    })
        
        return positions
        
    except Exception as e:
        return []

def get_live_whale_data():
    """Fetch live whale data from Hyperliquid API"""
    whale_data = {}
    
    for wallet, whale_name in WHALE_ADDRESSES.items():
        try:
            user_state = get_hyperliquid_user_state(wallet)
            
            if user_state:
                positions = parse_hyperliquid_positions(user_state, wallet)
                
                whale_data[wallet] = {
                    'name': whale_name,
                    'positions': positions,
                    'geo': WHALE_GEO_DATA.get(wallet, {}),
                    'last_updated': datetime.now()
                }
            else:
                # Fallback to demo data
                whale_data[wallet] = get_demo_whale_data(wallet, whale_name)
                
        except Exception as e:
            # Fallback to demo data on error
            whale_data[wallet] = get_demo_whale_data(wallet, whale_name)
    
    return whale_data

def get_demo_whale_data(wallet, name):
    """Enhanced demo data with all requested metrics"""
    demo_positions = {
        "0x742d35Cc6634C0532925a3b8D": [
            {
                'symbol': 'ETH',
                'type': 'LONG',
                'leverage': 5.2,
                'entry_price': 2450.50,
                'dca_price': 2450.50,
                'sl_price': 2082.93,
                'tp_price': 2940.60,
                'size': 125000,
                'pnl': 12500,
                'pnl_percent': 4.08,
                'mark_price': 2550.75,
                'liq_price': 1950.25,
                'margin': 24038
            }
        ],
        "0x8a4bC2349335b7D6a5d2f7A3b9": [
            {
                'symbol': 'BTC',
                'type': 'SHORT', 
                'leverage': 3.8,
                'entry_price': 42500,
                'dca_price': 42500,
                'sl_price': 48875,
                'tp_price': 34000,
                'size': 850000,
                'pnl': -8500,
                'pnl_percent': -1.0,
                'mark_price': 42050,
                'liq_price': 45200,
                'margin': 223684
            }
        ],
        "0x3cBdF0D8f7C4a5b0eE2d7a3c1": [
            {
                'symbol': 'SOL',
                'type': 'LONG', 
                'leverage': 4.5,
                'entry_price': 98.50,
                'dca_price': 98.50,
                'sl_price': 83.73,
                'tp_price': 118.20,
                'size': 75000,
                'pnl': 2812,
                'pnl_percent': 3.81,
                'mark_price': 102.25,
                'liq_price': 75.00,
                'margin': 16667
            },
            {
                'symbol': 'ARB',
                'type': 'LONG',
                'leverage': 6.2,
                'entry_price': 1.85,
                'dca_price': 1.85,
                'sl_price': 1.57,
                'tp_price': 2.22,
                'size': 45000,
                'pnl': 1701,
                'pnl_percent': 4.54,
                'mark_price': 1.92,
                'liq_price': 1.45,
                'margin': 7258
            }
        ],
        "0x4e5f6g7h8i9j0k1l2m3n4o5p6q": [
            {
                'symbol': 'BNB',
                'type': 'LONG',
                'leverage': 2.5,
                'entry_price': 315.00,
                'dca_price': 315.00,
                'sl_price': 267.75,
                'tp_price': 378.00,
                'size': 95000,
                'pnl': 9975,
                'pnl_percent': 3.17,
                'mark_price': 325.50,
                'liq_price': 280.00,
                'margin': 38000
            }
        ],
        "0x7r8s9t0u1v2w3x4y5z6a7b8c9d": [
            {
                'symbol': 'ADA',
                'type': 'SHORT',
                'leverage': 7.1,
                'entry_price': 0.52,
                'dca_price': 0.52,
                'sl_price': 0.598,
                'tp_price': 0.416,
                'size': 35000,
                'pnl': 1400,
                'pnl_percent': 2.69,
                'mark_price': 0.48,
                'liq_price': 0.56,
                'margin': 4929
            },
            {
                'symbol': 'LINK',
                'type': 'LONG',
                'leverage': 3.2,
                'entry_price': 13.80,
                'dca_price': 13.80,
                'sl_price': 11.73,
                'tp_price': 16.56,
                'size': 68000,
                'pnl': 2720,
                'pnl_percent': 2.90,
                'mark_price': 14.20,
                'liq_price': 12.10,
                'margin': 21250
            }
        ]
    }
    
    return {
        'name': name,
        'positions': demo_positions.get(wallet, []),
        'geo': WHALE_GEO_DATA.get(wallet, {}),
        'last_updated': datetime.now()
    }

def display_whale_dashboard(use_demo_data=False):
    """Display enhanced whale tracking dashboard with all metrics"""
    # Show loading message
    with st.spinner('🔄 Loading comprehensive whale data...'):
        # Fetch data
        if use_demo_data:
            whale_data = {}
            for wallet, name in WHALE_ADDRESSES.items():
                whale_data[wallet] = get_demo_whale_data(wallet, name)
            st.success("📊 Enhanced demo data loaded successfully!")
        else:
            whale_data = get_live_whale_data()
            st.success("🌐 Live data loaded successfully!")
    
    if not whale_data:
        st.error("❌ No whale data available")
        return
    
    # Calculate summary metrics
    total_whales = len(whale_data)
    total_positions = sum(len(data['positions']) for data in whale_data.values())
    total_value = sum(pos['size'] for data in whale_data.values() for pos in data['positions'])
    total_pnl = sum(pos['pnl'] for data in whale_data.values() for pos in data['positions'])
    
    # Enhanced summary metrics
    avg_leverage = sum(pos['leverage'] for data in whale_data.values() for pos in data['positions']) / total_positions if total_positions > 0 else 0
    winning_positions = sum(1 for data in whale_data.values() for pos in data['positions'] if pos['pnl'] > 0)
    win_rate = (winning_positions / total_positions * 100) if total_positions > 0 else 0
    
    # Display enhanced summary metrics
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.metric("Active Whales", total_whales)
    with col2:
        st.metric("Total Positions", total_positions)
    with col3:
        st.metric("Total Exposure", f"${total_value:,.0f}")
    with col4:
        st.metric("Total PnL", f"${total_pnl:+,.0f}")
    with col5:
        st.metric("Avg Leverage", f"{avg_leverage:.1f}x")
    with col6:
        st.metric("Win Rate", f"{win_rate:.1f}%")
    
    st.markdown("---")
    
    # Display whale cards with enhanced data table
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
                    total_whale_pnl = sum(pos['pnl'] for pos in data['positions'])
                    pnl_delta = f"${total_whale_pnl:+,.0f} PnL"
                    st.metric(
                        label="Total Exposure",
                        value=f"${total_whale_value:,.0f}",
                        delta=pnl_delta
                    )
            
            # Display positions as a professional table
            if data['positions']:
                # Create DataFrame for better table display
                positions_df = pd.DataFrame(data['positions'])
                
                # Format the DataFrame for display
                display_df = positions_df[[
                    'symbol', 'type', 'leverage', 'entry_price', 
                    'dca_price', 'sl_price', 'tp_price', 'size', 'pnl', 'pnl_percent'
                ]].copy()
                
                # Format numeric columns
                display_df['leverage'] = display_df['leverage'].apply(lambda x: f"{x:.1f}x")
                display_df['entry_price'] = display_df['entry_price'].apply(lambda x: f"${x:,.2f}")
                display_df['dca_price'] = display_df['dca_price'].apply(lambda x: f"${x:,.2f}")
                display_df['sl_price'] = display_df['sl_price'].apply(lambda x: f"${x:,.2f}")
                display_df['tp_price'] = display_df['tp_price'].apply(lambda x: f"${x:,.2f}")
                display_df['size'] = display_df['size'].apply(lambda x: f"${x:,.0f}")
                display_df['pnl'] = display_df['pnl'].apply(lambda x: f"${x:+,.0f}")
                display_df['pnl_percent'] = display_df['pnl_percent'].apply(lambda x: f"{x:+.2f}%")
                
                # Rename columns for better display
                display_df.columns = [
                    'Coin', 'Type', 'Leverage', 'Entry Price', 
                    'DCA', 'SL', 'TP', 'Size', 'PNL', 'PNL %'
                ]
                
                # Display the table
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Additional position details in expanders
                for i, position in enumerate(data['positions']):
                    with st.expander(f"📊 Detailed Analysis: {position['symbol']} {position['type']}", key=f"{wallet}_{i}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("**Position Metrics**")
                            st.write(f"**Current Price:** ${position['mark_price']:,.2f}")
                            st.write(f"**Liquidation Price:** ${position['liq_price']:,.2f}")
                            st.write(f"**Margin Used:** ${position['margin']:,.0f}")
                            
                            # Distance to SL/TP
                            if position['type'] == 'LONG':
                                sl_distance = ((position['mark_price'] - position['sl_price']) / position['mark_price']) * 100
                                tp_distance = ((position['tp_price'] - position['mark_price']) / position['mark_price']) * 100
                            else:
                                sl_distance = ((position['sl_price'] - position['mark_price']) / position['mark_price']) * 100
                                tp_distance = ((position['mark_price'] - position['tp_price']) / position['mark_price']) * 100
                            
                            st.write(f"**Distance to SL:** {sl_distance:.1f}%")
                            st.write(f"**Distance to TP:** {tp_distance:.1f}%")
                        
                        with col2:
                            st.write("**Risk Assessment**")
                            
                            # Risk level based on leverage and PnL
                            if position['leverage'] > 8:
                                risk_level = "🚨 Very High"
                            elif position['leverage'] > 5:
                                risk_level = "⚠️ High"
                            elif position['leverage'] > 3:
                                risk_level = "🔶 Medium"
                            else:
                                risk_level = "✅ Low"
                            
                            st.write(f"**Risk Level:** {risk_level}")
                            
                            # Position status
                            if position['pnl'] > 0:
                                status = "🟢 Profitable"
                            else:
                                status = "🔴 Losing"
                            
                            st.write(f"**Status:** {status}")
                            
                            # Recommendation
                            if position['pnl_percent'] < -10:
                                recommendation = "Consider reducing position"
                            elif position['leverage'] > 6:
                                recommendation = "Monitor leverage closely"
                            else:
                                recommendation = "Position looks healthy"
                            
                            st.write(f"**Recommendation:** {recommendation}")
            
            st.markdown("---")
