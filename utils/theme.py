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
        bg_primary = "#151924"      # Main background
        bg_secondary = "#151924"
        bg_card = "#1E222D"         # Card background
        text_primary = "#FFFFFF"    # Headings and main numbers
        text_secondary = "#D1D5DB"  # General text
        text_muted = "#9CA3AF"      # Labels, small text
        accent = "#2962FF"          # Blue accent
        border_color = "#2A2E39"    # Subtle borders
        badge_bg = "rgba(41, 98, 255, 0.15)"
        badge_text = "#38BDF8"
    else:
        # Fallback light theme (though image is strictly dark)
        bg_primary = "#F3F4F6"
        bg_secondary = "#F3F4F6"
        bg_card = "#FFFFFF"
        text_primary = "#111827"
        text_secondary = "#374151"
        text_muted = "#6B7280"
        accent = "#2563EB"
        border_color = "#E5E7EB"
        badge_bg = "rgba(37, 99, 235, 0.15)"
        badge_text = "#1D4ED8"
    
    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    /* Global font and background */
    html, body, [class*='css'] {{
        font-family: 'Inter', sans-serif !important;
        background-color: {bg_primary} !important;
        background-image: none !important;
        color: {text_secondary} !important;
    }}
    
    .stApp {{
        background-color: {bg_primary} !important;
        background-image: none !important;
    }}
    
    [data-testid='stAppViewContainer'] {{
        background-color: {bg_primary} !important;
        background-image: none !important;
    }}
    
    .css-18e3th9, .main, .block-container {{
        background: transparent !important;
        padding-top: 3.5rem !important;
    }}
    
    .stMarkdownContainer, .stText {{
        color: {text_secondary} !important;
    }}
    
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {{
        color: {text_primary} !important;
        font-weight: 700;
    }}
    
    /* Sidebar */
    [data-testid='stSidebar'] {{
        background-color: {bg_card} !important;
        border-right: 1px solid {border_color};
    }}
    
    /* Custom Dashboard Header matching the Mockup */
    .mockup-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: {bg_primary};
        padding: 0 0 20px 0;
        margin-bottom: 20px;
        border-bottom: 1px solid {border_color};
    }}
    
    .header-left h1 {{
        margin: 0;
        font-size: 28px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: {text_primary};
    }}
    
    .header-left .tags {{
        display: flex;
        align-items: center;
        gap: 10px;
        margin-top: 5px;
        font-size: 13px;
        font-weight: 600;
        color: {text_muted};
        text-transform: uppercase;
    }}
    
    .header-left .tags span.market-open {{
        color: #22C55E;
        display: flex;
        align-items: center;
        gap: 4px;
    }}
    
    .header-left .tags span.market-open::before {{
        content: '';
        display: inline-block;
        width: 8px;
        height: 8px;
        background-color: #22C55E;
        border-radius: 50%;
    }}
    
    .header-right {{
        display: flex;
        gap: 30px;
        align-items: center;
    }}
    
    .header-price {{
        display: flex;
        flex-direction: column;
        align-items: flex-end;
    }}
    
    .header-price .label {{
        font-size: 12px;
        font-weight: 600;
        color: {text_muted};
        text-transform: uppercase;
    }}
    
    .header-price .value {{
        font-size: 28px;
        font-weight: 800;
        color: {text_primary};
        margin-top: 2px;
    }}
    
    .header-price .change.positive {{
        color: #22C55E;
        font-size: 14px;
        font-weight: 600;
    }}
    
    .header-price .change.negative {{
        color: #EF4444;
        font-size: 14px;
        font-weight: 600;
    }}
    
    .header-signal {{
        display: flex;
        flex-direction: column;
        align-items: flex-end;
    }}
    
    .header-signal .label {{
        font-size: 12px;
        font-weight: 600;
        color: {text_muted};
        text-transform: uppercase;
    }}
    
    .header-signal .signal-box {{
        background-color: rgba(34, 197, 94, 0.15);
        color: #22C55E;
        padding: 6px 16px;
        border-radius: 6px;
        font-weight: 800;
        font-size: 18px;
        margin-top: 4px;
        text-transform: uppercase;
        border: 1px solid rgba(34, 197, 94, 0.3);
    }}
    
    .header-signal .signal-box.sell {{
        background-color: rgba(239, 68, 68, 0.15);
        color: #EF4444;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }}
    
    .header-signal .signal-box.hold {{
        background-color: rgba(245, 158, 11, 0.15);
        color: #F59E0B;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }}
    
    /* Top 3 Cards in Module 1 */
    .summary-cards-container {{
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 20px;
        margin-bottom: 20px;
    }}
    
    .summary-card {{
        background-color: {bg_card};
        border: 1px solid {border_color};
        border-radius: 12px;
        padding: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    
    .summary-card-left {{
        display: flex;
        flex-direction: column;
    }}
    
    .summary-card-label {{
        font-size: 13px;
        font-weight: 600;
        color: {text_muted};
        text-transform: uppercase;
        margin-bottom: 8px;
    }}
    
    .summary-card-value {{
        font-size: 26px;
        font-weight: 700;
        color: {text_primary};
    }}
    
    .summary-card-right {{
        width: 100px;
        height: 40px;
    }}
    
    /* Live Risk Metrics Bar */
    .live-risk-bar {{
        background-color: {bg_card};
        border: 1px solid {border_color};
        border-radius: 8px;
        padding: 15px 20px;
        margin-bottom: 20px;
    }}
    
    .live-risk-title {{
        font-size: 14px;
        font-weight: 700;
        color: {text_primary};
        margin-bottom: 12px;
        text-transform: uppercase;
    }}
    
    .live-risk-metrics {{
        display: flex;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 15px;
    }}
    
    .risk-metric-item {{
        display: flex;
        flex-direction: column;
    }}
    
    .risk-metric-label {{
        font-size: 11px;
        font-weight: 600;
        color: {text_muted};
        text-transform: uppercase;
        margin-bottom: 4px;
    }}
    
    .risk-metric-value {{
        font-size: 16px;
        font-weight: 700;
    }}
    
    /* Module Containers & Headers */
    .module-container {{
        background-color: {bg_card};
        border: 1px solid {border_color};
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
        height: 100%;
    }}
    
    .module-header-container {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        border-bottom: 1px solid {border_color};
        padding-bottom: 10px;
    }}
    
    .module-header-title {{
        font-size: 15px;
        font-weight: 800;
        color: {text_primary};
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin: 0;
    }}
    
    .module-badge {{
        font-size: 11px;
        font-weight: 700;
        padding: 4px 8px;
        border-radius: 4px;
        text-transform: uppercase;
    }}
    
    .module-badge.blue {{ color: #38BDF8; background: rgba(56, 189, 248, 0.1); }}
    .module-badge.red {{ color: #EF4444; background: rgba(239, 68, 68, 0.1); }}
    .module-badge.green {{ color: #22C55E; background: rgba(34, 197, 94, 0.1); }}
    
    /* Streamlit overrides to remove default padding around columns and elements */
    [data-testid="column"] > div > div > div > div > div > div > div > div > div.stMarkdown {{
        margin-bottom: 0 !important;
    }}
    
    /* Sidebar specific styling */
    .sidebar-logo-container {{
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 30px;
    }}
    
    .sidebar-logo-icon {{
        width: 24px;
        height: 24px;
        background-color: #2962FF;
        border-radius: 4px;
        display: flex;
        align-items: center;
        justify-content: center;
    }}
    
    .sidebar-logo-text {{
        font-size: 18px;
        font-weight: 800;
        color: {text_primary};
        letter-spacing: 1px;
    }}
    
    .sidebar-label {{
        font-size: 11px;
        font-weight: 600;
        color: {text_muted};
        text-transform: uppercase;
        margin-bottom: 8px;
        display: block;
    }}
    
    </style>
    """

