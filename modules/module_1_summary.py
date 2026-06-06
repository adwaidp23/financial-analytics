import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import yfinance as yf
from modules.module_2_arima import run_arima_model
from modules.module_4_dcf import fetch_cash_flow
from modules.module_7_credit_risk import generate_and_train_pd_model, fetch_financial_ratios
from modules.module_8_portfolio import optimize_portfolio

def make_svg_sparkline(data, color):
    """Generates an SVG sparkline from data."""
    if len(data) < 2: return ""
    data_list = list(data)
    min_d, max_d = min(data_list), max(data_list)
    range_d = max_d - min_d if max_d != min_d else 1
    points = []
    for i, v in enumerate(data_list):
        x = i * (100 / (len(data_list) - 1))
        y = 35 - ((v - min_d) / range_d * 30) # leave 5px margin top/bottom
        points.append(f"{x},{y}")
    pts_str = " ".join(points)
    return f"""<svg width="100" height="40" viewBox="0 0 100 40" xmlns="http://www.w3.org/2000/svg">
        <polyline points="{pts_str}" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>"""

def render_module_1(df, selected_ticker, port_returns):
    """Renders the Executive Summary matching the mockup."""
    
    # 1. Fetch values
    current_price = df['Close'].iloc[-1]
    
    with st.spinner("Aggregating module outputs for Executive Summary..."):
        try:
            results = run_arima_model(df)
            forecast_df = results[0]
            forecasted_price = forecast_df['Forecast'].iloc[-1]
            forecast_data = forecast_df['Forecast'].values
        except:
            forecasted_price = current_price * 1.05
            forecast_data = [current_price, forecasted_price]
            
    recent_cf, current_price_dcf, shares_out = fetch_cash_flow(selected_ticker)
    wacc = 0.10
    term_growth = 0.03
    forecast_years = 5
    cf_forecast = []
    current_cf = recent_cf
    for i in range(1, forecast_years + 1):
        current_cf = current_cf * 1.10
        cf_forecast.append(current_cf)
    pv_cf = sum([cf / ((1 + wacc) ** i) for i, cf in enumerate(cf_forecast, 1)])
    tv = cf_forecast[-1] * (1 + term_growth) / (wacc - term_growth)
    pv_tv = tv / ((1 + wacc) ** forecast_years)
    if shares_out <= 0: shares_out = 100000000
    intrinsic_value = (pv_cf + pv_tv) / shares_out
    
    # Generate Sparklines
    curr_sparkline = make_svg_sparkline(df['Close'].tail(30).values, '#22C55E')
    forecast_sparkline = make_svg_sparkline(forecast_data, '#38BDF8')
    dcf_sparkline = make_svg_sparkline(np.linspace(current_price, intrinsic_value, 10), '#22C55E' if intrinsic_value > current_price else '#EF4444')
    
    # 1a. Top 3 Cards
    cards_html = f"""
    <div class="summary-cards-container">
        <div class="summary-card">
            <div class="summary-card-left">
                <span class="summary-card-label">CURRENT PRICE</span>
                <span class="summary-card-value">₹{current_price:,.2f}</span>
            </div>
            <div class="summary-card-right">{curr_sparkline}</div>
        </div>
        <div class="summary-card">
            <div class="summary-card-left">
                <span class="summary-card-label">FORECASTED (ARIMA)</span>
                <span class="summary-card-value">₹{forecasted_price:,.2f}</span>
            </div>
            <div class="summary-card-right">{forecast_sparkline}</div>
        </div>
        <div class="summary-card">
            <div class="summary-card-left">
                <span class="summary-card-label">DCF INTRINSIC VALUE</span>
                <span class="summary-card-value">₹{intrinsic_value:,.2f}</span>
            </div>
            <div class="summary-card-right">{dcf_sparkline}</div>
        </div>
    </div>
    """
    st.markdown(cards_html, unsafe_allow_html=True)
    
    # 1b: 6 live metrics
    returns = df['Log_Return'].dropna()
    exp_return_1y = returns.mean() * 252 * 100
    
    if not port_returns.empty:
        opt_w, port_ret, port_vol, port_sharpe = optimize_portfolio(port_returns)
        port_ret = port_ret * 100
        port_vol = port_vol * 100
    else:
        port_ret, port_vol, port_sharpe = 0.0, 0.0, 0.0
        
    var_95_pct = (np.percentile(returns, 5) if not returns.empty else -0.02) * 100
    
    try:
        model, _, _, _ = generate_and_train_pd_model()
        features_df = fetch_financial_ratios(selected_ticker)
        pd_prob = model.predict_proba(features_df)[0, 1] * 100
    except Exception:
        pd_prob = 0.05
        
    # Set colors
    er_color = "#22C55E" if exp_return_1y > 0 else "#EF4444"
    pr_color = "#22C55E" if port_ret > 0 else "#EF4444"
    vol_color = "#EF4444" if port_vol > 20 else "#F59E0B"
    var_color = "#EF4444"
    pd_color = "#22C55E" if pd_prob < 1 else "#EF4444"
    sharpe_color = "#38BDF8"
    
    metrics_html = f"""
    <div class="live-risk-bar">
        <div class="live-risk-title">LIVE RISK METRICS</div>
        <div class="live-risk-metrics">
            <div class="risk-metric-item">
                <span class="risk-metric-label">EXPECTED RETURN (1Y)</span>
                <span class="risk-metric-value" style="color: {er_color}">{exp_return_1y:+.1f}%</span>
            </div>
            <div class="risk-metric-item">
                <span class="risk-metric-label">PORTFOLIO RETURN (1Y)</span>
                <span class="risk-metric-value" style="color: {pr_color}">{port_ret:+.1f}%</span>
            </div>
            <div class="risk-metric-item">
                <span class="risk-metric-label">VOLATILITY (ANNUAL)</span>
                <span class="risk-metric-value" style="color: {vol_color}">{port_vol:.1f}%</span>
            </div>
            <div class="risk-metric-item">
                <span class="risk-metric-label">VAR 95% (1-DAY)</span>
                <span class="risk-metric-value" style="color: {var_color}">{var_95_pct:.2f}%</span>
            </div>
            <div class="risk-metric-item">
                <span class="risk-metric-label">PROB OF DEFAULT (1Y)</span>
                <span class="risk-metric-value" style="color: {pd_color}">{pd_prob:.2f}%</span>
            </div>
            <div class="risk-metric-item">
                <span class="risk-metric-label">SHARPE RATIO (1Y)</span>
                <span class="risk-metric-value" style="color: {sharpe_color}">{port_sharpe:.2f}</span>
            </div>
        </div>
    </div>
    """
    st.markdown(metrics_html, unsafe_allow_html=True)

