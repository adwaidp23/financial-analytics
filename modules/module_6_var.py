import streamlit as st
import pandas as pd
import numpy as np
import scipy.stats as stats
import plotly.graph_objects as go
from utils.theme import apply_theme

def calc_kupiec_pof(exceptions, N, alpha):
    """Calculates the Kupiec Proportion of Failures (POF) Likelihood Ratio test p-value.

    Args:
        exceptions (int): The number of VaR exceptions observed.
        N (int): The total number of backtesting observations.
        alpha (float): The VaR confidence level (e.g., 0.95 or 0.99).

    Returns:
        float: The p-value of the Likelihood Ratio test.
    """
    p = 1 - alpha
    if exceptions == 0:
        # If 0 exceptions, it is extremely safe, return p-value 1.0 (fail to reject model validity)
        return 1.0
    if exceptions == N:
        # If all exceptions, it is extremely invalid, return p-value 0.0
        return 0.0
        
    p_hat = exceptions / N
    
    try:
        # Kupiec POF Likelihood Ratio Test Formula (log-form for numeric stability)
        if p_hat == 0 or p_hat == 1:
            # p_hat extremes are handled as model pass/fail boundaries
            return 1.0 if exceptions == 0 else 0.0

        lr_statistic = -2.0 * (
            exceptions * np.log(p / p_hat) +
            (N - exceptions) * np.log((1 - p) / (1 - p_hat))
        )
        p_value = 1 - stats.chi2.cdf(lr_statistic, df=1)
        if np.isnan(p_value):
            return 1.0
        return float(max(0.0, min(1.0, p_value)))
    except Exception:
        return 1.0

