import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from arch import arch_model

@st.cache_data(show_spinner=False)
def run_garch_model(df):
    # Multiply by 100 for better optimization convergence in arch
    returns = df['Log_Return'].dropna() * 100 
    if returns.empty:
        # Absolute fallback: constant 20% volatility
        return pd.Series(0.20, index=df.index)
        
    try:
        # Use rescale=True so the arch library handles scaling automatically
        am = arch_model(returns, vol='Garch', p=1, q=1, rescale=True)
        res = am.fit(disp='off')
        
        # Rescale back conditional volatility and annualise
        # GARCH conditional volatility is daily standard deviation of scaled return
        scale_factor = res.scale if hasattr(res, 'scale') and res.scale is not None else 1.0
        cond_vol = (res.conditional_volatility / scale_factor / 100) * np.sqrt(252)
        return cond_vol
    except Exception as e:
        # Fallback to 20-day rolling annualized standard deviation
        rolling_vol = df['Log_Return'].rolling(window=20).std() * np.sqrt(252)
        return rolling_vol.fillna(method='bfill').fillna(0.20)

def render_module_3(df):
    st.subheader("Module 3: GARCH Volatility Modeling")
    
    if len(df) < 100:
        st.warning("Not enough data to run GARCH.")
        return
        
    with st.spinner("Fitting GARCH model..."):
        cond_vol = run_garch_model(df)
        
    rolling_vol = df['Rolling_Vol'].dropna()
    common_idx = cond_vol.index.intersection(rolling_vol.index)
    cond_vol = cond_vol.loc[common_idx]
    rolling_vol = rolling_vol.loc[common_idx]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=cond_vol.index, y=cond_vol * 100, mode='lines', name='Conditional Volatility (GARCH)', line=dict(color='#ff9900')))
    fig.add_trace(go.Scatter(x=rolling_vol.index, y=rolling_vol * 100, mode='lines', name='20-Day Rolling Volatility', line=dict(color='white')))
    
    spike_date = cond_vol.idxmax()
    spike_val = cond_vol.loc[spike_date] * 100
    
    fig.add_vline(x=spike_date, line_dash="dash", line_color="red", annotation_text="Max Spike")
    
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
