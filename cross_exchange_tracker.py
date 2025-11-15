import requests
import time
from datetime import datetime

class CrossExchangeTracker:
    def __init__(self):
        self.exchange_activity = {}
        self.last_analysis_time = {}
        
    def get_etherscan_transactions(self, wallet_address, api_key=""):
        """Get recent transactions from Etherscan (free tier)"""
        try:
            # Use free tier without API key (limited to 1 request/5 sec)
            url = f"https://api.etherscan.io/api?module=account&action=txlist&address={wallet_address}&startblock=0&endblock=99999999&page=1&offset=10&sort=desc"
            if api_key:
                url += f"&apikey={api_key}"
                
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if data['status'] == '1':
                return data['result']
            else:
                print(f"⚠️ Etherscan API limit reached or error: {data.get('message', 'Unknown error')}")
                return []
        except Exception as e:
            print(f"❌ Etherscan error: {e}")
            return []
    
    def get_bscscan_transactions(self, wallet_address, api_key=""):
        """Get recent transactions from BscScan (free tier)"""
        try:
            url = f"https://api.bscscan.com/api?module=account&action=txlist&address={wallet_address}&startblock=0&endblock=99999999&page=1&offset=10&sort=desc"
            if api_key:
                url += f"&apikey={api_key}"
                
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if data['status'] == '1':
                return data['result']
            else:
                print(f"⚠️ BscScan API limit reached or error: {data.get('message', 'Unknown error')}")
                return []
        except Exception as e:
            print(f"❌ BscScan error: {e}")
            return []
    
    def analyze_exchange_deposits(self, transactions, wallet_address):
        """Analyze transactions for exchange deposits"""
        from config import EXCHANGE_HOT_WALLETS
        
        exchange_deposits = {}
        
        for tx in transactions:
            to_address = tx.get('to', '').lower()
            value_eth = int(tx.get('value', 0)) / 10**18
            
            # Check if transaction is to known exchange hot wallet
            for exchange, hot_wallet in EXCHANGE_HOT_WALLETS.items():
                if to_address == hot_wallet.lower():
                    if exchange not in exchange_deposits:
                        exchange_deposits[exchange] = []
                    
                    exchange_deposits[exchange].append({
                        'value_eth': value_eth,
                        'timestamp': datetime.fromtimestamp(int(tx.get('timeStamp', 0))),
                        'hash': tx.get('hash', '')
                    })
        
        return exchange_deposits
    
    def detect_cross_exchange_activity(self, whale_wallets):
        """Detect cross-exchange accumulation patterns with better free tier handling"""
        from config import EMAIL_CONFIG
        
        alerts = []
        current_time = time.time()
        
        for wallet_address in whale_wallets:
            # Rate limiting for free APIs (1 analysis per wallet per 10 minutes)
            if wallet_address in self.last_analysis_time:
                if current_time - self.last_analysis_time[wallet_address] < 600:  # 10 minutes
                    continue
            
            print(f"🔍 Analyzing cross-exchange activity for {wallet_address[:8]}...")
            
            try:
                # Get transactions from multiple chains with delay for rate limiting
                eth_txs = self.get_etherscan_transactions(wallet_address)
                time.sleep(1)  # Rate limit delay
                bsc_txs = self.get_bscscan_transactions(wallet_address)
                
                # Analyze for exchange deposits
                eth_deposits = self.analyze_exchange_deposits(eth_txs, wallet_address)
                bsc_deposits = self.analyze_exchange_deposits(bsc_txs, wallet_address)
                
                # Combine all exchange activity
                all_deposits = {}
                for exchange, deposits in {**eth_deposits, **bsc_deposits}.items():
                    total_value = sum(d['value_eth'] for d in deposits)
                    if total_value > 0:
                        all_deposits[exchange] = {
                            'total_eth': total_value,
                            'transaction_count': len(deposits),
                            'latest_deposit': max([d['timestamp'] for d in deposits]) if deposits else None
                        }
                
                # Check for multi-exchange activity (lower threshold for free tier)
                active_exchanges = len(all_deposits)
                total_deposit_value = sum(data['total_eth'] for data in all_deposits.values())
                
                # Alert conditions (lower thresholds for free API data)
                if active_exchanges >= 2 and total_deposit_value > 5:  # > 5 ETH total
                    alert_message = (
                        f"🌐 CROSS-EXCHANGE ACTIVITY DETECTED!\n\n"
                        f"🐋 Wallet: {wallet_address[:8]}...{wallet_address[-6:]}\n"
                        f"💰 Total Deposits: {total_deposit_value:.2f} ETH\n"
                        f"🏦 Exchanges Used: {active_exchanges}\n"
                    )
                    
                    for exchange, data in all_deposits.items():
                        alert_message += f"   • {exchange.upper()}: {data['total_eth']:.2f} ETH ({data['transaction_count']} txs)\n"
                    
                    alert_message += f"\n⏰ Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}"
                    
                    alerts.append({
                        'type': 'CROSS_EXCHANGE',
                        'wallet': wallet_address,
                        'exchanges': list(all_deposits.keys()),
                        'total_value_eth': total_deposit_value,
                        'message': alert_message,
                        'urgency': 'HIGH' if total_deposit_value > 50 else 'MEDIUM'
                    })
                
                self.last_analysis_time[wallet_address] = current_time
                
            except Exception as e:
                print(f"❌ Error analyzing {wallet_address[:8]}: {e}")
                continue
        
        return alerts
    
    def get_wallet_balance(self, wallet_address, chain='ethereum'):
        """Get current wallet balance across chains with free tier support"""
        try:
            if chain == 'ethereum':
                url = f"https://api.etherscan.io/api?module=account&action=balance&address={wallet_address}&tag=latest"
            elif chain == 'bsc':
                url = f"https://api.bscscan.com/api?module=account&action=balance&address={wallet_address}&tag=latest"
            else:
                return 0
                
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if data['status'] == '1':
                balance_wei = int(data['result'])
                return balance_wei / 10**18
            return 0
        except Exception as e:
            print(f"❌ {chain} balance error: {e}")
            return 0
    
    def get_cross_chain_balances(self, wallet_address):
        """Get balances across multiple chains with error handling"""
        try:
            chains = {
                'ethereum': self.get_wallet_balance(wallet_address, 'ethereum'),
                'bsc': self.get_wallet_balance(wallet_address, 'bsc')
            }
            
            # Add small delay for rate limiting
            time.sleep(0.5)
            
            return {chain: balance for chain, balance in chains.items() if balance > 0.001}  # Filter very small balances
        except Exception as e:
            print(f"❌ Cross-chain balance error for {wallet_address[:8]}: {e}")
            return {}
    
    def get_enhanced_wallet_info(self, wallet_address):
        """Get enhanced wallet information with better free tier handling"""
        balances = self.get_cross_chain_balances(wallet_address)
        activity_summary = {
            'total_balance_eth': sum(balances.values()),
            'active_chains': list(balances.keys()),
            'has_balance': len(balances) > 0,
            'last_updated': datetime.now().strftime('%H:%M:%S')
        }
        return activity_summary
