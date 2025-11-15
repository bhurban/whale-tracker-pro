def display_whale_dashboard(use_demo_data=False):
    """Display dashboard with REAL Hyperliquid data"""
    
    if use_demo_data:
        st.warning("📊 Demo mode activated - showing realistic patterns")
        whale_data = get_realistic_fallback_data()
    else:
        whale_data = get_real_whale_data()
    
    if not whale_data:
        st.error("❌ No whale data available")
        return
    
    # Calculate summary metrics from REAL data
    total_whales = len(whale_data)
    total_positions = sum(len(data['positions']) for data in whale_data.values())
    total_value = sum(pos['size'] for data in whale_data.values() for pos in data['positions'])
    total_pnl = sum(pos['pnl'] for data in whale_data.values() for pos in data['positions'])
    
    # Enhanced summary metrics
    avg_leverage = sum(pos['leverage'] for data in whale_data.values() for pos in data['positions']) / total_positions if total_positions > 0 else 0
    winning_positions = sum(1 for data in whale_data.values() for pos in data['positions'] if pos['pnl'] > 0)
    win_rate = (winning_positions / total_positions * 100) if total_positions > 0 else 0
    
    # Display REAL summary
    st.success(f"**🌐 LIVE HYPERLIQUID DATA:** {total_whales} active whales with {total_positions} positions")
    
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
    
    # Display REAL whale data with FULL wallet addresses
    for wallet, data in whale_data.items():
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.subheader(f"{data['name']}")
                
                # 🎯 FULL WALLET ADDRESS DISPLAY
                st.markdown(f"**Wallet:** `{wallet}`")
                
                # Optional: Also show with copy button functionality
                st.code(wallet, language="text")
                
                st.write(f"**Region:** {data['geo'].get('region', 'Global')}")
                st.write(f"**Trading Style:** {data['geo'].get('style', 'Active Trader')}")
                st.write(f"**Last Updated:** {data['last_updated'].strftime('%Y-%m-%d %H:%M:%S')}")
                st.write(f"**Active Positions:** {len(data['positions'])} trades")
                st.write(f"**Data Source:** {data['data_source']}")
            
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
            
            st.markdown("---")
