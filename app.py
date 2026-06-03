import streamlit as st
import pandas as pd
from datetime import date, timedelta
from utils.data_fetcher import fetch_stock_data
from modules.module_1_summary import render_module_1
from utils.theme import init_theme, get_template, apply_theme, get_css
from modules.module_2_arima import render_module_2
from modules.module_3_garch import render_module_3
from modules.module_4_dcf import render_module_4
from modules.module_5_monte_carlo import render_module_5
from modules.module_6_var import render_module_6
from modules.module_7_credit_risk import render_module_7
from modules.module_8_portfolio import render_module_8, simulate_bond_returns
from modules.module_9_stress import render_module_9
from modules.module_10_correlation import render_module_10
from utils.data_fetcher import fetch_portfolio_data

# Set Streamlit Page Configuration
init_theme()

# Theme toggle and injection
st.sidebar.checkbox("Dark Mode", value=st.session_state.dark_mode, key="dark_mode")
st.markdown(get_css(), unsafe_allow_html=True)

# -----------------
# Sidebar UI Controls
# -----------------
st.sidebar.markdown("<h2 style='text-align: center; color: #38bdf8;'>🛡️ Risk Dashboard</h2>", unsafe_allow_html=True)
st.sidebar.markdown("---")

TICKER_INPUT = st.sidebar.text_input("Enter Ticker (e.g., RELIANCE.NS)", value="")
# Validate ticker
if TICKER_INPUT:
    try:
        from utils.ticker_input import get_valid_ticker
        selected_ticker = get_valid_ticker(TICKER_INPUT)
        if not selected_ticker:
            st.error(f"Ticker '{TICKER_INPUT}' is invalid or data not available.")
            st.stop()
    except Exception as e:
        st.error(f"Error validating ticker: {e}")
        st.stop()
else:
    st.markdown("### 👆 Enter a ticker in the sidebar to begin")
    st.info("Provide a valid NSE ticker symbol, e.g., RELIANCE.NS")
    st.stop()

# ... (keep date range etc.)
# Replace module dispatch with try/except
if selected_module == "summary":
    try:
        render_module_1(df, selected_ticker, port_returns)
    except Exception as e:
        st.error(f"Error in Executive Summary: {e}")
elif selected_module == "arima":
    try:
        render_module_2(df)
    except Exception as e:
        st.error(f"Error in ARIMA module: {e}")
elif selected_module == "garch":
    try:
        render_module_3(df)
    except Exception as e:
        st.error(f"Error in GARCH module: {e}")
elif selected_module == "dcf":
    try:
        render_module_4(selected_ticker)
    except Exception as e:
        st.error(f"Error in DCF module: {e}")
elif selected_module == "monte_carlo":
    try:
        render_module_5(df)
    except Exception as e:
        st.error(f"Error in Monte Carlo module: {e}")
elif selected_module == "var":
    try:
        render_module_6(df)
    except Exception as e:
        st.error(f"Error in VaR module: {e}")
elif selected_module == "credit_risk":
    try:
        render_module_7(selected_ticker)
    except Exception as e:
        st.error(f"Error in Credit Risk module: {e}")
elif selected_module == "portfolio":
    try:
        render_module_8(port_returns)
    except Exception as e:
        st.error(f"Error in Portfolio module: {e}")
elif selected_module == "stress":
    try:
        render_module_9(port_returns)
    except Exception as e:
        st.error(f"Error in Stress module: {e}")
elif selected_module == "correlation":
    try:
        render_module_10(port_returns)
    except Exception as e:
        st.error(f"Error in Correlation module: {e}")

if selected_ticker == "-- Select a Ticker --":
    st.markdown("### 👆 Select a ticker from the sidebar to begin")
    st.info("Choose a stock from the sidebar dropdown to load the Risk Analytics Dashboard.")
    st.stop()

default_end = date.today()
default_start = default_end - timedelta(days=2 * 365) # Last 2 years default
date_range = st.sidebar.date_input("Select Date Range", value=(default_start, default_end))

