import pandas as pd
from typing import List, Dict
from datetime import datetime
import pytz

class PerformanceAnalyzer:
    @staticmethod
    def calculate_daily_performance(orders: list) -> pd.DataFrame:
        """
        Calculate daily P/L per symbol based on closed orders.
        Assumption: Intraday strategy (Flat at EOD). 
        P/L = (Sell Amount) - (Buy Amount)
        
        Returns: DataFrame with columns [Date, Symbol, P/L, Trades, Win]
        """
        if not orders:
            return pd.DataFrame()

        data = []
        
        # 1. Digest Orders
        for o in orders:
            if o.status != 'filled':
                continue
            
            # Timestamp to Date (US/Eastern)
            dt = o.filled_at.astimezone(pytz.timezone('US/Eastern'))
            date_str = dt.strftime('%Y-%m-%d')
            
            # Amount
            price = float(o.filled_avg_price) if o.filled_avg_price else 0.0
            qty = float(o.qty)
            amount = price * qty
            
            # Side effect
            # BUY: Cost (negative flow), SELL: Revenue (positive flow)
            flow = -amount if o.side == 'buy' else amount
            
            data.append({
                'Date': date_str,
                'Symbol': o.symbol,
                'Flow': flow,
                'Side': o.side,
                'Qty': qty
            })
            
        if not data:
            return pd.DataFrame()
            
        df = pd.DataFrame(data)
        
        # 2. Group by Date and Symbol
        # Sum of Flow = Net P/L (for completed round trips)
        daily_stats = df.groupby(['Date', 'Symbol']).agg({
            'Flow': 'sum',
            'Side': 'count' # Total orders (Buy+Sell)
        }).reset_index()
        
        daily_stats.rename(columns={'Flow': 'Net_PL', 'Side': 'Order_Count'}, inplace=True)
        
        # 3. Determine Win/Loss
        daily_stats['Win'] = daily_stats['Net_PL'] > 0
        
        return daily_stats

    @staticmethod
    def get_summary_metrics(daily_df: pd.DataFrame) -> Dict:
        """
        Calculate aggregate metrics.
        """
        if daily_df.empty:
            return {
                "total_pl": 0.0,
                "win_rate": 0.0,
                "total_trades": 0,
                "avg_pl": 0.0
            }
            
        total_pl = daily_df['Net_PL'].sum()
        total_trades = len(daily_df) # Each row is a "Day-Symbol" trade cycle
        wins = daily_df['Win'].sum()
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
        avg_pl = total_pl / total_trades if total_trades > 0 else 0
        
        return {
            "total_pl": total_pl,
            "win_rate": win_rate,
            "total_trades": total_trades,
            "avg_pl": avg_pl
        }
