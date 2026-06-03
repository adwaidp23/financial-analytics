import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_stock_data(ticker, start_date, end_date):
    """
    Fetches historical stock data using yfinance.
    Calculates daily log returns and 20-day rolling volatility.
    """
    try:
        df = yf.download(ticker, start=start_date, end=end_date)
        if df.empty:
            return pd.DataFrame()
        
        # yfinance returns a MultiIndex column DataFrame if multiple tickers, 
        # but sometimes does for single tickers in newer versions too.
        if isinstance(df.columns, pd.MultiIndex):
            # Find the level that contains 'Close' and use it
            if 'Close' in df.columns.get_level_values(0):
                df.columns = df.columns.get_level_values(0)
            elif 'Close' in df.columns.get_level_values(1):
                df.columns = df.columns.get_level_values(1)
            else:
                df.columns = df.columns.get_level_values(0)
            
        df = df.dropna(subset=['Close'])
        
        # Calculate Log Returns
        df['Log_Return'] = np.log(df['Close'] / df['Close'].shift(1))
        
        # Calculate Rolling Volatility (20-day annualized)
        df['Rolling_Vol'] = df['Log_Return'].rolling(window=20).std() * np.sqrt(252)
        
        return df
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_financial_metrics(ticker):
    """
    Fetches basic info and financial ratios needed for DCF and Credit Risk models.
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return info
    except Exception as e:
        print(f"Error fetching metrics for {ticker}: {e}")
        return {}

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_portfolio_data(tickers, start_date, end_date):
    """
    Fetches closing prices for a list of tickers, aligns them, and returns a DataFrame of Log Returns.
    """
    try:
        df = yf.download(tickers, start=start_date, end=end_date)
        if df.empty:
            return pd.DataFrame()
        
        # Robustly extract the 'Close' prices
        if isinstance(df.columns, pd.MultiIndex):
            if 'Close' in df.columns.get_level_values(0):
                df = df['Close']
            elif 'Close' in df.columns.get_level_values(1):
                df = df.xs('Close', axis=1, level=1)
        else:
            if 'Close' in df.columns:
                df = df[['Close']]
                
        df = df.dropna()
        returns = np.log(df / df.shift(1)).dropna()
        return returns
    except Exception as e:
        print(f"Error fetching portfolio data: {e}")
        return pd.DataFrame()
