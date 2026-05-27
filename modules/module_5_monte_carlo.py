import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time

def run_gbm_simulation(S0, mu, sigma, T, N):
    dt = 1/252
    Z = np.random.standard_normal((T, N))
    daily_returns = (mu - 0.5 * sigma ** 2) * dt + sigma * np.sqrt(dt) * Z
    cum_returns = np.cumsum(daily_returns, axis=0)
    
    paths = np.zeros((T + 1, N))
    paths[0] = S0
    paths[1:] = S0 * np.exp(cum_returns)
    return paths

def render_module_5(df):
    st.subheader("Module 5: Monte Carlo Simulation (GBM)")
    
    if df.empty:
        st.warning("No data available for simulation.")
        return
        
    returns = df['Log_Return'].dropna()
    mu = returns.mean() * 252
    sigma = returns.std() * np.sqrt(252)
    S0 = df['Close'].iloc[-1]
    
    cols = st.columns(2)
    n_sims = cols[0].slider("Number of Simulations", min_value=500, max_value=10000, value=1000, step=500)
    time_horizon = cols[1].slider("Time Horizon (Trading Days)", min_value=63, max_value=252, value=252, step=21)
    
    start_time = time.time()
    
    with st.spinner("Running Monte Carlo Simulations..."):
        paths = run_gbm_simulation(S0, mu, sigma, time_horizon, n_sims)
        
    comp_time = time.time() - start_time
    
    final_prices = paths[-1]
    p95 = np.percentile(final_prices, 95)
    p05 = np.percentile(final_prices, 5)
    
    # Cap plotted paths to prevent browser lag, but stats use all N simulations
    plot_n = min(n_sims, 1000)
    plot_idx = np.random.choice(n_sims, plot_n, replace=False)
    
    fig = go.Figure()
    
    # Efficiently aggregate paths into three consolidated traces separated by None
    # to avoid rendering 1000+ separate scatter elements in the browser DOM.
    green_x, green_y = [], []
    red_x, red_y = [], []
    blue_x, blue_y = [], []
    
    x_coords = list(range(time_horizon + 1))
    
    for i in plot_idx:
        path = paths[:, i]
        final_price = path[-1]
        
        if final_price >= p95:
            green_x.extend(x_coords + [None])
            green_y.extend(list(path) + [None])
        elif final_price <= p05:
            red_x.extend(x_coords + [None])
            red_y.extend(list(path) + [None])
        else:
            blue_x.extend(x_coords + [None])
            blue_y.extend(list(path) + [None])
            
    if blue_x:
        fig.add_trace(go.Scatter(
            x=blue_x, y=blue_y, mode='lines',
            line=dict(color='rgba(0, 212, 255, 0.08)', width=1),
            name='Median 90% Paths'
        ))
        
    if green_x:
        fig.add_trace(go.Scatter(
            x=green_x, y=green_y, mode='lines',
            line=dict(color='rgba(0, 204, 150, 0.5)', width=1.5),
            name='Top 5% (Bull Case)'
        ))
        
    if red_x:
        fig.add_trace(go.Scatter(
            x=red_x, y=red_y, mode='lines',
            line=dict(color='rgba(255, 75, 75, 0.5)', width=1.5),
            name='Bottom 5% (Bear Case)'
        ))
        
    fig.update_layout(
        title=f"Monte Carlo Paths (Simulated: {n_sims}, Rendered: {plot_n})",
        xaxis_title="Trading Days", yaxis_title="Price (INR)",
        template="plotly_dark", height=450, margin=dict(l=0, r=0, t=40, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)
    
    exp_price = np.mean(final_prices)
    median_price = np.median(final_prices)
    prob_up = np.sum(final_prices > S0 * 1.10) / n_sims * 100
    prob_down = np.sum(final_prices < S0 * 0.90) / n_sims * 100
    
    st.markdown(f"**Simulation Computation Time:** {comp_time:.2f} seconds")
    
    summary_df = pd.DataFrame({
        "Metric": ["Expected Price (Mean)", "Median Price", "Best Case (95th Pctl)", "Worst Case (5th Pctl)", "Prob > 10% Gain", "Prob > 10% Loss"],
        "Value": [f"₹ {exp_price:.2f}", f"₹ {median_price:.2f}", f"₹ {p95:.2f}", f"₹ {p05:.2f}", f"{prob_up:.1f}%", f"{prob_down:.1f}%"]
    })
    
    st.dataframe(summary_df, hide_index=True)
