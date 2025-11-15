import time
from datetime import datetime

class LeverageMonitor:
    def __init__(self):
        self.leverage_history = {}
        self.leverage_alerts = []
        self.pattern_alerts = []  # Track pattern alerts separately
        
    def monitor_leverage_changes(self, whale_data):
        """Monitor for significant leverage changes"""
        current_alerts = []
        
        for whale_name, data in whale_data.items():
            if data['position_count'] == 0:
                continue
                
            current_positions = data['positions']
            
            for position in current_positions:
                coin = position['Coin']
                current_leverage = position['Leverage']
                position_value = position['Value']
                
                # Skip small positions
                if position_value < 10000:
                    continue
                
                # Initialize tracking
                if whale_name not in self.leverage_history:
                    self.leverage_history[whale_name] = {}
                
                position_key = f"{whale_name}_{coin}"
                
                if position_key not in self.leverage_history[whale_name]:
                    self.leverage_history[whale_name][position_key] = {
                        'previous_leverage': current_leverage,
                        'last_alert_time': 0,
                        'max_leverage_seen': current_leverage,
                        'leverage_increases': 0,
                        'leverage_alerts_sent': 0
                    }
                
                previous_data = self.leverage_history[whale_name][position_key]
                previous_leverage = previous_data['previous_leverage']
                
                # Calculate leverage change
                leverage_change = current_leverage - previous_leverage
                leverage_ratio = current_leverage / previous_leverage if previous_leverage > 0 else float('inf')
                
                # Leverage surge detection (3x increase or 2x ratio)
                if (leverage_change >= 3.0 or leverage_ratio >= 2.0) and current_leverage >= 5.0:
                    current_time = time.time()
                    
                    # Check cooldown (30 minutes for leverage alerts)
                    if current_time - previous_data['last_alert_time'] > 1800:
                        
                        alert_message = (
                            f"⚡ LEVERAGE SURGE DETECTED!\n\n"
                            f"🐋 Whale: {whale_name}\n"
                            f"💰 Coin: {coin}\n"
                            f"📈 Leverage: {previous_leverage:.1f}x → {current_leverage:.1f}x\n"
                            f"📊 Increase: {leverage_change:+.1f}x ({leverage_ratio:.1f}×)\n"
                            f"💵 Position Value: ${position_value:,.2f}\n"
                            f"🎯 P&L: ${position['P&L']:+,.2f}\n"
                            f"🕒 Time: {datetime.now().strftime('%H:%M:%S UTC')}"
                        )
                        
                        alert_data = {
                            'type': 'LEVERAGE_SURGE',
                            'whale': whale_name,
                            'coin': coin,
                            'previous_leverage': previous_leverage,
                            'current_leverage': current_leverage,
                            'increase_ratio': leverage_ratio,
                            'position_value': position_value,
                            'message': alert_message,
                            'urgency': 'HIGH' if current_leverage > 10 else 'MEDIUM',
                            'timestamp': current_time
                        }
                        
                        current_alerts.append(alert_data)
                        previous_data['leverage_alerts_sent'] += 1
                        previous_data['last_alert_time'] = current_time
                        previous_data['leverage_increases'] += 1
                        previous_data['max_leverage_seen'] = max(previous_data['max_leverage_seen'], current_leverage)
                
                # Update leverage history
                previous_data['previous_leverage'] = current_leverage
        
        return current_alerts
    
    def detect_leverage_patterns(self, whale_data):
        """Detect sophisticated leverage patterns"""
        patterns = []
        
        for whale_name, data in whale_data.items():
            positions = data['positions']
            
            if len(positions) < 2:
                continue
            
            # Pattern 1: Multi-position high leverage
            high_leverage_positions = [p for p in positions if p['Leverage'] >= 8.0 and p['Value'] > 50000]
            
            if len(high_leverage_positions) >= 2:
                pattern_message = (
                    f"🎯 MULTI-POSITION HIGH LEVERAGE STRATEGY\n\n"
                    f"🐋 Whale: {whale_name}\n"
                    f"📊 High Leverage Positions: {len(high_leverage_positions)}\n"
                )
                
                for pos in high_leverage_positions:
                    pattern_message += f"   • {pos['Coin']}: {pos['Leverage']:.1f}x (${pos['Value']:,.0f})\n"
                
                pattern_message += f"\n🕒 Detected: {datetime.now().strftime('%H:%M:%S UTC')}"
                
                pattern_alert = {
                    'type': 'MULTI_POSITION_HIGH_LEVERAGE',
                    'whale': whale_name,
                    'positions': high_leverage_positions,
                    'message': pattern_message,
                    'urgency': 'HIGH',
                    'timestamp': time.time()
                }
                
                patterns.append(pattern_alert)
                
                # Track in history for statistics
                if whale_name not in self.leverage_history:
                    self.leverage_history[whale_name] = {}
                
                for pos in high_leverage_positions:
                    position_key = f"{whale_name}_{pos['Coin']}_pattern"
                    if position_key not in self.leverage_history[whale_name]:
                        self.leverage_history[whale_name][position_key] = {
                            'pattern_alerts_sent': 0,
                            'max_pattern_leverage': pos['Leverage']
                        }
                    self.leverage_history[whale_name][position_key]['pattern_alerts_sent'] += 1
                    self.leverage_history[whale_name][position_key]['max_pattern_leverage'] = max(
                        self.leverage_history[whale_name][position_key]['max_pattern_leverage'],
                        pos['Leverage']
                    )
            
            # Pattern 2: Leverage averaging down
            for position in positions:
                if position['P&L'] < -0.05 * position['Value']:  # >5% drawdown
                    position_key = f"{whale_name}_{position['Coin']}"
                    
                    if position_key in self.leverage_history.get(whale_name, {}):
                        history = self.leverage_history[whale_name][position_key]
                        
                        if position['Leverage'] > history['previous_leverage']:
                            pattern_message = (
                                f"🔄 LEVERAGE AVERAGING DOWN DETECTED\n\n"
                                f"🐋 Whale: {whale_name}\n"
                                f"💰 Coin: {position['Coin']}\n"
                                f"📈 Leverage Increased: {history['previous_leverage']:.1f}x → {position['Leverage']:.1f}x\n"
                                f"💸 Current P&L: ${position['P&L']:+,.2f}\n"
                                f"📉 Drawdown: {abs(position['P&L']/position['Value']*100):.1f}%\n"
                                f"🕒 Time: {datetime.now().strftime('%H:%M:%S UTC')}"
                            )
                            
                            patterns.append({
                                'type': 'LEVERAGE_AVERAGING_DOWN',
                                'whale': whale_name,
                                'coin': position['Coin'],
                                'message': pattern_message,
                                'urgency': 'MEDIUM'
                            })
        
        self.pattern_alerts.extend(patterns)
        return patterns
    
    def get_leverage_stats(self, whale_name):
        """Get comprehensive leverage statistics for a whale"""
        if whale_name not in self.leverage_history:
            return None
        
        whale_history = self.leverage_history[whale_name]
        
        if not whale_history:
            return None
        
        # Count all types of alerts
        total_leverage_alerts = sum(data.get('leverage_alerts_sent', 0) for data in whale_history.values())
        total_pattern_alerts = sum(data.get('pattern_alerts_sent', 0) for data in whale_history.values())
        
        # Get max leverage
        max_leverage = max(
            [data.get('max_leverage_seen', 0) for data in whale_history.values()] +
            [data.get('max_pattern_leverage', 0) for data in whale_history.values()]
        )
        
        # Get high leverage positions count
        high_leverage_positions = sum(1 for data in whale_history.values() 
                                    if data.get('max_leverage_seen', 0) >= 8.0)
        
        return {
            'total_leverage_alerts': total_leverage_alerts + total_pattern_alerts,
            'leverage_surge_alerts': total_leverage_alerts,
            'pattern_alerts': total_pattern_alerts,
            'max_leverage_used': max_leverage if max_leverage > 0 else 0,
            'high_leverage_positions': high_leverage_positions,
            'monitored_positions': len(whale_history)
        }
    
    def get_all_whales_stats(self, whale_data):
        """Get leverage statistics for all active whales"""
        stats = {}
        for whale_name in whale_data.keys():
            whale_stats = self.get_leverage_stats(whale_name)
            if whale_stats and whale_stats['total_leverage_alerts'] > 0:
                stats[whale_name] = whale_stats
        return stats
