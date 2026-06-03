import streamlit as st
import pandas as pd
from datetime import date, timedelta
from utils.data_fetcher import fetch_stock_data
from modules.module_1_summary import render_module_1
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
st.set_page_config(
    page_title="Risk Analytics Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Premium Dark Theme Styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    /* Global font and background */
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
        background: linear-gradient(135deg, #0d0f12 0%, #11141a 100%);
        color: #e2e8f0;
    }
    
    .stApp {
        background-color: transparent;
        padding: 2rem;
    }
    
    /* Glassmorphism Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(17,20,26,0.85) !important;
        backdrop-filter: saturate(180%) blur(12px);
        border-right: 1px solid #1e293b;
        border-radius: 0 12px 12px 0;
        transition: transform 0.3s ease;
    }
    [data-testid="stSidebar"]:hover {
        transform: translateX(2px);
    }
    
    /* Metric cards */
    div[data-testid="stMetricValue"] {
        font-size: 28px !important;
        font-weight: 700 !important;
        color: #ffffff !important;
        transition: color 0.3s ease;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 14px !important;
        color: #94a3b8 !important;
        font-weight: 500 !important;
    }
    div[data-testid="stMetricContainer"]:hover div[data-testid="stMetricValue"] {
        color: #38bdf8;
    }
    
    /* Module header with fade-in */
    .module-header {
        font-size: 26px;
        font-weight: 700;
        color: #38bdf8;
        margin-bottom: 20px;
        border-bottom: 2px solid #1e293b;
        padding-bottom: 8px;
        animation: fadeIn 0.8s ease-out;
    }
    
    /* Button styling */
    .stButton button {
        background: linear-gradient(135deg, #38bdf8, #0ea5e9);
        border: none;
        color: #ffffff;
        padding: 0.6rem 1.4rem;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(56,189,248,0.4);
    }
    
    /* Fade-in animation */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    </style>
    """, unsafe_allow_html=True)

# -----------------
# Sidebar UI Controls
# -----------------
st.sidebar.markdown("<h2 style='text-align: center; color: #38bdf8;'>🛡️ Risk Dashboard</h2>", unsafe_allow_html=True)
st.sidebar.markdown("---")

TICKERS = [
    "-- Select a Ticker --",
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS",
    "WIPRO.NS", "ICICIBANK.NS", "SBIN.NS", "BAJFINANCE.NS"
]
selected_ticker = st.sidebar.selectbox("Select Ticker", TICKERS, index=0)

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

selected_module_label = st.sidebar.radio(
    "Select Module to Display",
    options=list(MODULES.keys()),
    label_visibility="collapsed"
)
selected_module = MODULES[selected_module_label]

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
    st.error(f"Failed to fetch data for {selected_ticker}. Try another ticker or date range.")
    st.stop()

# Lazy data fetching: only download portfolio data if the selected module requires it
# Portfolio modules: Executive Summary (summary), Portfolio (portfolio), Stress (stress), Correlation (correlation)
port_returns = pd.DataFrame()
if selected_module in ["summary", "portfolio", "stress", "correlation"]:
    with st.spinner("Fetching portfolio data for optimization..."):
        # Filter out the dummy selection string to prevent yfinance timeouts and lag
        valid_tickers = [t for t in TICKERS if t != "-- Select a Ticker --"]
        portfolio_tickers = valid_tickers + ['GOLDBEES.NS']
        port_returns = fetch_portfolio_data(portfolio_tickers, start_date=start_date, end_date=end_date)
        if not port_returns.empty:
            # Simulate low-volatility bond returns
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

# Dispatch to Selected Module
if selected_module == "summary":
    render_module_1(df, selected_ticker, port_returns)
elif selected_module == "arima":
    render_module_2(df)
elif selected_module == "garch":
    render_module_3(df)
elif selected_module == "dcf":
    render_module_4(selected_ticker)
elif selected_module == "monte_carlo":
    render_module_5(df)
elif selected_module == "var":
    render_module_6(df)
elif selected_module == "credit_risk":
    render_module_7(selected_ticker)
elif selected_module == "portfolio":
    render_module_8(port_returns)
elif selected_module == "stress":
    render_module_9(port_returns)
elif selected_module == "correlation":
    render_module_10(port_returns)

st.markdown("---")
st.markdown("<p style='text-align: center; color: #475569;'>MCA Financial Analytics Capstone Project Dashboard</p>", unsafe_allow_html=True)