def render_module_6(df):
    """Renders the Value at Risk (VaR) and CVaR analysis dashboard page in Streamlit.

    Args:
        df (pd.DataFrame): DataFrame containing stock price data with at least 'Close' and 'Log_Return' columns.
    """
    st.subheader("Module 6: Value at Risk (VaR) & CVaR")
    
    if df.empty or len(df) < 252:
        st.warning("Insufficient data. At least 252 days of data required for VaR calculations.")
        return
        
    returns = df['Log_Return'].dropna()
    current_price = df['Close'].iloc[-1]
    
    # 6a: Three VaR methods (95% and 99%) using returns consistently
    var_95_hist_pct = np.percentile(returns, 5)
    var_99_hist_pct = np.percentile(returns, 1)
    
    var_95_hist = current_price * (np.exp(var_95_hist_pct) - 1)
    var_99_hist = current_price * (np.exp(var_99_hist_pct) - 1)
    
    # 2. Parametric Normal
    mu = returns.mean()
    sigma = returns.std()
    
    z_95 = stats.norm.ppf(0.05)
    z_99 = stats.norm.ppf(0.01)
    
    var_95_param_pct = mu + z_95 * sigma
    var_99_param_pct = mu + z_99 * sigma
    
    var_95_param = current_price * (np.exp(var_95_param_pct) - 1)
    var_99_param = current_price * (np.exp(var_99_param_pct) - 1)
    
    # 3. Monte Carlo Simulation (10,000 paths)
    n_sims = 10000
    z_mc = np.random.standard_normal(n_sims)
    # 1-day simulated returns
    sim_returns = mu + sigma * z_mc
    sim_prices = current_price * np.exp(sim_returns)
    sim_pnl = sim_prices - current_price
    
    var_95_mc = np.percentile(sim_pnl, 5)
    var_99_mc = np.percentile(sim_pnl, 1)
    
    var_df = pd.DataFrame({
        "Method": ["Historical Simulation", "Parametric Normal", "Monte Carlo (10k)"],
        "VaR 95% (1-Day)": [f"₹ {var_95_hist:,.2f}", f"₹ {var_95_param:,.2f}", f"₹ {var_95_mc:,.2f}"],
        "VaR 99% (1-Day)": [f"₹ {var_99_hist:,.2f}", f"₹ {var_99_param:,.2f}", f"₹ {var_99_mc:,.2f}"]
    })
    
    st.markdown("**1-Day Value at Risk (VaR) Comparison**")
    st.dataframe(var_df, hide_index=True)
    
    # 6b: Expected Shortfall (CVaR) at 95% for all methods
    cvar_95_hist_pct = returns[returns <= var_95_hist_pct].mean() if np.any(returns <= var_95_hist_pct) else var_95_hist_pct
    cvar_95_param_pct = returns[returns <= var_95_param_pct].mean() if np.any(returns <= var_95_param_pct) else var_95_param_pct
    cvar_95_mc_pct = sim_returns[sim_returns <= np.percentile(sim_returns, 5)].mean()

    cvar_95_hist = current_price * (np.exp(cvar_95_hist_pct) - 1)
    cvar_95_param = current_price * (np.exp(cvar_95_param_pct) - 1)
    cvar_95_mc = current_price * (np.exp(cvar_95_mc_pct) - 1)

    cvar_df = pd.DataFrame({
        "Method": ["Historical Simulation", "Parametric Normal", "Monte Carlo (10k)"],
        "CVaR 95% (1-Day)": [
            f"₹ {cvar_95_hist:,.2f}",
            f"₹ {cvar_95_param:,.2f}",
            f"₹ {cvar_95_mc:,.2f}"
        ]
    })

    st.markdown("**Expected Shortfall (CVaR 95%) Comparison**")
    st.dataframe(cvar_df, hide_index=True)
    st.info("CVaR (Expected Shortfall) measures the average loss in the worst 5% of outcomes and is thus a more conservative tail-risk metric than VaR.")
    
    # 6c: Loss Distribution Chart
    fig = go.Figure()
    
    # Histogram of P&L
    fig.add_trace(go.Histogram(
        x=sim_pnl,
        histnorm='probability density',
        name="Expected P&L",
        marker_color='#00d4ff',
        opacity=0.6,
        nbinsx=100
    ))
    
    # Add VaR line
    fig.add_vline(x=var_95_mc, line_dash="dash", line_color="#ff4b4b", line_width=2, annotation_text="VaR 95% Limit", annotation_position="top left")
    
    # Shade the tail region
    fig.add_trace(go.Histogram(
        x=sim_pnl[sim_pnl <= var_95_mc],
        histnorm='probability density',
        name="Loss Tail (CVaR 95% Region)",
        marker_color='#ff4b4b',
        opacity=0.7,
        nbinsx=30
    ))
    
    fig.update_layout(
    title="Monte Carlo 1-Day P&L Distribution (Loss Tail Highlighted)",
    xaxis_title="Profit & Loss (INR)",
    yaxis_title="Probability Density",
    height=400,
    barmode='overlay',
    margin=dict(l=0, r=0, t=40, b=0),
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
)
    apply_theme(fig)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 6d: Kupiec Backtesting using the same return threshold as the VaR model
    hist_prices = df['Close'].iloc[-253:].values
    hist_returns = np.log(hist_prices[1:] / hist_prices[:-1])
    
    # Using historical one-day returns to count exceptions below the 95% VaR return threshold
    exceptions = np.sum(hist_returns < var_95_hist_pct)
    N = len(hist_returns)
    alpha = 0.95
    expected_exceptions = N * (1 - alpha)
    
    p_value = calc_kupiec_pof(exceptions, N, alpha)
    is_valid = "Valid" if p_value > 0.05 else "Invalid"
    valid_color = "#00cc96" if is_valid == "Valid" else "#ff4b4b"
    
    st.markdown("**Kupiec Proportion of Failures (POF) Test (Last 252 Days)**")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Exceptions", int(exceptions))
    col2.metric("Expected Exceptions", f"{expected_exceptions:.1f}")
    col3.metric("p-value", f"{p_value:.4f}")
    col4.markdown(f"<div style='padding-top:20px; font-size:24px; color:{valid_color}; font-weight:bold;'>Model {is_valid}</div>", unsafe_allow_html=True)
