import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.optimize import minimize

@st.cache_data
def simulate_bond_returns(_dates: pd.DatetimeIndex, target_vol: float = 0.03) -> pd.Series:
    """Generate simulated bond returns.

    Parameters
    ----------
    _dates: pd.DatetimeIndex
        Index of dates for which to generate returns.
    target_vol: float, optional
        Desired annualized volatility (default 0.03).
    """
    np.random.seed(42)
    daily_vol = target_vol / np.sqrt(252)
    bond_ret = np.random.normal(0, daily_vol, len(_dates))
    return pd.Series(bond_ret, index=_dates, name='BOND_SIM')

def optimize_portfolio(returns):
    mu = returns.mean() * 252
    cov = returns.cov() * 252
    
    n_assets = len(mu)
    
    def neg_sharpe(weights):
        p_ret = np.sum(weights * mu)
        p_vol = np.sqrt(np.dot(weights.T, np.dot(cov, weights)))
        if p_vol == 0:
            return 0
        return -p_ret / p_vol
        
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bounds = tuple((0, 1) for _ in range(n_assets))
    init_guess = np.array([1./n_assets] * n_assets)
    
    result = minimize(neg_sharpe, init_guess, method='SLSQP', bounds=bounds, constraints=constraints)
    
    opt_w = result.x
    opt_ret = np.sum(opt_w * mu)
    opt_vol = np.sqrt(np.dot(opt_w.T, np.dot(cov, opt_w)))
    opt_sharpe = opt_ret / opt_vol if opt_vol > 0 else 0
    
    return opt_w, opt_ret, opt_vol, opt_sharpe

def generate_random_portfolios(returns, n_portfolios=5000):
    np.random.seed(42)
    mu = returns.mean().values * 252
    cov = returns.cov().values * 252
    n_assets = len(mu)
    
    # Vectorized generation of random weights: shape (n_portfolios, n_assets)
    weights = np.random.random((n_portfolios, n_assets))
    weights = weights / np.sum(weights, axis=1, keepdims=True)
    
    # Vectorized calculation of expected portfolio returns
    p_returns = np.dot(weights, mu)
    
    # Vectorized calculation of portfolio risk (volatility)
    # Volatility = sqrt(w^T * cov * w)
    p_vols = np.sqrt(np.sum(np.dot(weights, cov) * weights, axis=1))
    
    # Vectorized calculation of Sharpe Ratio
    p_sharpe = np.where(p_vols > 0, p_returns / p_vols, 0)
    
    results = np.vstack((p_returns, p_vols, p_sharpe))
    return results

def render_module_8(returns_df):
    st.subheader("Module 8: Portfolio Optimization")
    
    if returns_df.empty:
        st.warning("Insufficient data.")
        return
        
    # Interactive Toggle for assets
    st.markdown("##### Toggle Assets in Portfolio")
    selected_assets = []
    cols = st.columns(len(returns_df.columns))
    for i, col in enumerate(returns_df.columns):
        # We handle layout dynamically
        if cols[i % len(cols)].checkbox(col, value=True, key=f"mod8_{col}"):
            selected_assets.append(col)
            
    if len(selected_assets) < 2:
        st.error("Please select at least 2 assets for optimization.")
        return
        
    opt_returns = returns_df[selected_assets]
    
    with st.spinner("Running Monte Carlo Portfolio Generation & Optimization..."):
        opt_w, opt_ret, opt_vol, opt_sharpe = optimize_portfolio(opt_returns)
        results = generate_random_portfolios(opt_returns)
        
    fig = go.Figure()
    
    # Scatter plot for random portfolios
    fig.add_trace(go.Scatter(
        x=results[1] * 100,
        y=results[0] * 100,
        mode='markers',
        marker=dict(
            color=results[2],
            colorscale='Viridis',
            showscale=True,
            size=5,
            colorbar=dict(title='Sharpe Ratio')
        ),
        name='Random Portfolios'
    ))
    
    # Mark Max Sharpe
    fig.add_trace(go.Scatter(
        x=[opt_vol * 100],
        y=[opt_ret * 100],
        mode='markers+text',
        marker=dict(color='red', size=12, symbol='star'),
        text=['Max Sharpe'],
        textposition='top center',
        name='Max Sharpe Portfolio'
    ))
    
    fig.update_layout(
        title="Efficient Frontier (5000 Random Portfolios)",
        xaxis_title="Volatility (Risk) %",
        yaxis_title="Expected Return %",
        template="plotly_dark",
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        pie_fig = go.Figure(data=[go.Pie(labels=selected_assets, values=opt_w, hole=.3)])
        pie_fig.update_layout(title="Optimal Portfolio Allocation", template="plotly_dark", height=400)
        st.plotly_chart(pie_fig, use_container_width=True)
        
    with col2:
        st.markdown("<br><br>**Max Sharpe Portfolio Metrics**", unsafe_allow_html=True)
        st.metric("Expected Return", f"{opt_ret*100:.2f}%")
        st.metric("Portfolio Volatility", f"{opt_vol*100:.2f}%")
        st.metric("Sharpe Ratio", f"{opt_sharpe:.2f}")
