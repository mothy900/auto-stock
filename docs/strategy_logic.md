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
    *   It tests K values from `0.1` to `0.9` to simulate: *"If I traded with this K, what would be the return?"*
    *   The K value with the highest cumulative return is selected for today.
    *   *Effect: In volatile markets, K increases (harder to buy). In trending markets, K decreases (easier to buy).*
*   **Action 2: Position Sizing**
    *   **Formula**: `(Total Buying Power * 0.90) / 12 Symbols`
    *   It allocates capital equally, leaving a 10% safety buffer for slippage and fees.

### 🚀 B. Market Open (Entry Logic)
*   **Time**: 09:30 ET ~ 15:55 ET.
*   **Target Calculation**:
    ```math
    Target Price = Today's Open Price + (Yesterday's Range × Optimized K)
    ```
    *(Range = Yesterday High - Yesterday Low)*
*   **Buy Condition**:
    *   Wait primarily.
    *   **IF** `Current Price` >= `Target Price` **THEN** Market Buy immediately.
    *   **Logic**: "The price has surged enough to confirm a strong upward trend."
*   **Frequency**: Maximum **1 Entry per day** per symbol.

### 🛑 C. Market Close (Exit Logic)
*   **Time**: 15:55 ET (5 minutes before official close).
*   **Action**: **Liquidate All Positions (Market Sell)**.
*   **Reason**:
    *   Eliminate **Overnight Risk** (gap downs next morning).
    *   Compounding is reset daily.
*   **Stop-Loss / Take-Profit**:
    *   Currently **Disabled**.
    *   Logic: "Let profits run until the end of the day." (Intraday volatility is noise).

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
