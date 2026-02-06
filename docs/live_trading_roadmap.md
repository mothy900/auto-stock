# Live Trading Roadmap

## Phase 1: Paper Trading Verification (Current)
**Duration**: 2 Weeks (min)
**Criteria for Advancement**:
1. **Connectivity**: >99.9% Uptime (No crashing for 1 week).
2. **Execution**: No missing orders vs Signals.
3. **Data**: Confirm target prices match manual checks (use `check_status.py`).
4. **Win Rate**: Volatility Breakout typically aims for 40-50% win rate with high Risk:Reward. Ensure R:R > 1.5.

## Phase 2: Risk Management Setup
Before live money, implement hard constraints:
1. **Max Daily Loss**: Stop trading if equity drops > 2% in a day.
2. **Position Sizing**: Start with 10% of capital per symbol (not all-in).
3. **Emergency**: Verify "Halt" button works instantly.

## Phase 3: Live Deployment (Small Cap)
1. **Account**: Fund Alpaca Live Account.
2. **Config**:
   - Change `.env` to Live URL.
   - Set `ALPACA_API_KEY` to Live Key.
   - **Reduce Position Size**: Set `INVESTMENT_PER_SYMBOL` to min ($100 or 1 share) for first 3 days.
3. **Monitor**:
   - Watch the first 3 opens (09:30-09:35) like a hawk.
   - Compare `Main` logs with `Alpaca Dashboard`.

## Phase 4: Scaling
- If Week 1 Live is positive/stable, increase size to standard model.
- Enable automatic performance reporting.
