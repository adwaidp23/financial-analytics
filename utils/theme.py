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
    """Generate dynamic CSS based on current theme state."""
    dark_mode = st.session_state.get('dark_mode', True)
    
    if dark_mode:
        bg_primary = "#090b10"
        bg_secondary = "#111827"
        bg_tertiary = "rgba(15, 23, 42, 0.95)"
        text_primary = "#e2e8f0"
        text_secondary = "#cbd5e1"
        text_muted = "#94a3b8"
        accent = "#38bdf8"
        accent_light = "#0ea5e9"
        border_color = "#1e293b"
        badge_bg = "rgba(56, 189, 248, 0.12)"
        badge_text = "#dbeafe"
    else:
        bg_primary = "#f5f5f5"
        bg_secondary = "#e8e8e8"
        bg_tertiary = "rgba(245, 245, 245, 0.98)"
        text_primary = "#0a0e27"
        text_secondary = "#1e293b"
        text_muted = "#475569"
        accent = "#0066cc"
        accent_light = "#0052a3"
        border_color = "#ccc"
        badge_bg = "rgba(0, 102, 204, 0.15)"
        badge_text = "#003d99"
    
    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    /* Global font and background */
    html, body, [class*='css'] {{
        font-family: 'Outfit', sans-serif;
        background: linear-gradient(135deg, {bg_primary} 0%, {bg_secondary} 100%) !important;
        color: {text_primary} !important;
        line-height: 1.6;
    }}
    
    /* Sticky Header */
    .kpi-header {{
        position: sticky;
        top: 0;
        background: {bg_tertiary};
        backdrop-filter: saturate(180%) blur(8px);
        padding: 0.5rem 1rem;
        display: flex;
        justify-content: space-around;
        align-items: center;
        z-index: 10;
        border-bottom: 1px solid {border_color};
    }}
    .kpi-card {{
        text-align: center;
    }}
    .kpi-card h3 {{
        margin: 0;
        font-size: 1.2rem;
        color: {text_primary} !important;
    }}
    .kpi-card p {{
        margin: 0;
        font-size: 1.4rem;
        font-weight: 600;
        color: {text_primary} !important;
    }}
    
    .stApp {{
        background: linear-gradient(180deg, {bg_primary} 0%, {bg_secondary} 100%) !important;
        padding: 2rem;
        color: {text_primary} !important;
    }}
    
    [data-testid='stAppViewContainer'] {{
        background: linear-gradient(180deg, {bg_primary} 0%, {bg_secondary} 100%) !important;
        color: {text_primary} !important;
    }}
    
    .css-18e3th9, .main, .block-container {{
        background: transparent !important;
        color: {text_primary} !important;
    }}
    
    .stMarkdownContainer, .stText, .stText span, .stText p, .stText div {{
        color: {text_primary} !important;
    }}
    
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {{
        color: {text_primary} !important;
    }}
    
    .stMarkdownContainer a, .stText a, a {{
        color: {accent} !important;
    }}
    
    .stDataFrame table {{
        color: {text_primary} !important;
    }}
    
    /* Sidebar */
    [data-testid='stSidebar'] {{
        background: {bg_tertiary} !important;
        backdrop-filter: saturate(180%) blur(12px);
        border-right: 1px solid {border_color};
        border-radius: 0 12px 12px 0;
        transition: transform 0.3s ease;
    }}
    [data-testid='stSidebar']:hover {{
        transform: translateX(2px);
    }}
    
    /* Metric cards */
    div[data-testid='stMetricValue'] {{
        font-size: 30px !important;
        font-weight: 700 !important;
        color: {text_primary} !important;
        transition: color 0.3s ease;
    }}
    div[data-testid='stMetricLabel'] {{
        font-size: 15px !important;
        color: {text_secondary} !important;
        font-weight: 500 !important;
    }}
    div[data-testid='stMetricContainer']:hover div[data-testid='stMetricValue'] {{
        color: {accent};
    }}

    /* Dashboard banner */
    .dashboard-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 1rem;
        padding: 1.5rem 1.25rem;
        margin-bottom: 1.5rem;
        background: {bg_tertiary};
        border: 1px solid {border_color};
        border-radius: 20px;
        box-shadow: 0 24px 80px rgba(0, 0, 0, 0.10);
    }}
    .dashboard-header h1 {{
        margin: 0;
        font-size: 2.3rem;
        letter-spacing: -0.04em;
        color: {text_primary};
    }}
    .dashboard-header p {{
        margin: 0.5rem 0 0;
        color: {text_secondary};
        line-height: 1.6;
    }}
    .dashboard-badges {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        justify-content: flex-end;
    }}
    .dashboard-badges span {{
        padding: 0.65rem 0.9rem;
        border-radius: 999px;
        background: {badge_bg};
        color: {badge_text};
        font-size: 0.93rem;
        font-weight: 600;
    }}
    .sidebar-heading {{
        font-size: 1.5rem;
        font-weight: 700;
        color: {accent};
        margin-bottom: 0.25rem;
    }}
    .sidebar-description {{
        color: {text_secondary};
        margin-bottom: 1rem;
        line-height: 1.6;
    }}
    .sidebar-subtitle {{
        color: {text_muted};
        font-size: 0.95rem;
        margin-bottom: 0.25rem;
    }}
    .sidebar-help {{
        color: {text_secondary};
        padding: 0.8rem 0.9rem;
        background: {badge_bg};
        border-radius: 14px;
        margin-bottom: 1rem;
        font-size: 0.95rem;
        line-height: 1.5;
    }}
    .badge-card {{
        background: {badge_bg};
        border: 1px solid {border_color};
        border-radius: 18px;
    }}
    .page-title {{
        font-size: 2rem;
        margin-bottom: 0.25rem;
        color: {text_primary};
    }}
    .page-subtitle {{
        margin-top: 0;
        margin-bottom: 1rem;
        color: {text_muted};
        font-size: 1rem;
    }}
    .section-divider {{
        height: 1px;
        width: 100%;
        background: {border_color};
        margin-bottom: 1.5rem;
    }}
    
    /* Module header with fade-in */
    .module-header {{
        font-size: 26px;
        font-weight: 700;
        color: {accent};
        margin-bottom: 20px;
        border-bottom: 2px solid {border_color};
        padding-bottom: 8px;
        animation: fadeIn 0.8s ease-out;
    }}
    
    /* Button styling */
    .stButton button {{
        background: linear-gradient(135deg, {accent}, {accent_light});
        border: none;
        color: #ffffff;
        padding: 0.6rem 1.4rem;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        transition: transform 0.2s, box-shadow 0.2s;
    }}
    .stButton button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(56, 189, 248, 0.4);
    }}
    
    /* Fade-in animation */
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    </style>
    """
