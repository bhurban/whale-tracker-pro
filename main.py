import streamlit as st
import traceback
import pandas as pd
import plotly.express as px
import time
from datetime import datetime
import sys
import os
from dotenv import load_dotenv
import sqlite3

try:
    # Your existing main.py code here
    from whale_monitor import display_whale_dashboard
    st.set_page_config(page_title="Whale Tracker Pro", layout="wide")
    display_whale_dashboard()
    
except Exception as e:
    st.set_page_config(page_title="Whale Tracker Pro", layout="wide")
    st.error("🚨 Application Error")
    st.code(traceback.format_exc())
    
load_dotenv()


# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import your custom modules
from config import WHALE_ADDRESSES, EMAIL_CONFIG
from whale_monitor import get_whale_data, display_whale_dashboard
from cross_exchange_tracker import CrossExchangeTracker
from leverage_monitor import LeverageMonitor
from email_alerts import send_email_alert, check_for_alerts, should_send_alert

# In main.py, add error handling
try:
    from whale_monitor import get_whale_data, display_whale_dashboard
    from database_manager import DatabaseManager
    # ... other imports
except ImportError as e:
    import streamlit as st
    st.error(f"Import error: {e}")


# Use get() with defaults instead of direct os.environ[]
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
API_KEY = os.getenv('HYPERLIQUID_API_KEY', '')



