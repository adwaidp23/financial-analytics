# Financial Risk Analytics Dashboard

A fully functional, interactive Risk Analytics Dashboard replicating a professional Fintech Risk Engineering tool. Built for the MCA Financial Analytics Capstone Project.

## Project Overview
This Streamlit-based dashboard provides comprehensive risk analytics, financial forecasting, and portfolio optimization across 10 core modules. It supports live ticker switching across NSE/BSE-listed equities and auto-refreshes all charts and KPIs.

## Features (10 Modules)
- **Module 1: Executive Summary** - Live KPI panel with Price, Forecasts, Intrinsic Value, Returns, VaR, PD, Sharpe, and an algorithmic Investment Signal.
- **Module 2: ARIMA Forecasting** - Walk-forward validated 90-day price forecasting using `pmdarima`.
- **Module 3: GARCH Volatility** - Conditional volatility modeling and dynamic regime detection.
- **Module 4: DCF Valuation** - Interactive Discounted Cash Flow waterfall with Margin of Safety.
- **Module 5: Monte Carlo Simulation** - Geometric Brownian Motion (GBM) probability paths.
- **Module 6: Value at Risk (VaR)** - Historical, Parametric, and Monte Carlo VaR with CVaR and Kupiec Backtesting.
- **Module 7: Credit Risk Modeling** - Logistic regression Probability of Default (PD) scoring and 15-month trend simulation.
- **Module 8: Portfolio Optimization** - Max Sharpe Ratio Efficient Frontier with dynamic asset toggles.
- **Module 9: Stress Testing** - Factor-beta based scenario analysis and risk narrative.
- **Module 10: Correlation Heatmap** - Asset co-movement detection and diversification insights.

## Setup Instructions
1. Clone the repository.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```

## Technology Stack
- **Frontend / Framework**: Streamlit, Plotly
- **Data Acquisition**: yfinance, pandas
- **Quantitative Modeling**: pmdarima, arch, scipy, scikit-learn, numpy

## Academic Integrity
This project was developed adhering to all capstone guidelines. 
*Note: AI tools were utilized during development for code architecture and troubleshooting, as permitted.*
