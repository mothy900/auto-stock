import streamlit as st
import sys
import os

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
sys.path.insert(0, project_root)

import pandas as pd
import time
from datetime import datetime
import pytz
from src.data.alpaca_interface import AlpacaInterface
from src.data.database import DatabaseManager
from src.backtest.analyzer import PerformanceAnalyzer
from alpaca.trading.requests import GetOrdersRequest
from alpaca.trading.enums import QueryOrderStatus
from streamlit_autorefresh import st_autorefresh

# Page Config
st.set_page_config(
    page_title="Antigravity Agent Dashboard",
    page_icon="💸",
    layout="wide"
)

# Auto-Refresh every 60 seconds
count = st_autorefresh(interval=60000, key="data_refresh")

# Initialize Interface
@st.cache_resource
def get_alpaca():
    return AlpacaInterface()

@st.cache_resource
def get_db():
    return DatabaseManager()

try:
    alpaca = get_alpaca()
    db = get_db()
except Exception as e:
    st.error(f"Failed to connect to services: {e}")
    st.stop()

# Main Content
st.title("🚀 Antigravity Agent Monitor")

# Top Metrics & Chart
try:
    account = alpaca.get_account_info()
    
    # 1. key Metrics (Top Row)
    m1, m2, m3 = st.columns(3)
    equity = float(account.equity)
    last_equity = float(account.last_equity)
    change = equity - last_equity
    
    m1.metric("Total Equity", f"${equity:,.2f}", f"{change:+.2f}")
    m2.metric("Cash Balance", f"${float(account.cash):,.2f}")
    m3.metric("Buying Power", f"${float(account.buying_power):,.2f}")
    
    st.divider()

    # 2. Equity History Chart
    st.subheader("📈 Asset Growth (Equity History)")
    
    # Fetch History
    history = alpaca.get_portfolio_history(period="1M", timeframe="1D")
    
    if history and history.timestamp:
        # Convert to DataFrame
        df_hist = pd.DataFrame({
            'timestamp': [datetime.fromtimestamp(ts, pytz.timezone('US/Eastern')) for ts in history.timestamp],
            'equity': history.equity
        })
        df_hist.set_index('timestamp', inplace=True)
        
        # Plot (Line Chart)
        st.line_chart(df_hist['equity'], color="#00FF00")
    else:
        st.info("No sufficient history data available yet.")

except Exception as e:
    st.error(f"Error fetching account/history: {e}")

# Sidebar (Status Only)
st.sidebar.title("⚙️ Status")
if st.sidebar.button("🔄 Refresh Data"):
    st.rerun()

clock = alpaca.get_market_status()
status_color = "green" if clock.is_open else "red"
st.sidebar.markdown(f"**Market**: :{status_color}[{'OPEN' if clock.is_open else 'CLOSED'}]")

et_now = datetime.now(pytz.timezone('US/Eastern'))
st.sidebar.text(f"Server Time (ET):\n{et_now.strftime('%Y-%m-%d %H:%M:%S')}")
st.sidebar.divider()


# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Live Status", "📈 Analysis", "📝 Trade Logs", "⚙️ System"])

