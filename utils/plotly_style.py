import plotly.graph_objects as go

# Central Plotly style for the Financial Risk Analytics Dashboard
DEFAULT_LAYOUT = dict(
    template='none',  # we apply custom colors directly
    paper_bgcolor='#f5f5f5',
    plot_bgcolor='#ffffff',
    font=dict(family='Outfit', color='#111111'),
    xaxis=dict(
        gridcolor='#1e293b',
        tickfont=dict(color='#94a3b8'),
        zerolinecolor='#1e293b'
    ),
    yaxis=dict(
        gridcolor='#1e293b',
        tickfont=dict(color='#94a3b8'),
        zerolinecolor='#1e293b'
    ),
    colorway=['#38bdf8', '#0ea5e9', '#6366f1', '#a78bfa']
)

def apply_default_style(fig: go.Figure) -> go.Figure:
    """Apply the dark theme layout and enable download button.
    This function mutates the figure and returns it for convenience.
    """
    fig.update_layout(**DEFAULT_LAYOUT)
    # Add PNG download button to modebar
    fig.update_layout(modebar_add=['downloadImage'])
    # Enable smooth transitions for any updates
    fig.update_layout(transition=dict(duration=500))
    return fig
