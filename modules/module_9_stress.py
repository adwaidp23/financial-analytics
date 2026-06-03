import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

try:
    from utils.theme import apply_theme
except Exception:
    def apply_theme(fig):
        try:
            fig.update_layout(template='plotly_dark')
        except Exception:
            pass
        return fig

def render_module_9(returns_df):
    """Renders the Stress Testing & Scenario Analysis dashboard page in Streamlit.

    Args:
        returns_df (pd.DataFrame): DataFrame containing daily log returns for all portfolio assets.
    """
    st.subheader("Module 9: Stress Testing & Scenario Analysis")
    
    if returns_df.empty:
        st.warning("Insufficient data.")
        return
        
    st.markdown("##### Define Custom Scenario")
    custom_name = st.text_input("Custom Scenario Name", value="Global Pandemic")
    custom_shock = st.slider("Market Shock (%)", min_value=-50.0, max_value=50.0, value=-15.0, step=1.0)
    
    assets = returns_df.columns
    
    # Highly realistic, industry-standard factor sensitivities (Betas)
    FACTOR_BETAS = {
        'RELIANCE.NS': {'Market': 1.15, 'InterestRate': -0.20, 'Oil': 0.35},
        'TCS.NS': {'Market': 0.95, 'InterestRate': -0.10, 'Oil': -0.05},
        'INFY.NS': {'Market': 0.98, 'InterestRate': -0.10, 'Oil': -0.05},
        'HDFCBANK.NS': {'Market': 1.10, 'InterestRate': 0.45, 'Oil': -0.15},
        'WIPRO.NS': {'Market': 0.90, 'InterestRate': -0.10, 'Oil': -0.05},
        'GOLDBEES.NS': {'Market': 0.05, 'InterestRate': -0.40, 'Oil': 0.15},
        'BOND_SIM': {'Market': -0.02, 'InterestRate': -0.75, 'Oil': -0.10}
    }
    
    # Generate arrays for computation
    betas_market = np.array([FACTOR_BETAS.get(asset, {'Market': 1.0}).get('Market', 1.0) for asset in assets])
    betas_rate = np.array([FACTOR_BETAS.get(asset, {'InterestRate': 0.0}).get('InterestRate', 0.0) for asset in assets])
    betas_oil = np.array([FACTOR_BETAS.get(asset, {'Oil': 0.0}).get('Oil', 0.0) for asset in assets])
    
    # Equally-weighted portfolio proxy
    w = np.ones(len(assets)) / len(assets)
    
    port_beta_market = np.sum(w * betas_market)
    port_beta_rate = np.sum(w * betas_rate)
    port_beta_oil = np.sum(w * betas_oil)
    
    scenarios = [
        {"Scenario": "Market Crash -20%", "Market Shock": -0.20, "Rate Shock": 0, "Oil Shock": 0},
        {"Scenario": "Interest Rate Hike +2%", "Market Shock": -0.05, "Rate Shock": 0.02, "Oil Shock": 0},
        {"Scenario": "Recession Scenario", "Market Shock": -0.15, "Rate Shock": -0.02, "Oil Shock": -0.10},
        {"Scenario": "Oil Price Shock +25%", "Market Shock": -0.05, "Rate Shock": 0.01, "Oil Shock": 0.25},
        {"Scenario": "Best Case Scenario +15%", "Market Shock": 0.15, "Rate Shock": 0, "Oil Shock": 0},
        {"Scenario": custom_name, "Market Shock": custom_shock / 100, "Rate Shock": 0, "Oil Shock": 0}
    ]
    
    impacts = []
    for scen in scenarios:
        impact = (scen["Market Shock"] * port_beta_market +
                  scen["Rate Shock"] * port_beta_rate +
                  scen["Oil Shock"] * port_beta_oil)
        impacts.append(impact * 100)
        
    scenario_df = pd.DataFrame({
        "Scenario": [s["Scenario"] for s in scenarios],
        "Impact (%)": impacts
    })
    
    # 9c: Horizontal Bar Chart
    colors = ['#ff4b4b' if i < 0 else '#00cc96' for i in impacts]
    
    fig = go.Figure(go.Bar(
        x=impacts,
        y=scenario_df["Scenario"],
        orientation='h',
        marker_color=colors,
        text=[f"{i:.1f}%" for i in impacts],
        textposition='outside'
    ))
    
    # Compute dynamic x-axis range to avoid clipping
    x_min = min(-30.0, min(impacts) - 5)
    x_max = max(30.0, max(impacts) + 5)
    
    fig.update_layout(
        title="Portfolio Impact by Scenario",
        xaxis_title="Impact (%)",
        yaxis_title="Scenario",
        xaxis=dict(range=[x_min, x_max]),
        height=400, margin=dict(l=0, r=0, t=40, b=0)
    )
    apply_theme(fig)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 9d: Risk Narrative
    worst_idx = np.argmin(impacts)
    worst_scenario = scenario_df["Scenario"].iloc[worst_idx]
    
    factor_exposures = {"Market": port_beta_market, "Interest Rates": port_beta_rate, "Oil": port_beta_oil}
    most_sig_factor = max(factor_exposures, key=lambda k: abs(factor_exposures[k]))
    
    hedge_action = "buying index put options" if most_sig_factor == "Market" else \
                   ("entering interest rate swaps" if most_sig_factor == "Interest Rates" else "allocating to commodities/energy ETFs")
                   
    st.info(f"**Risk Interpretation:** The portfolio is most vulnerable to the **{worst_scenario}** scenario. The most significant factor exposure is **{most_sig_factor}** (Beta = {factor_exposures[most_sig_factor]:.2f}). A recommended hedging action would be **{hedge_action}**.")