# --- TAB 1: Live Status ---
with tab1:
    st.subheader("Holdings")
    try:
        positions = alpaca.trading_client.get_all_positions()
        if positions:
            pos_data = []
            for p in positions:
                pos_data.append({
                    "Symbol": p.symbol,
                    "Qty": float(p.qty),
                    "Entry Price": float(p.avg_entry_price),
                    "Current Price": float(p.current_price),
                    "Market Value": float(p.market_value),
                    "P/L ($)": float(p.unrealized_pl),
                    "P/L (%)": float(p.unrealized_plpc) * 100
                })
            
            df_pos = pd.DataFrame(pos_data)
            
            st.dataframe(
                df_pos.style.format({
                    "Entry Price": "${:.2f}",
                    "Current Price": "${:.2f}",
                    "Market Value": "${:.2f}",
                    "P/L ($)": "${:+.2f}",
                    "P/L (%)": "{:+.2f}%"
                }),
                use_container_width=True
            )
        else:
            st.info("No active positions.")
            
    except Exception as e:
        st.error(f"Error fetching positions: {e}")

    st.divider()
    
    st.subheader("Recent Orders (Live)")
    try:
        req = GetOrdersRequest(status=QueryOrderStatus.ALL, limit=50)
        orders = alpaca.trading_client.get_orders(filter=req)
        
        if orders:
            order_data = []
            for o in orders:
                order_data.append({
                    "Time": o.created_at.astimezone(pytz.timezone('US/Eastern')).strftime('%Y-%m-%d %H:%M:%S'),
                    "Symbol": o.symbol,
                    "Side": o.side.value.upper(),
                    "Qty": float(o.qty),
                    "Filled": f"${float(o.filled_avg_price):.2f}" if o.filled_avg_price else "-",
                    "Status": o.status.value.upper()
                })
            
            df_orders = pd.DataFrame(order_data)
            
            # Color Rows
            def highlight_side(row):
                if row.Side == 'BUY':
                    return ['background-color: rgba(0, 255, 0, 0.1)'] * len(row)
                elif row.Side == 'SELL':
                    return ['background-color: rgba(255, 0, 0, 0.1)'] * len(row)
                else:
                    return [''] * len(row)

            st.dataframe(
                df_orders.style.apply(highlight_side, axis=1), 
                use_container_width=True
            )
        else:
            st.info("No recent orders.")
    except Exception as e:
        st.error(f"Error fetching orders: {e}")

# --- TAB 2: Analysis (New) ---
with tab2:
    st.subheader("Performance Scorecard (Paper Trading)")
    try:
        req_closed = GetOrdersRequest(status=QueryOrderStatus.CLOSED, limit=500)
        closed_orders = alpaca.trading_client.get_orders(filter=req_closed)
        
        daily_stats = PerformanceAnalyzer.calculate_daily_performance(closed_orders)
        metrics = PerformanceAnalyzer.get_summary_metrics(daily_stats)
        
        # Metrics Top Row
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Win Rate", f"{metrics['win_rate']:.1f}%")
        c2.metric("Total P/L", f"${metrics['total_pl']:.2f}")
        c3.metric("Total Trades", f"{metrics['total_trades']}")
        c4.metric("Avg P/L (Day)", f"${metrics['avg_pl']:.2f}")
        
        st.divider()
        
        if not daily_stats.empty:
            st.subheader("Cumulative Profit")
            daily_pl_sum = daily_stats.groupby('Date')['Net_PL'].sum().cumsum()
            st.line_chart(daily_pl_sum)
            
            st.subheader("Daily Details")
            st.dataframe(
                daily_stats.style.format({
                    "Net_PL": "${:+.2f}",
                    "Win": "✅"
                }).applymap(lambda x: 'color: protected_green' if x > 0 else 'color: protected_red', subset=['Net_PL']),
                use_container_width=True
            )
        else:
            st.info("No sufficient closed trades for analysis.")
            
    except Exception as e:
        st.error(f"Analysis Error: {e}")

# --- TAB 3: Trade Logs (DB) ---
with tab3:
    st.subheader("Database Logs")
    rows = db.execute_query("SELECT * FROM trade_logs ORDER BY timestamp DESC LIMIT 50")
    if rows:
        st.dataframe(pd.DataFrame([dict(r) for r in rows]), use_container_width=True)
    else:
        st.caption("No internal DB logs found.")

# --- TAB 4: System ---
with tab4:
    st.subheader("Control Panel")
    if st.button("⛔ EMERGENCY HALT (Liquidate All)", type="primary"):
        st.warning("Executing Emergency Liquidation...")
        try:
            alpaca.trading_client.cancel_orders()
            positions = alpaca.trading_client.get_all_positions()
            for p in positions:
                alpaca.submit_order(p.symbol, float(p.qty), 'sell')
            st.success("Halt Signal Sent.")
            time.sleep(2)
            st.rerun()
        except Exception as e:
            st.error(f"Halt Failed: {e}") 