st.sidebar.markdown("---")
st.sidebar.markdown("<h4 style='color: #94a3b8;'>Navigate Modules</h4>", unsafe_allow_html=True)

MODULES = {
    "📊 Executive Summary": "summary",
    "📈 ARIMA Forecasting (M2)": "arima",
    "⚡ GARCH Volatility (M3)": "garch",
    "💸 DCF Valuation (M4)": "dcf",
    "🎲 Monte Carlo Simulation (M5)": "monte_carlo",
    "📉 Value at Risk & CVaR (M6)": "var",
    "🛡️ Credit Risk Modeling (M7)": "credit_risk",
    "💼 Portfolio Optimization (M8)": "portfolio",
    "🌋 Stress Testing (M9)": "stress",
    "🕸️ Correlation Heatmap (M10)": "correlation"
}

# ----- Top Tab Bar -----



st.sidebar.markdown("---")
st.sidebar.info("Data auto-refreshes when selections change.")

# Validate Date Range
if len(date_range) != 2:
    st.error("Please select a valid start and end date.")
    st.stop()
start_date, end_date = date_range

# -----------------
# Data Fetching Pipeline
# -----------------
with st.spinner(f"Fetching price data for {selected_ticker}..."):
    df = fetch_stock_data(selected_ticker, start_date=start_date, end_date=end_date)
    
if df.empty:
    st.error(f"Failed to fetch data for {selected_ticker}.")
    st.stop()

# KPI Sticky Header (computes latest price and daily change)
if not df.empty and 'Close' in df.columns:
    last_price = df['Close'].iloc[-1]
    prev_price = df['Close'].iloc[-2] if len(df) > 1 else last_price
    delta = ((last_price - prev_price) / prev_price * 100) if prev_price else 0
else:
    last_price = 0
    delta = 0

st.markdown(
    f"""<div class="kpi-header">
            <div class="kpi-card"><h3>{selected_ticker}</h3></div>
            <div class="kpi-card"><h3>{last_price:.2f}</h3><p>{delta:+.2f}%</p></div>
        </div>""",
    unsafe_allow_html=True,
)

# Lazy data fetching: always download portfolio data (used by several modules)
port_returns = pd.DataFrame()
with st.spinner("Fetching portfolio data for optimization..."):
    valid_tickers = [t for t in TICKERS if t != "-- Select a Ticker --"]
    portfolio_tickers = valid_tickers + ['GOLDBEES.NS']
    port_returns = fetch_portfolio_data(portfolio_tickers, start_date=start_date, end_date=end_date)
    if not port_returns.empty:
        bond_ret = simulate_bond_returns(port_returns.index)
        port_returns['BOND_SIM'] = bond_ret
    else:
        st.warning("Failed to fetch portfolio data. Portfolio metrics will use fallbacks.")

# -----------------
# Main Content Area
# -----------------
st.markdown(f"<h1 style='color: #ffffff; margin-bottom: 0;'>{selected_ticker} Risk Analytics</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='color: #64748b;'>Date Range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}</p>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

    # Dispatch modules inside top tabs after data is ready
    tabs = st.tabs(list(MODULES.keys()))
    for label, tab in zip(MODULES.keys(), tabs):
        with tab:
            module_key = MODULES[label]
            if module_key == "summary":
                render_module_1(df, selected_ticker, port_returns)
            elif module_key == "arima":
                render_module_2(df)
            elif module_key == "garch":
                render_module_3(df)
            elif module_key == "dcf":
                render_module_4(selected_ticker)
            elif module_key == "monte_carlo":
                render_module_5(df)
            elif module_key == "var":
                render_module_6(df)
            elif module_key == "credit_risk":
                render_module_7(selected_ticker)
            elif module_key == "portfolio":
                render_module_8(port_returns)
            elif module_key == "stress":
                render_module_9(port_returns)
            elif module_key == "correlation":
                render_module_10(port_returns)


st.markdown("---")
st.markdown("<p style='text-align: center; color: #475569;'>MCA Financial Analytics Capstone Project Dashboard</p>", unsafe_allow_html=True)
