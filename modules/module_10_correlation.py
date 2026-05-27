import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

def render_module_10(returns_df):
    """Renders the Correlation Heatmap dashboard page in Streamlit.

    Args:
        returns_df (pd.DataFrame): DataFrame containing daily log returns for all portfolio assets.
    """
    st.subheader("Module 10: Correlation Heatmap")
    
    if returns_df.empty:
        st.warning("Insufficient data.")
        return
        
    corr_matrix = returns_df.corr()
    
    # Prepare data for heatmap
    z = corr_matrix.values
    x = corr_matrix.columns.tolist()
    y = corr_matrix.index.tolist()
    
    annotations = []
    for i in range(len(y)):
        for j in range(len(x)):
            val = z[i][j]
            text = f"{val:.2f}"
            
            if abs(val) > 0.70 and i != j:
                text += " ⚠️"
                color = "#ff4b4b" # Highlight high correlation warning in red
                font_weight = "bold"
            else:
                color = "#e2e8f0" # High-contrast off-white for regular cells
                font_weight = "normal"
            
            annotations.append(dict(
                x=x[j], y=y[i],
                text=text,
                showarrow=False,
                font=dict(color=color, size=13, weight=font_weight)
            ))
            
    fig = go.Figure(data=go.Heatmap(
        z=z, x=x, y=y,
        colorscale='RdBu',
        zmin=-1, zmax=1,
        reversescale=True,
    ))
    
    fig.update_layout(
        title="Asset Correlation Matrix",
        annotations=annotations,
        template="plotly_dark",
        height=600, margin=dict(l=0, r=0, t=40, b=0)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 10d: Insights
    # copy array to mask diagonal
    z_mask = z.copy()
    np.fill_diagonal(z_mask, np.nan)
    
    if not np.isnan(z_mask).all():
        max_idx = np.nanargmax(z_mask)
        max_i, max_j = np.unravel_index(max_idx, z_mask.shape)
        
        min_idx = np.nanargmin(z_mask)
        min_i, min_j = np.unravel_index(min_idx, z_mask.shape)
        
        st.success(f"**Most Diversifying Pair:** {y[min_i]} & {x[min_j]} (Corr: {z_mask[min_i, min_j]:.2f})")
        st.error(f"**Most Redundant Pair:** {y[max_i]} & {x[max_j]} (Corr: {z_mask[max_i, max_j]:.2f})")
