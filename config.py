# ===== WHALE CONFIGURATION =====
WHALE_ADDRESSES = {
    "0x5b5d51203a0f9079f8aeb098a6523a13f298c060": "🦁 Singapore Whale",
    "0xc2a30212a8ddac9e123944d6e29faddce994e5f2": "🦅 US Whale", 
    "0x4044570e13b5184f7eb2709de25a4eb766a4794c": "👑 UK Whale",
    "0x6a56d5665bae79056207c8605c7fa5421737711b": "🕌 Emirates Whale",
    "0xd83cff88a32ffbf3951f2b13e4a0a37103b3193d": "🐉 Hong Kong Whale"
}

WHALE_GEO_DATA = {
    "0x5b5d51203a0f9079f8aeb098a6523a13f298c060": {
        "name": "🦁 Singapore Whale",
        "country": "Singapore",
        "region": "Asia",
        "risk_level": "Medium"
    },
    "0xc2a30212a8ddac9e123944d6e29faddce994e5f2": {
        "name": "🦅 US Whale",
        "country": "United States", 
        "region": "North America",
        "risk_level": "High"
    },
    "0x4044570e13b5184f7eb2709de25a4eb766a4794c": {
        "name": "👑 UK Whale",
        "country": "United Kingdom",
        "region": "Europe",
        "risk_level": "High"
    }
}

# ===== EMAIL CONFIGURATION =====
EMAIL_CONFIG = {
    "SENDER_EMAIL": "safecaretrustisb@gmail.com",
    "SENDER_PASSWORD": "bwcwhktylznehjwt",
    "RECEIVER_EMAILS": [
        "safecaretrustisb@gmail.com",
        "yoursecondemail@gmail.com",
        "yourthirdemail@yahoo.com"
    ],
    "ALERT_THRESHOLDS": {
        "new_position": 100000,  # Alert for positions > $100k
        "portfolio_change": 50000,  # Alert for portfolio changes > $50k
        "large_pnl": 100000,  # Alert for P&L moves > $100k
        "large_trade": 500000  # Alert for large trades > $500k
    },
    "ALERT_COOLDOWNS": {
        "NEW_WHALE": 3600,  # 1 hour cooldown for new whale alerts
        "NEW_POSITION": 1800,  # 30 minutes for new position alerts
        "PORTFOLIO_CHANGE": 900,  # 15 minutes for portfolio changes
        "LARGE_PNL": 300,  # 5 minutes for P&L alerts
        "SAME_COIN_PNL": 600,  # 10 minutes for same coin P&L alerts
        "LEVERAGE_SURGE": 1800,  # 30 minutes for leverage alerts
        "CROSS_EXCHANGE": 3600  # 1 hour for cross-exchange alerts
    }
}

# ===== CROSS-EXCHANGE CONFIG =====
EXCHANGE_HOT_WALLETS = {
    'binance': '0x3f5CE5FBFe3E9af3971dD833D26bA9b5C936f0bE',
    'coinbase': '0xA9D1e08C7793af67E9d92fe308d5697FB81d3E43',
    'kraken': '0x2910543Af39abA0Cd09dBb2D50200b3E800A63D2',
    'kucoin': '0x2b5634c42055806a59e9107ed44d43c426e58258'
}

BLOCKCHAIN_SCANNERS = {
    'ethereum': 'https://api.etherscan.io/api',
    'bsc': 'https://api.bscscan.com/api',
    'polygon': 'https://api.polygonscan.com/api',
    'avalanche': 'https://api.snowtrace.io/api'
}