# Database Manager Class
class WhaleDatabase:
    def __init__(self, db_path='whale_analytics.db'):
        self.db_path = db_path
        self.setup_database()
    
    def setup_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Whale positions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS whale_positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                whale_name TEXT,
                coin TEXT,
                position_type TEXT,
                value REAL,
                leverage REAL,
                pnl REAL,
                pnl_percent REAL,
                entry_price REAL,
                size REAL
            )
        ''')
        
        # Alert history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alert_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                alert_type TEXT,
                whale_name TEXT,
                coin TEXT,
                message TEXT,
                urgency TEXT
            )
        ''')
        
        # Performance metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                total_portfolio_value REAL,
                active_whales INTEGER,
                total_positions INTEGER,
                net_pnl REAL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def log_whale_position(self, whale_data):
        """Log current whale positions to database"""
        conn = sqlite3.connect(self.db_path)
        
        for whale_name, data in whale_data.items():
            for position in data.get('positions', []):
                conn.execute('''
                    INSERT INTO whale_positions 
                    (whale_name, coin, position_type, value, leverage, pnl, pnl_percent, entry_price, size)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    whale_name,
                    position['Coin'],
                    position['Type'],
                    position['Value'],
                    position['Leverage'],
                    position['P&L'],
                    position['P&L %'],
                    position['Entry Price'],
                    position['Size']
                ))
        
        conn.commit()
        conn.close()
    
    def log_alert(self, alert_data):
        """Log alert to database"""
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            INSERT INTO alert_history (alert_type, whale_name, coin, message, urgency)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            alert_data.get('type'),
            alert_data.get('whale'),
            alert_data.get('coin', 'N/A'),
            alert_data.get('message'),
            alert_data.get('urgency', 'MEDIUM')
        ))
        conn.commit()
        conn.close()
    
    def get_historical_data(self, days=7):
        """Get historical data for analytics"""
        conn = sqlite3.connect(self.db_path)
        
        # Get whale position history
        positions_df = pd.read_sql('''
            SELECT * FROM whale_positions 
            WHERE timestamp >= datetime('now', '-{} days')
            ORDER BY timestamp DESC
        '''.format(days), conn)
        
        # Get alert history
        alerts_df = pd.read_sql('''
            SELECT * FROM alert_history 
            WHERE timestamp >= datetime('now', '-{} days')
            ORDER BY timestamp DESC
        '''.format(days), conn)
        
        conn.close()
        return positions_df, alerts_df

# Initialize session state
def init_session_state():
    if 'previous_whale_data' not in st.session_state:
        st.session_state.previous_whale_data = {}
    if 'email_alerts_enabled' not in st.session_state:
        st.session_state.email_alerts_enabled = True
    if 'sent_alerts' not in st.session_state:
        st.session_state.sent_alerts = []
    if 'leverage_monitor' not in st.session_state:
        st.session_state.leverage_monitor = LeverageMonitor()
    if 'cross_exchange_tracker' not in st.session_state:
        st.session_state.cross_exchange_tracker = CrossExchangeTracker()
    if 'alert_cooldowns' not in st.session_state:
        st.session_state.alert_cooldowns = {}
    if 'whale_database' not in st.session_state:
        st.session_state.whale_database = WhaleDatabase()

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        border-left: 4px solid #1E88E5;
    }
    .positive-pnl { color: #00C853; font-weight: bold; }
    .negative-pnl { color: #FF1744; font-weight: bold; }
    .whale-section { background: white; padding: 1.5rem; border-radius: 10px; border: 1px solid #e0e0e0; margin-bottom: 1rem; }
    .cooldown-active { background: #FFF3CD; padding: 0.5rem; border-radius: 5px; border-left: 4px solid #FFC107; }
    .debug-section { background: #f8f9fa; padding: 1rem; border-radius: 10px; border: 1px solid #dee2e6; margin-bottom: 1rem; }
</style>
""", unsafe_allow_html=True)

def main():
    st.set_page_config(
        page_title="🐋 Advanced Hyperliquid Whale Tracker",
        page_icon="🐋",
        layout="wide"
    )
    
    # Initialize session state FIRST
    init_session_state()
    
    # Header
    st.markdown('<div class="main-header">🐋 Advanced Hyperliquid Whale Tracker</div>', unsafe_allow_html=True)
    st.markdown("### 🌐 Cross-Exchange Tracking + ⚡ Leverage Intelligence + 📧 Smart Alerts")
    
    # Refresh Controls
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.info("🔄 Live Hyperliquid API + 🌐 Cross-Exchange Tracking + ⚡ Leverage Intelligence")
    with col2:
        refresh_rate = st.selectbox("Refresh Rate", [30, 60, 120], index=0)
    with col3:
        if st.button("🔄 Refresh Now"):
            st.rerun()
    
    # Fetch Live Data FIRST (so whale_data is defined)
    with st.spinner("🦁 Fetching live whale data from Hyperliquid..."):
        whale_data = get_whale_data()
    
    # Debug Controls (AFTER whale_data is defined)
    st.markdown("## 🔧 Debug & Testing Tools")
    
    debug_col1, debug_col2, debug_col3, debug_col4, debug_col5 = st.columns(5)
    
    with debug_col1:
        if st.button("🔄 Force Reset Alerts"):
            st.session_state.previous_whale_data = {}
            st.session_state.alert_cooldowns = {}
            st.session_state.sent_alerts = []
            st.success("✅ Alert history reset! Next refresh will detect ALL new positions.")
    
    with debug_col2:
        if st.button("📊 Debug Position Counts"):
            st.write("### Current Position Counts:")
            for whale_name, data in whale_data.items():
                st.write(f"**{whale_name}**: {data['position_count']} positions")
            if st.session_state.previous_whale_data:
                st.write("### Previous Position Counts:")
                for whale_name, data in st.session_state.previous_whale_data.items():
                    st.write(f"**{whale_name}**: {data.get('position_count', 0)} positions")
    
    with debug_col3:
        # EMERGENCY ZEC DETECTION FIX
        if st.button("🚨 Force ZEC Position Alert"):
            # Manually create a ZEC new position alert
            zec_position = None
            uk_whale_data = None
            
            # Find UK Whale data
            for whale_name, data in whale_data.items():
                if "UK Whale" in whale_name:
                    uk_whale_data = data
                    break
            
            if uk_whale_data:
                for position in uk_whale_data['positions']:
                    if position['Coin'] == 'ZEC':
                        zec_position = position
                        break
            
            if zec_position:
                alert_message = (
                    f"🆕 NEW POSITION OPENED!\n\n"
                    f"🐋 Whale: 👑 UK Whale\n"
                    f"💰 Coin: ZEC {zec_position['Type']}\n"
                    f"📊 Position Size: ${zec_position['Value']:,.2f}\n"
                    f"⚡ Leverage: {zec_position['Leverage_Display']}\n"
                    f"🎯 Entry Price: ${zec_position['Entry Price']:,.2f}\n"
                    f"📈 Size: {zec_position['Size']:,.0f} ZEC\n\n"
                    f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}"
                )
                
                if send_email_alert("Whale Alert - 👑 UK Whale", alert_message, False):
                    st.success("✅ Manual ZEC alert sent!")
                    st.session_state.sent_alerts.append({
                        'time': datetime.now().strftime('%H:%M:%S'),
                        'whale': '👑 UK Whale',
                        'type': 'NEW_POSITION',
                        'coin': 'ZEC',
                        'message': alert_message.split('\n')[0]
                    })
                    # Log to database
                    st.session_state.whale_database.log_alert({
                        'type': 'NEW_POSITION',
                        'whale': '👑 UK Whale',
                        'coin': 'ZEC',
                        'message': alert_message,
                        'urgency': 'MEDIUM'
                    })
            else:
                st.error("❌ ZEC position not found in current UK Whale data")
    
    with debug_col4:
        if st.button("🕒 Reset Position Timestamps"):
            # This will force the system to treat all current positions as "new"
            try:
                import email_alerts
                email_alerts.position_timestamps = {}
                st.success("✅ Position timestamps reset! All current positions will be treated as new.")
            except Exception as e:
                st.error(f"❌ Error resetting timestamps: {e}")
    
    with debug_col5:
        if st.button("📋 Show Timestamp Status"):
            try:
                import email_alerts
                if hasattr(email_alerts, 'position_timestamps') and email_alerts.position_timestamps:
                    st.write("### Current Position Timestamps:")
                    for whale_name, positions in email_alerts.position_timestamps.items():
                        st.write(f"**{whale_name}**: {len(positions)} positions tracked")
                        for coin, data in positions.items():
                            st.write(f"  - {coin}: first seen {datetime.fromtimestamp(data['first_seen']).strftime('%H:%M:%S')}")
                else:
                    st.info("No position timestamps tracked yet")
            except Exception as e:
                st.error(f"❌ Error showing timestamps: {e}")
    
    # Enhanced Alert System
    st.markdown("## 📧 Enhanced Alert System")
    
    alert_col1, alert_col2, alert_col3, alert_col4 = st.columns(4)
    with alert_col1:
        # Use the initialized session state value
        email_enabled = st.checkbox("Enable Email Alerts", value=st.session_state.email_alerts_enabled)
        st.session_state.email_alerts_enabled = email_enabled
    
    with alert_col2:
        if st.button("🧪 Test Email Alert"):
            test_message = "This is a test alert from your Advanced Hyperliquid Whale Tracker!"
            if send_email_alert("Test Alert", test_message):
                st.success("✅ Test email sent successfully!")
            else:
                st.error("❌ Failed to send test email")
    
    with alert_col3:
        st.metric("Recipients", len(EMAIL_CONFIG["RECEIVER_EMAILS"]))
    
    with alert_col4:
        active_cooldowns = len([k for k, v in st.session_state.alert_cooldowns.items() 
                               if time.time() - v < 3600])
        st.metric("⏳ Active Cooldowns", active_cooldowns)
    
    # Check for all alert types
    all_alerts = []
    
    # 1. Basic whale alerts
    basic_alerts = check_for_alerts(st.session_state.previous_whale_data, whale_data)
    all_alerts.extend(basic_alerts)
    
    # 2. Leverage alerts
    leverage_alerts = st.session_state.leverage_monitor.monitor_leverage_changes(whale_data)
    leverage_patterns = st.session_state.leverage_monitor.detect_leverage_patterns(whale_data)
    all_alerts.extend(leverage_alerts)
    all_alerts.extend(leverage_patterns)
    
    # 3. Cross-exchange alerts (sample for active whales)
    active_wallets = [data['wallet'] for data in whale_data.values() if data['total_value'] > 100000]
    if active_wallets:
        cross_exchange_alerts = st.session_state.cross_exchange_tracker.detect_cross_exchange_activity(active_wallets)
        all_alerts.extend(cross_exchange_alerts)
    
    # Send alerts and log to database
    if email_enabled and all_alerts:
        st.markdown("### 🔔 Recent Alerts")
        for alert in all_alerts:
            if should_send_alert(alert.get('whale', 'Unknown'), alert['type'], alert.get('coin')):
                if send_email_alert(f"Whale Alert - {alert.get('whale', 'Unknown')}", alert['message'], alert.get('urgent', False)):
                    alert_icon = "🚨" if alert.get('urgent', False) else "📊"
                    st.success(f"{alert_icon} {alert['message'].split('!')[0]}")
                    
                    # Add to session state
                    st.session_state.sent_alerts.append({
                        'time': datetime.now().strftime('%H:%M:%S'),
                        'whale': alert.get('whale', 'Unknown'),
                        'type': alert['type'],
                        'coin': alert.get('coin', 'N/A'),
                        'message': alert['message'].split('\n')[0]
                    })
                    
                    # Log to database
                    st.session_state.whale_database.log_alert(alert)
    
    # Show recent alerts
    if st.session_state.sent_alerts:
        st.markdown("#### 📋 Alert History (Last 10)")
        recent_alerts = st.session_state.sent_alerts[-10:]
        for alert in reversed(recent_alerts):
            coin_info = f" - {alert['coin']}" if alert['coin'] != 'N/A' else ""
            st.write(f"**{alert['time']}** - {alert['whale']}{coin_info}: {alert['message']}")
    
    # Log whale data to database
    try:
        st.session_state.whale_database.log_whale_position(whale_data)
    except Exception as e:
        st.error(f"Database logging error: {e}")
    
    # Summary Statistics
    st.markdown("## 📈 Live Overview")
    
    active_whales = [w for w in whale_data.values() if w['total_value'] > 1000]
    total_portfolio = sum(w['total_value'] for w in active_whales)
    total_pnl = sum(w['total_pnl'] for w in active_whales)
    total_positions = sum(w['position_count'] for w in active_whales)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💰 Total Portfolio", f"${total_portfolio:,.0f}", delta=f"{len(active_whales)} active whales")
    with col2:
        st.metric("📊 Total Positions", f"{total_positions}", delta=f"{len(active_whales)} whales")
    with col3:
        pnl_percent = (total_pnl / total_portfolio * 100) if total_portfolio > 0 else 0
        st.metric("📈 Net P&L", f"${total_pnl:+,.0f}", delta=f"{pnl_percent:+.1f}%")
    with col4:
        st.metric("🟢 Active Whales", f"{len(active_whales)}/{len(whale_data)}", delta=f"{len(whale_data) - len(active_whales)} inactive")
    
    # Cross-Exchange Intelligence Section
    st.markdown("## 🌐 Cross-Exchange Whale Intelligence")
    
    if active_wallets:
        for wallet in active_wallets[:2]:  # Show first 2 active whales
            cross_balances = st.session_state.cross_exchange_tracker.get_cross_chain_balances(wallet)
            
            if cross_balances:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("🌍 Active Chains", len(cross_balances))
                with col2:
                    total_balance = sum(cross_balances.values())
                    st.metric("💰 Cross-Chain Balance", f"{total_balance:.2f} ETH")
                with col3:
                    main_chain = max(cross_balances, key=cross_balances.get)
                    st.metric("🎯 Main Chain", main_chain.upper())
            else:
                # Show enhanced wallet info instead
                wallet_info = st.session_state.cross_exchange_tracker.get_enhanced_wallet_info(wallet)
                if wallet_info['has_balance']:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("🌍 Active Chains", len(wallet_info['active_chains']))
                    with col2:
                        st.metric("💰 Total Balance", f"{wallet_info['total_balance_eth']:.2f} ETH")
                    with col3:
                        st.metric("🕒 Last Updated", wallet_info['last_updated'])
                else:
                    st.info(f"🔍 Scanning cross-chain activity for {wallet[:8]}... (Free API limits may affect data)")
    else:
        st.info("No active whales with significant positions for cross-exchange analysis")
    
    # Leverage Intelligence Section
    st.markdown("## ⚡ Live Leverage Intelligence")
    
    if leverage_alerts:
        for alert in leverage_alerts:
            urgency_color = "🔴" if alert['urgency'] == 'HIGH' else "🟡"
            st.warning(f"{urgency_color} {alert['message']}")
    
    # Display leverage statistics - ENHANCED SECTION
    st.markdown("### 📊 Leverage Intelligence Dashboard")
    
    # Get comprehensive leverage stats
    leverage_stats = st.session_state.leverage_monitor.get_all_whales_stats(whale_data)
    
    if leverage_stats:
        # Create columns for stats
        num_cols = min(3, len(leverage_stats))
        leverage_stats_cols = st.columns(num_cols)
        
        for idx, (whale_name, stats) in enumerate(leverage_stats.items()):
            if idx < num_cols:
                with leverage_stats_cols[idx]:
                    st.metric(
                        f"⚡ {whale_name}", 
                        f"{stats['total_leverage_alerts']} alerts",
                        delta=f"{stats['high_leverage_positions']} high leverage"
                    )
                    st.caption(f"Max: {stats['max_leverage_used']:.1f}x leverage")
    else:
        # Show current high leverage positions instead
        st.info("🔍 Monitoring for leverage patterns...")
        
        high_leverage_whales = []
        for whale_name, data in whale_data.items():
            if data['total_value'] > 1000:
                high_leverage_positions = [p for p in data['positions'] if p['Leverage'] >= 8.0]
                if high_leverage_positions:
                    high_leverage_whales.append({
                        'whale': whale_name,
                        'count': len(high_leverage_positions),
                        'max_leverage': max(p['Leverage'] for p in high_leverage_positions)
                    })
        
        if high_leverage_whales:
            st.subheader("🎯 Current High Leverage Positions")
            for whale_info in high_leverage_whales:
                st.write(f"**{whale_info['whale']}**: {whale_info['count']} positions (max {whale_info['max_leverage']:.1f}x)")
    
    # Historical Analytics Section
    st.markdown("## 📊 Historical Analytics")
    
    try:
        positions_df, alerts_df = st.session_state.whale_database.get_historical_data(days=1)
        
        if not positions_df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("📈 Positions Tracked", len(positions_df))
            
            with col2:
                st.metric("📊 Alerts Logged", len(alerts_df))
            
            # Show recent activity chart
            if len(positions_df) > 0:
                daily_activity = positions_df.groupby('whale_name').size().reset_index(name='position_count')
                fig = px.bar(daily_activity, x='whale_name', y='position_count', 
                            title='Recent Whale Activity (Last 24 Hours)',
                            color='position_count',
                            color_continuous_scale='Viridis')
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No historical data available yet. Data will appear after the system runs for a while.")
    except Exception as e:
        st.error(f"Error loading historical data: {e}")
    
    # Main Whale Dashboard
    display_whale_dashboard(whale_data)
    
    # Update previous data
    st.session_state.previous_whale_data = whale_data
    
    # Footer
    st.markdown("---")
    st.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    st.markdown(f"**Data Source:** Hyperliquid Mainnet API | **Update Frequency:** {refresh_rate} seconds")
    st.markdown("**Database:** SQLite | **Version:** 2.0 Production")
    
    # Auto-refresh
    st.markdown(f"""
    <script>
    setTimeout(function() {{
        window.location.reload();
    }}, {refresh_rate * 1000});
    </script>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
