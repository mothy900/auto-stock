Antigravity Agent Skill Specifications
1. Agent Profile
Name: Antigravity Agent (AGA)

Role: Autonomous US Stock Trading Bot specialized in Volatility Breakout Strategy.

Objective: Maximize risk-adjusted returns by exploiting intraday momentum while strictly adhering to risk management protocols.

Operating Environment: Alpaca Paper Trading (US Equity Market).

2. Capability Overview
The agent possesses the ability to ingest real-time market data, calculate technical indicators, execution buy/sell orders, and manage portfolio risk. It operates autonomously during US market hours (09:30 - 16:00 ET).

3. Tool Definitions (Function Calls)
A. Market Data Perception
get_current_price(symbol: str) -> float

Description: Fetches the most recent trade price for a given ticker symbol using Alpaca Data API.

Usage: Used to check if the breakout condition is met.

get_daily_ohlcv(symbol: str, days: int = 20) -> DataFrame

Description: Retrieves historical Open, High, Low, Close, Volume data for the specified number of days.

Usage: Essential for calculating the 'Range' (High - Low) and optimizing the 'K' value.

check_market_status() -> dict

Description: Returns the current status of the US market (Pre-market, Open, After-hours, Closed) based on US/Eastern time.

Usage: Determines whether to activate the trading loop or enter sleep mode.

B. Strategic Reasoning & Optimization
calculate_target_price(symbol: str, k: float) -> float

Description: Computes the breakout target price.

Formula: Target = Today_Open + (Yesterday_High - Yesterday_Low) * k

optimize_k_value(symbol: str) -> float

Description: Runs a backtest simulation on the last 20 days of data to find the 'K' value (0.3~0.9) that yields the highest cumulative return.

Usage: Called once daily before market open.

C. Execution & Action
submit_buy_order(symbol: str, qty: int, order_type: str = 'market') -> dict

Description: Sends a buy order to the Alpaca exchange.

Constraints: Only executable if cash_balance > estimated_cost.

submit_sell_order(symbol: str, qty: int, reason: str) -> dict

Description: Sends a sell order to liquidate positions.

Reasons: 'Target_Hit', 'Stop_Loss', 'Time_Cut' (End of Day).

get_account_summary() -> dict

Description: Retrieves total equity, cash balance, and buying power.

D. Risk Management
emergency_halt()

Description: Immediately cancels all open orders and liquidates all positions.

Usage: Triggered when system anomaly is detected or daily loss limit (-3%) is breached.

4. Operational Workflows
Daily Routine (Cron Jobs)
09:00 ET (Pre-Market):

Run check_market_status().

Update get_daily_ohlcv() for target symbols.

Execute optimize_k_value() to determine today's parameters.

Calculate calculate_target_price() and log targets.

09:30 ET - 15:50 ET (Trading Session):

Loop every 1 second:

price = get_current_price()

If price >= target_price AND price > sma_20 AND no_position:

submit_buy_order()

If position_exists:

Check Stop Loss condition (-3%).

15:55 ET (Market Close Approach):

Execute submit_sell_order(reason='Time_Cut') for all holdings.

Generate daily performance report.

5. Safety Protocols
Rate Limiting: Ensure API calls do not exceed 200 requests per minute to avoid IP bans.

Data Integrity: If get_current_price() returns stale data (> 1 min old), pause trading and alert.

Capital Allocation: Never invest more than 20% of total equity in a single trade (Kelly Criterion simplified).

6. Deployment Procedures (AWS EC2)
A. Initial Setup
1. Provision EC2 Instance (Amazon Linux 2023, t2.micro).
2. Configure Security Group: Allow SSH (22) and Streamlit (8501).
3. Install Dependencies:
   ```bash
   sudo dnf install git python3-pip
   git clone https://github.com/mothy900/auto-stock.git
   cd auto-stock
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

B. Configuration
1. Create `.env` file with Alpaca API keys.
2. Create `.streamlit/secrets.toml` for dashboard password.

C. Service Management (Systemd)
1. Create `/etc/systemd/system/antigravity.service`:
   ```ini
   [Unit]
   Description=Antigravity Trading Bot
   After=network.target

   [Service]
   User=ec2-user
   WorkingDirectory=/home/ec2-user/stock-trading
   ExecStart=/home/ec2-user/stock-trading/venv/bin/python main.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```
2. Enable and Start:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable antigravity
   sudo systemctl start antigravity
   ```

D. Dashboard Deployment
1. Use `run.sh` script to launch Streamlit in background.
   ```bash
   nohup ./run.sh > streamlit.log 2>&1 &
   ```
