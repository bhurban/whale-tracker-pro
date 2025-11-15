import smtplib
import time
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Global position tracking
position_timestamps = {}

def send_email_alert(subject, message, is_urgent=False):
    """Send email alert to multiple recipients"""
    from config import EMAIL_CONFIG
    
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG["SENDER_EMAIL"]
        msg['To'] = ", ".join(EMAIL_CONFIG["RECEIVER_EMAILS"])
        
        if is_urgent:
            subject = f"🚨 URGENT: {subject}"
        else:
            subject = f"📊 {subject}"
            
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_CONFIG["SENDER_EMAIL"], EMAIL_CONFIG["SENDER_PASSWORD"])
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Email alert sent to {len(EMAIL_CONFIG['RECEIVER_EMAILS'])} recipients")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email alert: {e}")
        return False

def should_send_alert(whale_name, alert_type, coin=None):
    """Check if we should send alert based on cooldown periods"""
    from config import EMAIL_CONFIG
    
    current_time = time.time()
    
    # Initialize alert tracking in session state
    if 'alert_cooldowns' not in globals():
        globals()['alert_cooldowns'] = {}
    
    # Create unique key for this alert
    if alert_type == "LARGE_PNL" and coin:
        alert_key = f"{whale_name}_{alert_type}_{coin}"
    elif alert_type in ["LEVERAGE_SURGE", "CROSS_EXCHANGE", "NEW_POSITION"]:
        alert_key = f"{whale_name}_{alert_type}_{coin if coin else 'general'}"
    else:
        alert_key = f"{whale_name}_{alert_type}"
    
    # Check if alert was recently sent
    last_sent = globals()['alert_cooldowns'].get(alert_key, 0)
    cooldown_period = EMAIL_CONFIG["ALERT_COOLDOWNS"].get(alert_type, 300)
    
    if current_time - last_sent < cooldown_period:
        remaining_time = cooldown_period - (current_time - last_sent)
        print(f"⏳ Alert cooldown active for {alert_key}: {remaining_time:.0f}s remaining")
        return False
    
    # Update cooldown timer
    globals()['alert_cooldowns'][alert_key] = current_time
    return True

def track_position_timestamps(whale_name, current_positions):
    """Track when positions were first detected"""
    global position_timestamps
    
    current_time = time.time()
    
    if whale_name not in position_timestamps:
        position_timestamps[whale_name] = {}
    
    # Update timestamps for current positions
    for position in current_positions:
        coin = position['Coin']
        position_key = f"{whale_name}_{coin}"
        
        if position_key not in position_timestamps[whale_name]:
            # New position detected - record first seen time
            position_timestamps[whale_name][position_key] = {
                'first_seen': current_time,
                'last_seen': current_time,
                'value': position['Value']
            }
            print(f"🆕 NEW POSITION TIMESTAMP: {whale_name} - {coin} first seen at {datetime.fromtimestamp(current_time).strftime('%H:%M:%S')}")
        else:
            # Update last seen time
            position_timestamps[whale_name][position_key]['last_seen'] = current_time

def get_recently_opened_positions(whale_name, current_positions, time_window=300):
    """Find positions that were opened in the last time_window seconds"""
    global position_timestamps
    
    current_time = time.time()
    recent_positions = []
    
    if whale_name not in position_timestamps:
        return recent_positions
    
    for position in current_positions:
        coin = position['Coin']
        position_key = f"{whale_name}_{coin}"
        
        if position_key in position_timestamps[whale_name]:
            position_data = position_timestamps[whale_name][position_key]
            time_since_first_seen = current_time - position_data['first_seen']
            
            # Position is "recent" if first seen within the time window
            if time_since_first_seen <= time_window:
                recent_positions.append({
                    'coin': coin,
                    'position': position,
                    'seconds_ago': time_since_first_seen,
                    'first_seen': position_data['first_seen']
                })
    
    return recent_positions

