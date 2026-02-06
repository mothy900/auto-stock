# 🧠 Antigravity Trading Algorithm Specification
> **Strategy**: Volatility Breakout (Larry Williams)
> **Objective**: Capture strong intraday trends while avoiding overnight risk.

---

## 1. Core Philosophy
This bot operates on the principle that **"yesterday's range predicts today's momentum."**
It does not predict the direction (up/down) in advance. instead, it waits for the market to move significantly in one direction and then "rides the wave."

## 2. Trading Workflow

### 🌅 A. Pre-Market (Daily Initialization)
*   **Time**: Every morning before 09:30 ET.
*   **Action 1: Calculate K-Value (Dynamic Optimization)**
    *   The bot analyzes the last **30 days** of data for each symbol.
    *   It tests K values from `0.3` to `0.9` (updated from 0.1 for stability).
    *   The K value with the highest cumulative return is selected for today.
*   **Action 2: Trend Filter Calculation**
    *   Calculates the **20-day Simple Moving Average (SMA)**.
    *   *Rule*: If Current Price < 20-day SMA, trade entry is suppressed (Bear Market Filter).

### 🚀 B. Market Open (Entry Logic)
*   **Time**: 09:30 ET ~ 15:55 ET.
*   **Buy Condition**:
    *   **Price Condition**: `Current Price` >= `Target Price` (Open + Range * K)
    *   **Trend Condition**: `Current Price` > `20-day SMA` (Must be in uptrend)
    *   **Action**: Market Buy immediately.

### 🛑 C. Risk Management (Exit Logic)
*   **1. Stop-Loss (New)**:
    *   If current price drops **-3%** below average entry price -> **Immediate Market Sell**.
    *   Protects against sudden intraday crashes.
*   **2. Time-Cut (Standard)**:
    *   **Time**: 15:55 ET.
    *   All remaining positions are closed to avoid overnight risk.

---

## 3. Supported Symbols (The Volatility 12)
The bot monitors high-beta (high volatility) stocks across sectors:
*   **Tech/AI**: `NVDA`, `TSLA`, `AMD`, `PLTR`, `INOD`
*   **Semiconductors**: `SOXL` (3x Bull)
*   **Nasdaq 100**: `TQQQ` (3x Bull)
*   **Healthcare**: `HROW`, `SGRY`
*   **Finance/Energy**: `TIGR`, `PAYO`, `DUK`

## 4. Example Scenario
1.  **Yesterday**: NVDA moved between $100 (Low) and $110 (High). Range = $10.
2.  **Morning**: Bot calculates optimal K = 0.5.
3.  **Target**: $5 (range $10 * 0.5) movement required.
4.  **Today Open**: NVDA starts at $105.
5.  **Target Price**: $105 + $5 = **$110**.
6.  **Action**:
    *   Price hits $108 -> No Action.
    *   Price hits $110.01 -> **BUY!**
    *   Price falls to $109 -> Hold (No Stop Loss).
    *   Price rises to $115 -> Hold.
    *   **15:55 PM**: Sell at Market Price ($115). **Profit: $5/share.**
