"""
Configuration file for Whale Tracker Pro
"""

# Whale addresses to monitor (Hyperliquid wallet addresses)
WHALE_ADDRESSES = {
    "0x742d35Cc6634C0532925a3b8D": "Crypto Whale Alpha",
    "0x8a4bC2349335b7D6a5d2f7A3b9": "Institutional Trader", 
    "0x3cBdF0D8f7C4a5b0eE2d7a3c1": "DeFi Giant",
    "0x1a2b3c4d5e6f7a8b9c0d1e2f3": "Market Maker Pro",
    "0x9e8d7c6b5a4f3e2d1c0b9a8f7": "Hedge Fund One"
}

# Geographic data for whales
WHALE_GEO_DATA = {
    "0x742d35Cc6634C0532925a3b8D": {
        "region": "North America",
        "country": "US",
        "timezone": "EST"
    },
    "0x8a4bC2349335b7D6a5d2f7A3b9": {
        "region": "Europe", 
        "country": "UK",
        "timezone": "GMT"
    },
    "0x3cBdF0D8f7C4a5b0eE2d7a3c1": {
        "region": "Asia",
        "country": "SG", 
        "timezone": "SGT"
    },
    "0x1a2b3c4d5e6f7a8b9c0d1e2f3": {
        "region": "North America",
        "country": "CA",
        "timezone": "PST"
    },
    "0x9e8d7c6b5a4f3e2d1c0b9a8f7": {
        "region": "Europe", 
        "country": "CH",
        "timezone": "CET"
    }
}

# Alert thresholds
ALERT_THRESHOLDS = {
    "high_leverage": 8.0,
    "large_position": 500000,  # USD
    "pnl_alert": 10000,  # USD
    "liquidation_risk": 0.15  # 15% from liquidation
}

# API Configuration
HYPERLIQUID_CONFIG = {
    "mainnet_url": "https://api.hyperliquid.xyz",
    "testnet_url": "https://api.hyperliquid-testnet.xyz",
    "websocket_url": "wss://api.hyperliquid.xyz/ws"
}
