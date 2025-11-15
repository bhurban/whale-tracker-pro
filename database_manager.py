import sqlite3
import pandas as pd
from datetime import datetime
import json

class DatabaseManager:
    def __init__(self, db_path="whale_analytics.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Whale positions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS whale_positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                wallet_address TEXT,
                whale_name TEXT,
                symbol TEXT,
                side TEXT,
                size REAL,
                entry_price REAL,
                mark_price REAL,
                liq_price REAL,
                leverage REAL,
                unrealized_pnl REAL,
                margin REAL,
                timestamp DATETIME,
                raw_data TEXT
            )
        ''')
        
        # Whale alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS whale_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                wallet_address TEXT,
                alert_type TEXT,
                alert_message TEXT,
                severity TEXT,
                timestamp DATETIME,
                resolved BOOLEAN DEFAULT FALSE
            )
        ''')
        
        # Price history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                price REAL,
                timestamp DATETIME
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_whale_positions(self, whale_data):
        """Save whale positions to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for wallet, data in whale_data.items():
            for position in data['positions']:
                cursor.execute('''
                    INSERT INTO whale_positions 
                    (wallet_address, whale_name, symbol, side, size, entry_price, mark_price, liq_price, leverage, unrealized_pnl, margin, timestamp, raw_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    wallet,
                    data['name'],
                    position['symbol'],
                    position['side'],
                    position['size'],
                    position['entryPrice'],
                    position['markPrice'],
                    position['liqPrice'],
                    position['leverage'],
                    position['unrealizedPnl'],
                    position['margin'],
                    datetime.now(),
                    json.dumps(position.get('raw_data', {}))
                ))
        
        conn.commit()
        conn.close()
    
    def get_whale_history(self, wallet_address, hours=24):
        """Get historical positions for a whale"""
        conn = sqlite3.connect(self.db_path)
        query = '''
            SELECT * FROM whale_positions 
            WHERE wallet_address = ? AND timestamp >= datetime('now', ?)
            ORDER BY timestamp DESC
        '''
        df = pd.read_sql_query(query, conn, params=[wallet_address, f'-{hours} hours'])
        conn.close()
        return df
