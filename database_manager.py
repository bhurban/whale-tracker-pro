import sqlite3
import pandas as pd
from datetime import datetime

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
