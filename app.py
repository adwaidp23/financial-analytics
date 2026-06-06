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

# The banner is removed; we will use a unified top header after data is fetched

# -----------------
# Sidebar UI Controls
# -----------------
st.sidebar.markdown("""
<div class='sidebar-logo-container'>
    <div class='sidebar-logo-icon'>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M2 22L12 2L22 22H2Z" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
    </div>
    <div class='sidebar-logo-text'>RISK TERMINAL</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("<span class='sidebar-label'>TICKER SELECTION</span>", unsafe_allow_html=True)

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
st.sidebar.markdown("<span class='sidebar-label' style='margin-top:20px;'>DATE RANGE</span>", unsafe_allow_html=True)
date_range = st.sidebar.date_input("", value=(default_start, default_end), label_visibility="collapsed")

st.sidebar.markdown("<hr style='border-color: #2A2E39; margin: 20px 0;'>", unsafe_allow_html=True)
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

# ----- Sidebar Navigation -----
st.sidebar.markdown("<div class='sidebar-nav'>", unsafe_allow_html=True)
for label, key in MODULES.items():
    st.sidebar.markdown(f"<a href='#{key}' style='display: block; padding: 10px 15px; color: #9CA3AF; text-decoration: none; font-size: 13px; font-weight: 500; border-radius: 6px; margin-bottom: 4px; transition: all 0.2s;' onmouseover=\"this.style.background='rgba(255,255,255,0.05)'; this.style.color='#fff'\" onmouseout=\"this.style.background='transparent'; this.style.color='#9CA3AF'\">{label}</a>", unsafe_allow_html=True)
st.sidebar.markdown("</div>", unsafe_allow_html=True)
st.sidebar.markdown("<hr style='border-color: #2A2E39; margin: 20px 0;'>", unsafe_allow_html=True)
if st.sidebar.button("Refresh Dashboard", use_container_width=True):
    st.rerun()
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

# Mockup Header
if not df.empty and 'Close' in df.columns:
    last_price = df['Close'].iloc[-1]
    prev_price = df['Close'].iloc[-2] if len(df) > 1 else last_price
    delta = ((last_price - prev_price) / prev_price * 100) if prev_price else 0
    price_change_class = "positive" if delta >= 0 else "negative"
    price_change_sign = "+" if delta >= 0 else ""
else:
    last_price = 0
    delta = 0
    price_change_class = "positive"
    price_change_sign = "+"

# Basic mock for signal
if delta > 1.0:
    signal = "STRONG BUY"
    signal_class = "buy"
elif delta < -1.0:
    signal = "SELL"
    signal_class = "sell"
else:
    signal = "HOLD"
    signal_class = "hold"

st.markdown(
    f"""
    <div class="mockup-header">
        <div class="header-left">
            <h1>{selected_ticker.replace('.NS', '')} LTD</h1>
            <div class="tags">
                <span>NSE: {selected_ticker.replace('.NS', '')}</span>
                <span style="color: #4B5563;">|</span>
                <span class="market-open">MARKET OPEN</span>
            </div>
        </div>
        <div class="header-right">
            <div class="header-price">
                <span class="label">LAST PRICE</span>
                <span class="value">₹{last_price:,.2f}</span>
                <span class="change {price_change_class}">{price_change_sign}{delta:.2f}% (Today)</span>
            </div>
            <div class="header-signal">
                <span class="label">INVESTMENT SIGNAL</span>
                <span class="signal-box {signal_class}">{signal}</span>
            </div>
        </div>
    </div>
    """,
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

# Continuous Grid Layout
st.markdown("<div id='summary'></div>", unsafe_allow_html=True)
render_module_1(df, selected_ticker, port_returns)

st.markdown("<br><div id='arima'></div><div id='garch'></div>", unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    render_module_2(df)
with col2:
    render_module_3(df)

st.markdown("<br><div id='dcf'></div>", unsafe_allow_html=True)
render_module_4(selected_ticker)

st.markdown("<br><div id='monte_carlo'></div><div id='var'></div>", unsafe_allow_html=True)
col3, col4 = st.columns(2)
with col3:
    render_module_5(df)
with col4:
    render_module_6(df)

st.markdown("<br><div id='credit_risk'></div><div id='portfolio'></div>", unsafe_allow_html=True)
col5, col6 = st.columns(2)
with col5:
    render_module_7(selected_ticker)
with col6:
    render_module_8(port_returns)

st.markdown("<br><div id='stress'></div><div id='correlation'></div>", unsafe_allow_html=True)
col7, col8 = st.columns(2)
with col7:
    render_module_9(port_returns)
with col8:
    render_module_10(port_returns)


st.markdown("---")
st.markdown("<p style='text-align: center; color: #475569;'>MCA Financial Analytics Capstone Project Dashboard</p>", unsafe_allow_html=True)
