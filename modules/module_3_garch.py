import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from arch import arch_model

@st.cache_data(show_spinner=False)
def run_garch_model(df):
    """Fits a GARCH(1,1) model to stock log returns and estimates conditional volatility.

    Args:
        df (pd.DataFrame): DataFrame containing stock price data with at least a 'Log_Return' column.

    Returns:
        tuple: A tuple containing:
            - cond_vol (pd.Series): Annualized conditional volatility series.
            - omega (float): Constant parameter in the variance equation.
            - alpha (float): ARCH parameter coefficient (alpha[1]).
            - beta (float): GARCH parameter coefficient (beta[1]).
            - is_stationary (bool): True if alpha + beta < 1, False otherwise.
    """
    # Multiply by 100 for better optimization convergence in arch
    returns = df['Log_Return'].dropna() * 100 
    if returns.empty:
        # Absolute fallback: constant 20% volatility
        return pd.Series(0.20, index=df.index), 0.0, 0.0, 0.0, True
        
    try:
        # Use rescale=True so the arch library handles scaling automatically
        am = arch_model(returns, vol='Garch', p=1, q=1, rescale=True)
        res = am.fit(disp='off')
        
        # Rescale back conditional volatility and annualise
        # GARCH conditional volatility is daily standard deviation of scaled return
        scale_factor = res.scale if hasattr(res, 'scale') and res.scale is not None else 1.0
        cond_vol = (res.conditional_volatility / scale_factor / 100) * np.sqrt(252)
        
        omega = float(res.params.get('omega', 0.0))
        alpha = float(res.params.get('alpha[1]', 0.0))
        beta = float(res.params.get('beta[1]', 0.0))
        persistence = alpha + beta
        is_stationary = bool(persistence < 1.0)
        
        return cond_vol, omega, alpha, beta, is_stationary
    except Exception as e:
        # Fallback to 20-day rolling annualized standard deviation
        rolling_vol = df['Log_Return'].rolling(window=20).std() * np.sqrt(252)
        cond_vol = rolling_vol.fillna(method='bfill').fillna(0.20)
        return cond_vol, 0.0, 0.0, 0.0, True

def render_module_3(df):
    """Renders the GARCH Volatility Modeling dashboard page in Streamlit.

    Args:
        df (pd.DataFrame): DataFrame containing stock price data with at least 'Log_Return' and 'Rolling_Vol' columns.
    """
    st.subheader("Module 3: GARCH Volatility Modeling")
    
    if len(df) < 100:
        st.warning("Not enough data to run GARCH.")
        return
        
    with st.spinner("Fitting GARCH model..."):
        cond_vol, omega, alpha, beta, is_stationary = run_garch_model(df)
        
    rolling_vol = df['Rolling_Vol'].dropna()
    common_idx = cond_vol.index.intersection(rolling_vol.index)
    cond_vol = cond_vol.loc[common_idx]
    rolling_vol = rolling_vol.loc[common_idx]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=cond_vol.index, y=cond_vol * 100, mode='lines', name='Conditional Volatility (GARCH)', line=dict(color='#ff9900')))
    fig.add_trace(go.Scatter(x=rolling_vol.index, y=rolling_vol * 100, mode='lines', name='20-Day Rolling Volatility', line=dict(color='white')))
    
    spike_date = cond_vol.idxmax()
    spike_val = cond_vol.loc[spike_date] * 100
    
    fig.add_vline(x=spike_date.strftime('%Y-%m-%d'), line_dash="dash", line_color="red", annotation_text="Max Spike")
    
    fig.update_layout(title="Volatility Modeling: GARCH vs Rolling", template="plotly_dark", height=450, yaxis_title="Annualised Volatility (%)", margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig, use_container_width=True)
    
    current_vol = cond_vol.iloc[-1]
    long_term_avg = cond_vol.mean()
    p25 = cond_vol.quantile(0.25)
    p75 = cond_vol.quantile(0.75)
    
    if current_vol > p75:
        regime = "High"
        reg_color = "#ff4b4b"
    elif current_vol < p25:
        regime = "Low"
        reg_color = "#00cc96"
    else:
        regime = "Moderate"
        reg_color = "#ff9900"
        
    cols = st.columns(4)
    cols[0].metric("Current Volatility", f"{current_vol * 100:.2f}%")
    cols[1].metric("Long-Term Average", f"{long_term_avg * 100:.2f}%")
    cols[2].markdown(f"**Regime**<br><span style='color:{reg_color}; font-size:24px; font-weight:bold;'>{regime}</span>", unsafe_allow_html=True)
    cols[3].metric("Last Spike Date", spike_date.strftime('%Y-%m-%d'))

    st.markdown("---")
    st.markdown("##### GARCH(1,1) Model Parameters & Stationarity")
    
    p_cols = st.columns(4)
    p_cols[0].metric("Omega (ω)", f"{omega:.6f}")
    p_cols[1].metric("Alpha (α - ARCH)", f"{alpha:.4f}")
    p_cols[2].metric("Beta (β - GARCH)", f"{beta:.4f}")
    
    persistence = alpha + beta
    status_symbol = "✅ Stationary" if is_stationary else "❌ Non-Stationary"
    status_color = "#00cc96" if is_stationary else "#ff4b4b"
    p_cols[3].markdown(
        f"**Persistence (α + β)**<br>"
        f"<span style='font-size:20px; font-weight:bold;'>{persistence:.4f}</span> "
        f"<span style='color:{status_color}; font-weight:bold; font-size:16px;'>({status_symbol})</span>", 
        unsafe_allow_html=True
    )

