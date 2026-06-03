import streamlit as st

def init_theme():
    """Initialize dark mode setting in session state if not present."""
    if 'dark_mode' not in st.session_state:
        # Default to dark mode for premium look
        st.session_state.dark_mode = True

def get_template():
    """Return appropriate Plotly template based on current theme."""
    return 'plotly_dark' if st.session_state.get('dark_mode', True) else 'plotly_white'

def apply_theme(fig):
    """Apply cohesive Plotly style to figure and return it."""
    try:
        from utils.plotly_style import apply_default_style
        return apply_default_style(fig)
    except Exception:
        # Fallback to basic theme if import fails
        fig.update_layout(template=get_template())
        return fig
def get_css():
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    
    /* Global font and background */
    html, body, [class*="css"] {\n        font-family: 'Outfit', sans-serif;\n        background: linear-gradient(135deg, #0d0f12 0%, #11141a 100%);\n        color: #e2e8f0;\n    }
    
    /* Sticky Header */
    .kpi-header {\n        position: sticky;\n        top: 0;\n        background: rgba(17,20,26,0.9);\n        backdrop-filter: saturate(180%) blur(8px);\n        padding: 0.5rem 1rem;\n        display: flex;\n        justify-content: space-around;\n        align-items: center;\n        z-index: 10;\n        border-bottom: 1px solid #1e293b;\n    }
    .kpi-card {\n        text-align: center;\n    }
    .kpi-card h3 {\n        margin: 0;\n        font-size: 1.1rem;\n        color: #94a3b8;\n    }
    .kpi-card p {\n        margin: 0;\n        font-size: 1.3rem;\n        font-weight: 600;\n        color: #ffffff;\n    }
    
    
    .stApp {
        background-color: transparent;
        padding: 2rem;
    }
    
    /* Glassmorphism Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(17,20,26,0.85) !important;
        backdrop-filter: saturate(180%) blur(12px);
        border-right: 1px solid #1e293b;
        border-radius: 0 12px 12px 0;
        transition: transform 0.3s ease;
    }
    [data-testid="stSidebar"]:hover {
        transform: translateX(2px);
    }
    
    /* Metric cards */
    div[data-testid="stMetricValue"] {
        font-size: 28px !important;
        font-weight: 700 !important;
        color: #ffffff !important;
        transition: color 0.3s ease;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 14px !important;
        color: #94a3b8 !important;
        font-weight: 500 !important;
    }
    div[data-testid="stMetricContainer"]:hover div[data-testid="stMetricValue"] {
        color: #38bdf8;
    }
    
    /* Module header with fade-in */
    .module-header {
        font-size: 26px;
        font-weight: 700;
        color: #38bdf8;
        margin-bottom: 20px;
        border-bottom: 2px solid #1e293b;
        padding-bottom: 8px;
        animation: fadeIn 0.8s ease-out;
    }
    
    /* Button styling */
    .stButton button {
        background: linear-gradient(135deg, #38bdf8, #0ea5e9);
        border: none;
        color: #ffffff;
        padding: 0.6rem 1.4rem;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(56,189,248,0.4);
    }
    
    /* Fade-in animation */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    </style>
    """
