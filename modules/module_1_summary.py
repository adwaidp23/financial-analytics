import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import yfinance as yf
from modules.module_2_arima import run_arima_model
from modules.module_4_dcf import fetch_cash_flow
from modules.module_7_credit_risk import generate_and_train_pd_model, fetch_financial_ratios
from modules.module_8_portfolio import optimize_portfolio

def create_sparkline(data, color):
    fig = go.Figure(go.Scatter(y=data, mode='lines', line=dict(color=color, width=2)))
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=40,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def render_module_1(df, selected_ticker, port_returns):
    st.subheader("Module 1: Executive Summary")
    
    # 1a: Current Price, Forecasted Price, DCF Intrinsic Value
    current_price = df['Close'].iloc[-1]
    
    with st.spinner("Aggregating module outputs for Executive Summary..."):
        try:
            results = run_arima_model(df)
            forecast_df = results[0]
            forecasted_price = forecast_df['Forecast'].iloc[-1]
        except:
            forecasted_price = current_price * 1.05 # fallback
            
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
    # Ensure shares outstanding is safe
    if shares_out <= 0:
        shares_out = 100000000
    intrinsic_value = (pv_cf + pv_tv) / shares_out
    
    if intrinsic_value <= 0:
        margin_of_safety = 0.0
    else:
        margin_of_safety = ((intrinsic_value - current_price) / intrinsic_value) * 100
        
    # Render 1a
    st.markdown("##### Valuation & Price Action")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Current Price", f"₹ {current_price:,.2f}")
        st.plotly_chart(create_sparkline(df['Close'].tail(30).values, '#00d4ff'), use_container_width=True, config={'displayModeBar': False})
        
    with col2:
        delta = forecasted_price - current_price
        st.metric("Forecasted Price (90d)", f"₹ {forecasted_price:,.2f}", f"{delta:,.2f}")
        st.plotly_chart(create_sparkline(forecast_df['Forecast'].values if 'forecast_df' in locals() else [], '#00cc96'), use_container_width=True, config={'displayModeBar': False})
        
    with col3:
        iv_delta = intrinsic_value - current_price
        st.metric("DCF Intrinsic Value", f"₹ {intrinsic_value:,.2f}", f"{iv_delta:,.2f}")
        st.plotly_chart(create_sparkline(np.linspace(current_price, intrinsic_value, 10), '#b82edd'), use_container_width=True, config={'displayModeBar': False})
        
    # 1b: 6 live metrics
    returns = df['Log_Return'].dropna()
    exp_return_1y = returns.mean() * 252
    
    if not port_returns.empty:
        opt_w, port_ret, port_vol, port_sharpe = optimize_portfolio(port_returns)
    else:
        port_ret, port_vol, port_sharpe = 0.0, 0.0, 0.0
        
    var_95_pct = np.percentile(returns, 5) if not returns.empty else -0.02 # historical 1-day var percentage
    
    try:
        model, _, _, _ = generate_and_train_pd_model()
        features_df = fetch_financial_ratios(selected_ticker)
        pd_prob = model.predict_proba(features_df)[0, 1]
    except Exception:
        pd_prob = 0.02 # fallback PD
    
    st.markdown("##### Key Risk Metrics")
    
    # Compute Beta, Jensen's Alpha, R² via NIFTY50 regression
    try:
        nifty = yf.download("^NSEI", start=df.index[0], end=df.index[-1], progress=False)
        if isinstance(nifty.columns, pd.MultiIndex):
            nifty.columns = nifty.columns.get_level_values(0)
        nifty_ret = np.log(nifty["Close"] / nifty["Close"].shift(1)).dropna()
        aligned = pd.concat([returns, nifty_ret], axis=1).dropna()
        aligned.columns = ["stock", "market"]
        cov_matrix = np.cov(aligned["stock"], aligned["market"])
        beta = cov_matrix[0, 1] / cov_matrix[1, 1]
        rfr_daily = 0.065 / 252  # 6.5% annual risk-free rate
        alpha = (aligned["stock"].mean() - rfr_daily) - beta * (aligned["market"].mean() - rfr_daily)
        alpha_annual = alpha * 252
        ss_res = np.sum((aligned["stock"] - (alpha + beta * aligned["market"])) ** 2)
        ss_tot = np.sum((aligned["stock"] - aligned["stock"].mean()) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
    except Exception:
        beta, alpha_annual, r_squared = 1.0, 0.0, 0.0
    
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.metric("Expected Return (1Y)", f"{exp_return_1y*100:.1f}%")
    m2.metric("Portfolio Return", f"{port_ret*100:.1f}%")
    m3.metric("Portfolio Risk", f"{port_vol*100:.1f}%")
    m4.metric("VaR 95% (1-Day)", f"{var_95_pct*100:.2f}%")
    m5.metric("Prob of Default (PD)", f"{pd_prob*100:.2f}%")
    m6.metric("Sharpe Ratio", f"{port_sharpe:.2f}")
    
    m7, m8, m9 = st.columns(3)
    m7.metric("Beta (vs NIFTY50)", f"{beta:.3f}")
    m8.metric("Jensen's Alpha (Ann.)", f"{alpha_annual*100:.2f}%")
    m9.metric("R² (Market Fit)", f"{r_squared:.3f}")
    
    # 1c: Investment Signal Logic
    var_pct_val = var_95_pct * 100
    
    if margin_of_safety > 20 and var_pct_val > -5.0:
        signal = "BUY"
        color = "#00cc96"
    elif 5 <= margin_of_safety <= 20:
        signal = "HOLD"
        color = "#ff9900"
    else:
        signal = "SELL"
        color = "#ff4b4b"
        
    if var_pct_val < -3.0:
        risk_level = "High"
        risk_color = "#ff4b4b"
    elif var_pct_val < -1.5:
        risk_level = "Medium"
        risk_color = "#ff9900"
    else:
        risk_level = "Low"
        risk_color = "#00cc96"
        
    st.markdown("##### Investment Signal")
    st.markdown(f"""
        <div style="padding: 25px; border-radius: 12px; background: linear-gradient(135deg, #111827 0%, #1f2937 100%); border: 1px solid #374151; text-align: center; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);">
            <div style="font-size: 14px; text-transform: uppercase; letter-spacing: 0.1em; color: #9ca3af; margin-bottom: 8px;">Investment Action Signal</div>
            <h2 style="color: {color}; margin: 0; font-size: 54px; font-weight: 800; text-shadow: 0 0 15px {color}40;">{signal}</h2>
            <div style="margin-top: 15px; display: inline-flex; gap: 20px; font-size: 16px; color: #e5e7eb;">
                <span style="background: rgba(255,255,255,0.05); padding: 4px 12px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.1);">Risk Level: <b style="color: {risk_color}">{risk_level}</b></span>
                <span style="background: rgba(255,255,255,0.05); padding: 4px 12px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.1);">Margin of Safety: <b style="color: {color}">{margin_of_safety:.2f}%</b></span>
            </div>
        </div>
    """, unsafe_allow_html=True)
