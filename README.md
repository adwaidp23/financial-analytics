# Financial Risk Analytics Dashboard

A fully functional, interactive, and professional-grade Quantitative Risk Analytics and Financial Engineering Dashboard. Developed for the MCA Financial Analytics Capstone Project.

---

## 1. Project Overview & Features

This dashboard replicates a professional Fintech Risk Engineering workstation, combining statistical forecasting, structural volatility estimation, valuation models, risk forecasting, credit modeling, and portfolio construction.

### The 10 Core Analytics Modules:
1. **Executive Summary (Module 1)**: A unified live KPI cockpit showing the core ticker price, 90-day ARIMA forecast, DCF intrinsic value, Sharpe ratio, Probability of Default (PD), and Monte Carlo VaR. Integrates a rule-based algorithmic **Investment Action Signal (BUY / HOLD / SELL)** with risk level classification. Includes 3 new live market metrics (Beta, Jensen's Alpha, and $R^2$) computed against the NIFTY50 (^NSEI) index.
2. **ARIMA Price Forecasting (Module 2)**: Fits an Auto-ARIMA model (`pmdarima`) on daily stock close prices, estimates optimal $(p, d, q)$ orders, and forecasts prices 90 days out with a 95% confidence interval. Includes a walk-forward validation framework (80/20 train/test split) comparing in-sample vs. out-of-sample Root Mean Squared Error (RMSE) displayed side-by-side.
3. **GARCH Volatility Modeling (Module 3)**: Fits a GARCH(1,1) model using the `arch` library to estimate conditional daily/annualized volatility, and compares it to a 20-day rolling historical volatility. Outputs model parameters ($\omega, \alpha, \beta$), calculates persistence ($\alpha + \beta$), and provides an automated **Stationarity Validation Check** ($\alpha + \beta < 1$).
4. **DCF Valuation (Module 4)**: A structured Discounted Cash Flow valuation tool using annual Free Cash Flow / Operating Cash Flow, shares outstanding, and user-defined discount rates (WACC) and terminal growth rates. Displays a Plotly Waterfall chart highlighting short-term cash flow PVs (green), Terminal Value PV (blue), and total Enterprise Value (purple).
5. **Monte Carlo GBM Simulation (Module 5)**: Simulates 1,000+ asset price paths over a 1-year horizon (252 trading days) using Geometric Brownian Motion (GBM). Categorizes path outcomes into Bear Case (bottom 5%), Bull Case (top 5%), and Median 90% paths. Efficiently pools paths to avoid browser DOM lag.
6. **Value at Risk (VaR) & CVaR (Module 6)**: Computes 1-day VaR at 95% and 99% confidence levels using three distinct methodologies: Historical Simulation, Parametric Normal, and Monte Carlo (10,000 paths). Computes Expected Shortfall (CVaR) and performs a **Kupiec Proportion of Failures (POF) Likelihood Ratio Test** to validate model adequacy over the last 252 trading days.
7. **Credit Risk Modeling (Module 7)**: Trains a Logistic Regression model on corporate financial ratios (Debt-to-Equity, Interest Coverage, Current Ratio, ROE, Net Profit Margin) to estimate the Probability of Default (PD). Maps PD to a standard credit score (300-850), assigns a credit rating grade (AAA to D), displays performance metrics (AUC-ROC, Confusion Matrix), and runs a 15-month dynamic forward-looking PD simulation under shocks.
8. **Portfolio Optimization (Module 8)**: Implements Markowitz Mean-Variance Portfolio Optimization. Uses a Monte Carlo simulation of 5,000 random portfolios to build and visualize the **Efficient Frontier**. Dynamically optimizes for the Max Sharpe Ratio portfolio and displays the optimal weights in an interactive Pie chart.
9. **Stress Testing & Factor Analysis (Module 9)**: Conducts macro factor stress testing (Market Crash, Interest Rate Hike, Oil Shock, Recession, Best Case, and a User-Defined Custom Shock). Computes portfolio returns under shocks based on asset factor-betas, and generates an automated risk narrative and hedging recommendation.
10. **Correlation Heatmap (Module 10)**: Computes and visualizes the Pearson correlation matrix of daily log returns for all portfolio assets. Automatically flags highly redundant asset pairs ($|\rho| > 0.70$) with a warning annotation (`⚠️`) on the heatmap, and identifies the most diversifying and redundant asset pairs.

---

## 2. Data Sources & Integration

- **Equity Prices**: Fetched dynamically via the Yahoo Finance API (`yfinance`) with a 5-year lookback period. Supported tickers include major Indian blue-chips: `RELIANCE.NS`, `TCS.NS`, `INFY.NS`, `HDFCBANK.NS`, `WIPRO.NS`, `ICICIBANK.NS`, `SBIN.NS`, `BAJFINANCE.NS`.
- **Market Benchmark**: NIFTY50 index (`^NSEI`) returns are fetched dynamically over the identical stock lookback period to compute regression statistics (Beta, Jensen's Alpha, and $R^2$) and stress-testing market factors.
- **Financial Statements**: Ticker cash flows, shares outstanding, and leverage/liquidity metrics are extracted from annual balance sheets and income statements via yfinance.
- **Bulletproof Fallback System**: To bypass API rate-limiting or service outages, high-quality, stock-specific defaults based on actual corporate reports are cached in the data-fetcher layer, ensuring 100% dashboard uptime.
- **Performance Caching**: All yfinance API calls and computationally heavy operations are cached using `@st.cache_data(ttl=300)` to optimize load times and prevent API throttling.

---

## 3. Quantitative Model Assumptions & Formulations

### A. ARIMA Forecasting (Module 2)
The model assumes that future asset prices are a linear function of past close prices (Auto-regressive) and past forecast errors (Moving average).
- **Formulation**: $X_t = c + \sum_{i=1}^p \phi_i X_{t-i} + \varepsilon_t + \sum_{j=1}^q \theta_j \varepsilon_{t-j}$ where $X_t$ is the differenced series.
- **Assumptions**: Differencing parameter $d$ is determined via KPSS/ADF tests to enforce stationarity. Search space for $(p, d, q)$ is restricted to $p, q \le 3$ for low latency.

### B. GARCH Volatility (Module 3)
Estimates conditional variance to capture "volatility clustering" (periods of turbulence followed by turbulence).
- **Formulation (GARCH(1,1))**: $\sigma_t^2 = \omega + \alpha \varepsilon_{t-1}^2 + \beta \sigma_{t-1}^2$
- **Stationarity & Parameter Constraint**:
  - $\omega > 0, \alpha \ge 0, \beta \ge 0$
  - $\alpha + \beta$ represents the persistence of a volatility shock. If $\alpha + \beta < 1$, the variance process is stationary and reverts to its long-run average.

### C. Discounted Cash Flow (Module 4)
Assumes the value of a business is the present value of its future free cash flows.
- **Formulation**: $\text{Intrinsic Value} = \frac{1}{S} \left[ \sum_{t=1}^N \frac{\text{FCF}_0 \cdot (1+g_{\text{short}})^t}{(1+\text{WACC})^t} + \frac{\text{FCF}_N \cdot (1+g_{\text{term}})}{(\text{WACC} - g_{\text{term}}) \cdot (1+\text{WACC})^N} \right]$
- **Assumptions**: Short-term growth ($g_{\text{short}}$) is assumed to be 10%. Shares outstanding $S$ and initial FCF are fetched dynamically.

### D. Geometric Brownian Motion (Module 5)
Prices are assumed to follow a continuous stochastic process where log returns are normally distributed.
- **Formulation**: $dS_t = \mu S_t dt + \sigma S_t dW_t$
- **Discretized Scheme**: $S_{t+\Delta t} = S_t \exp\left( \left(\mu - \frac{\sigma^2}{2}\right)\Delta t + \sigma \sqrt{\Delta t} Z \right), \quad Z \sim N(0, 1)$
- **Assumptions**: Drift ($\mu$) and volatility ($\sigma$) are constant, and there are no jumps in prices.

### E. Kupiec POF Backtesting (Module 6)
Validates the accuracy of the 95% Parametric VaR model. It checks if the number of actual losses exceeding the VaR (exceptions) is statistically consistent with the nominal 5% rate.
- **Formulation (Likelihood Ratio Test)**:
  $LR = -2 \ln \left[ \frac{p^{x}(1-p)^{N-x}}{\hat{p}^{x}(1-\hat{p})^{N-x}} \right] \sim \chi^2(1)$
  where $p = 1 - \alpha = 0.05$, $x$ is the count of exceptions, $N$ is the number of trading days (252), and $\hat{p} = x/N$.
- **Hypothesis**: Reject the model as invalid if the p-value $\le 0.05$.

### F. Credit Risk Logistic Regression (Module 7)
Models default probability as a logistic function of leverage, liquidity, and profitability metrics.
- **Formulation**: $P(\text{Default} = 1 \mid \mathbf{X}) = \frac{1}{1 + e^{-\mathbf{\beta}^T \mathbf{X}}}$
  where $\mathbf{X}$ represents: Debt/Equity, Interest Coverage, Current Ratio, ROE, Net Profit Margin.

### G. Portfolio Markowitz Mean-Variance Optimization (Module 8)
- **Objective**: Maximize Sharpe Ratio: $\max_{\mathbf{w}} \frac{\mathbf{w}^T \mathbf{\mu} - R_f}{\sqrt{\mathbf{w}^T \mathbf{\Sigma} \mathbf{w}}}$ subject to $\sum w_i = 1$ and $w_i \ge 0$.

---

## 4. Model Limitations & Edge Cases

1. **ARIMA Stationarity & Linearity**: ARIMA assumes linear relationships and constant variance. In hyper-volatile markets or structural regime shifts (e.g., pandemics, regulatory changes), ARIMA forecasts revert heavily to the mean and fail to predict sudden spikes.
2. **GBM Non-Clustered Volatility**: GBM assumes constant volatility ($\sigma$) and constant drift ($\mu$). In reality, stock volatilities are time-varying, show clustering (GARCH behavior), and asset return distributions have "fat tails" (kurtosis) that GBM underestimates.
3. **DCF Sensitivity**: The DCF model is extremely sensitive to changes in WACC and the Terminal Growth Rate. A 0.5% variance in WACC can swing the intrinsic value per share by $\pm 20\%$.
4. **Credit Model Synthetic Ratios**: Because Indian financial firms and banks do not publish standardized ratios in a single, simple API format, yfinance data can sometimes contain gaps. While the fallback handles this, actual live credit assessments require detailed audited reports.
5. **GARCH Convergence Failures**: When an asset experiences prolonged flat pricing or extremely extreme non-normal returns, the optimization solver for the GARCH likelihood function can fail to converge. The module implements a robust rolling-historical volatility fallback for this edge case.

---

## 5. Setup & Running Instructions

### Prerequisites
- Python 3.10, 3.11, or 3.12 (Python 3.12.3 recommended)
- A terminal (PowerShell, bash, etc.)

### Installation Steps
1. Clone the repository and navigate to the project directory:
   ```bash
   git clone <repo-url>
   cd Financial_Analytics
   ```
2. Set up a Python virtual environment (recommended):
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install the exact pinned dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the dashboard application:
   ```bash
   python -m streamlit run app.py
   ```

---

## 6. Future Work & Enhancements

- **Copula-Based Portfolio VaR**: Replace linear Pearson correlation with Copula functions (e.g., Clayton or Gumbel Copulas) to model tail dependencies and joint default/loss probabilities more accurately during extreme market stress.
- **Deep Learning Forecasting**: Integrate Recurrent Neural Networks (RNN) and Long Short-Term Memory (LSTM) networks to capture non-linear temporal dependencies in stock prices, replacing the linear ARIMA model.
- **Black-Litterman Asset Allocation**: Enhance the Markowitz portfolio optimization module by incorporating subjective investor views combined with market equilibrium weights, resulting in more stable and realistic allocations.
- **Multi-Factor Structural Credit Models**: Implement structural credit models (like the Merton model) where equity is treated as a call option on the company's assets, instead of a purely static logistic regression approach.

---

## 7. AI Usage Declaration

This project was built using AI pair-programming tools. 
- **Code Generation & Optimization**: AI tools were utilized to generate the initial file skeleton, build quantitative mathematical formulations (GBM paths, Kupiec Likelihood Ratio formula, SLSQP solver setup), and optimize plotly heatmap annotation rendering to avoid browser lag.
- **Refactoring & Code Quality**: AI was used to draft standard Google-style docstrings, pin requirements to exact versions, and structure clean exception fallbacks.
- **Validation**: All quantitative outputs, logic blocks, and Streamlit components were manually verified and tested for correctness by the developer.

---

## 8. Contributor Information

- **Developer Name**: [Your Name / Student Name]
- **Student ID / Roll No**: [Your Roll Number]
- **Course**: MCA (Master of Computer Applications)
- **Specialization / Batch**: Financial Analytics / 2026 Batch
- **Institution**: [Your University/Institution]
- **Project Advisor**: [Advisor Name]
- **Date of Submission**: May 27, 2026
