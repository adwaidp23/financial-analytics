import yfinance as yf
import streamlit as st

@st.cache_data(ttl=3600, show_spinner=False)
def validate_ticker(ticker: str) -> bool:
    """Check if a ticker is valid by attempting to download minimal data.

    Returns True if data is found, False otherwise.
    """
    try:
        # Download a single day of data; if empty, ticker likely invalid
        df = yf.download(ticker, period="1d", progress=False)
        return not df.empty
    except Exception:
        return False

def get_valid_ticker(user_input: str, default: str = "RELIANCE.NS") -> str:
    """Return a validated ticker.

    If the user_input is empty or invalid, fall back to the default ticker and display a warning.
    """
    ticker = user_input.strip()
    if not ticker:
        st.warning(f"No ticker entered. Using default: {default}")
        return default
    if validate_ticker(ticker):
        return ticker
    else:
        st.error(f"Ticker '{ticker}' not found or unavailable. Using default: {default}")
        return default