def check_for_alerts(previous_data, current_data):
    """Check for significant changes that warrant alerts"""
    from config import EMAIL_CONFIG
    
    alerts = []
    
    print(f"🔍 [DEBUG] Starting alert check. Previous data keys: {list(previous_data.keys())}")
    
    for whale_name, current_whale in current_data.items():
        if current_whale['position_count'] == 0 or current_whale['total_value'] < 1000:
            continue
            
        previous_whale = previous_data.get(whale_name, {})
        previous_positions = previous_whale.get('positions', [])
        current_positions = current_whale.get('positions', [])
        
        # Track position timestamps for recent opening detection
        track_position_timestamps(whale_name, current_positions)
        
        # DEBUG: Detailed position analysis
        print(f"🔍 [DEBUG] {whale_name}:")
        print(f"   Previous positions: {len(previous_positions)}")
        print(f"   Current positions: {len(current_positions)}")
        
        # NEW: Detect RECENTLY opened positions (using timestamp tracking)
        recent_positions = get_recently_opened_positions(whale_name, current_positions, time_window=600)  # 10 minutes
        
        print(f"   Recently opened positions (last 10min): {[p['coin'] for p in recent_positions]}")
        
        for recent_data in recent_positions:
            coin = recent_data['coin']
            position = recent_data['position']
            seconds_ago = recent_data['seconds_ago']
            
            if position['Value'] > EMAIL_CONFIG["ALERT_THRESHOLDS"]["new_position"]:
                print(f"   ✅ RECENT POSITION QUALIFIED: {whale_name} - {coin} (${position['Value']:,.2f}, opened {seconds_ago:.0f}s ago)")
                
                if should_send_alert(whale_name, "NEW_POSITION", coin):
                    alert_message = (
                        f"🆕 NEW POSITION OPENED!\n\n"
                        f"🐋 Whale: {whale_name}\n"
                        f"💰 Coin: {coin} {position['Type']}\n"
                        f"📊 Position Size: ${position['Value']:,.2f}\n"
                        f"⚡ Leverage: {position['Leverage_Display']}\n"
                        f"🎯 Entry Price: ${position['Entry Price']:,.2f}\n"
                        f"📈 Size: {position['Size']:,.0f} {coin}\n"
                        f"⏱️ Opened: {seconds_ago:.0f} seconds ago\n\n"
                        f"⏰ Alert Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}"
                    )
                    
                    alerts.append({
                        'type': 'NEW_POSITION',
                        'whale': whale_name,
                        'coin': coin,
                        'message': alert_message,
                        'urgent': position['Value'] > 1000000
                    })
                    print(f"   📧 NEW_POSITION alert queued for {coin}")
        
        # Traditional new position detection (for comparison)
        if previous_whale and previous_whale.get('total_value', 0) > 1000:
            previous_coins = {p['Coin'] for p in previous_positions}
            current_coins = {p['Coin'] for p in current_positions}
            new_coins = current_coins - previous_coins
            
            print(f"   Traditional detection - New coins: {sorted(new_coins)}")
        
        # Rest of your existing alert logic (NEW_WHALE, PORTFOLIO_CHANGE, LARGE_PNL)...
        # New whale activity
        if not previous_whale or previous_whale.get('total_value', 0) < 1000:
            if current_whale['total_value'] > EMAIL_CONFIG["ALERT_THRESHOLDS"]["new_position"]:
                if should_send_alert(whale_name, "NEW_WHALE"):
                    print(f"   🐋 NEW_WHALE alert triggered for {whale_name}")
                    alerts.append({
                        'type': 'NEW_WHALE',
                        'whale': whale_name,
                        'message': f"🐋 {whale_name} JUST BECAME ACTIVE!\n\n"
                                  f"📍 Portfolio: ${current_whale['total_value']:,.2f}\n"
                                  f"📊 Positions: {current_whale['position_count']}\n"
                                  f"💸 P&L: ${current_whale['total_pnl']:+,.2f}\n"
                                  f"🌍 Location: {current_whale['country']}\n"
                                  f"👛 Wallet: {current_whale['display_wallet']}\n\n"
                                  f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}",
                        'urgent': True
                    })
        
        # Portfolio changes
        if previous_whale and previous_whale.get('total_value', 0) > 1000:
            portfolio_change = current_whale['total_value'] - previous_whale.get('total_value', 0)
            if abs(portfolio_change) > EMAIL_CONFIG["ALERT_THRESHOLDS"]["portfolio_change"]:
                if should_send_alert(whale_name, "PORTFOLIO_CHANGE"):
                    alerts.append({
                        'type': 'PORTFOLIO_CHANGE',
                        'whale': whale_name,
                        'message': f"📈 {whale_name} PORTFOLIO CHANGE!\n\n"
                                  f"💰 Change: ${portfolio_change:+,.2f}\n"
                                  f"📊 New Total: ${current_whale['total_value']:,.2f}\n"
                                  f"🎯 Positions: {current_whale['position_count']}\n"
                                  f"💸 Total P&L: ${current_whale['total_pnl']:+,.2f}\n\n"
                                  f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}",
                        'urgent': abs(portfolio_change) > 1000000
                    })
        
        # Large P&L moves
        for position in current_whale['positions']:
            if abs(position['P&L']) > EMAIL_CONFIG["ALERT_THRESHOLDS"]["large_pnl"]:
                if should_send_alert(whale_name, "LARGE_PNL", position['Coin']):
                    alerts.append({
                        'type': 'LARGE_PNL',
                        'whale': whale_name,
                        'coin': position['Coin'],
                        'message': f"🎯 {whale_name} LARGE P&L MOVE!\n\n"
                                  f"💰 Coin: {position['Coin']} {position['Type']}\n"
                                  f"📈 P&L: ${position['P&L']:+,.2f}\n"
                                  f"📊 P&L %: {position['P&L %']:+.1f}%\n"
                                  f"🎯 Position Value: ${position['Value']:,.2f}\n"
                                  f"⚡ Leverage: {position['Leverage_Display']}\n\n"
                                  f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}",
                        'urgent': abs(position['P&L']) > 500000
                    })
    
    print(f"🔍 [DEBUG] Alert check complete. Total alerts found: {len(alerts)}")
    return alerts
