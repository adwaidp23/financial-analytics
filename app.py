import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
from utils.data_fetcher import fetch_stock_data
from modules.module_1_summary import render_module_1

st.set_page_config(
    page_title="Financial Risk Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Default portfolio ticker universe for portfolio and correlation modules
TICKERS = [
    'RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS',
    'ICICIBANK.NS', 'SBIN.NS', 'BAJFINANCE.NS', 'WIPRO.NS'
]
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
# The key automatically syncs with st.session_state.dark_mode (initialized in init_theme)
st.sidebar.checkbox("Dark Mode", key="dark_mode")
st.markdown(get_css(), unsafe_allow_html=True)

st.markdown(
    """
    <div class='dashboard-header'>
        <div>
            <h1>Financial Risk Analytics</h1>
            <p>Interactive market risk and portfolio analytics dashboard for Indian equities.</p>
        </div>
        <div class='dashboard-badges'>
            <span>📊 Multi-Module Risk Toolkit</span>
            <span>⚡ Live Model Insights</span>
            <span>🔒 Data-Driven Decisions</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------
# Sidebar UI Controls
# -----------------
st.sidebar.markdown("<div class='sidebar-heading'>🛡️ Risk Dashboard</div>", unsafe_allow_html=True)
st.sidebar.markdown("<div class='sidebar-description'>Use the controls below to choose a ticker, adjust the date range, and explore each analytics module.</div>", unsafe_allow_html=True)
st.sidebar.markdown("---")

ticker_selection = st.sidebar.selectbox(
    "Choose a ticker from the default universe",
    ["-- Select a Ticker --"] + TICKERS,
    index=0,
)
TICKER_INPUT = st.sidebar.text_input("Or enter a custom ticker (e.g., RELIANCE.NS)", value="")

# Resolve selected ticker with validation
try:
    from utils.ticker_input import get_valid_ticker
    if TICKER_INPUT.strip():
        selected_ticker = get_valid_ticker(TICKER_INPUT.strip())
    elif ticker_selection != "-- Select a Ticker --":
        selected_ticker = ticker_selection
    else:
        st.markdown("### 👆 Enter a ticker or select one from the sidebar to begin")
        st.info("Provide a valid NSE ticker symbol or choose one from the curated universe.")
        st.stop()
except Exception as e:
    st.error(f"Error validating ticker: {e}")
    st.stop()

# The previous sidebar dispatch using `selected_module` has been removed.
# Module rendering is now handled via the top‑tab navigation defined later.
# The variables `selected_module`, `df`, and `port_returns` are now defined later in the script.
# This placeholder ensures no NameError occurs.


default_end = date.today()
default_start = default_end - timedelta(days=2 * 365) # Last 2 years default
date_range = st.sidebar.date_input("Select Date Range", value=(default_start, default_end))

st.sidebar.markdown("---")
st.sidebar.markdown("<h4 class='sidebar-subtitle'>Navigate Modules</h4>", unsafe_allow_html=True)

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
if st.sidebar.button("Refresh Dashboard", help="Reload the dashboard with the latest ticker and date range."):
    st.experimental_rerun()
st.sidebar.markdown("<div class='sidebar-help'>Tip: Use the date range selector and module tabs to explore models interactively.</div>", unsafe_allow_html=True)
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

updated_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

st.markdown(
    f"""<div class='kpi-header'>
            <div class='kpi-card'><h3>{selected_ticker}</h3></div>
            <div class='kpi-card'><h3>₹ {last_price:.2f}</h3><p>Daily Δ {delta:+.2f}%</p></div>
            <div class='kpi-card badge-card'><span>Date Range:</span><strong>{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}</strong></div>
            <div class='kpi-card badge-card'><span>Last Refresh:</span><strong>{updated_time}</strong></div>
        </div>""",
    unsafe_allow_html=True,
)

# Lazy data fetching: always download portfolio data (used by several modules)
port_returns = pd.DataFrame()
with st.spinner("Fetching portfolio data for optimization..."):
    portfolio_tickers = [selected_ticker] + [t for t in TICKERS if t != selected_ticker]
    if 'GOLDBEES.NS' not in portfolio_tickers:
        portfolio_tickers.append('GOLDBEES.NS')
    port_returns = fetch_portfolio_data(portfolio_tickers, start_date=start_date, end_date=end_date)
    if not port_returns.empty:
        bond_ret = simulate_bond_returns(port_returns.index)
        port_returns['BOND_SIM'] = bond_ret
    else:
        st.warning("Failed to fetch portfolio data. Portfolio metrics will use fallbacks.")

# -----------------
# Main Content Area
# -----------------
st.markdown(f"<h1 class='page-title'>{selected_ticker} Risk Analytics</h1>", unsafe_allow_html=True)
st.markdown(f"<p class='page-subtitle'>A unified risk analytics experience across forecasting, valuation, portfolio, and stress-testing modules.</p>", unsafe_allow_html=True)
st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

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
