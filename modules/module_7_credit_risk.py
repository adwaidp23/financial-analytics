import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import yfinance as yf
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, accuracy_score, confusion_matrix
from utils.theme import apply_theme

@st.cache_data(show_spinner=False)
def generate_and_train_pd_model():
    """Generates synthetic corporate data and trains a Logistic Regression credit risk model.

    Returns:
        tuple: A tuple containing:
            - model (LogisticRegression): The trained model.
            - auc (float): AUC-ROC score.
            - acc (float): Accuracy score.
            - cm (np.ndarray): Confusion matrix.
    """
    np.random.seed(42)
    N = 500
    
    # Features
    # Debt-to-Equity, Interest Coverage Ratio, Current Ratio, Return on Equity (ROE), Net Profit Margin
    dte = np.random.uniform(0.1, 5.0, N)
    icr = np.random.uniform(-2.0, 15.0, N)
    cr = np.random.uniform(0.5, 3.0, N)
    roe = np.random.uniform(-0.2, 0.4, N)
    npm = np.random.uniform(-0.1, 0.3, N)
    
    z = 0.5 * dte - 0.2 * icr - 0.5 * cr - 2.0 * roe - 3.0 * npm + np.random.normal(0, 1, N)
    
    # Sigmoid function
    prob = 1 / (1 + np.exp(-z))
    
    # Threshold for default (1) or non-default (0)
    y = (prob > 0.5).astype(int)
    
    X = pd.DataFrame({
        'DebtToEquity': dte,
        'InterestCoverage': icr,
        'CurrentRatio': cr,
        'ROE': roe,
        'NetProfitMargin': npm
    })
    
    model = LogisticRegression()
    model.fit(X, y)
    
    y_pred = model.predict(X)
    y_prob = model.predict_proba(X)[:, 1]
    
    auc = roc_auc_score(y, y_prob)
    acc = accuracy_score(y, y_pred)
    cm = confusion_matrix(y, y_pred)
    
    return model, auc, acc, cm

@st.cache_data(show_spinner=False)
def fetch_financial_ratios(ticker):
    """Fetches key financial ratios for a given stock ticker, falling back to industry averages if unavailable.

    Args:
        ticker (str): The stock ticker (e.g., 'RELIANCE.NS').

    Returns:
        pd.DataFrame: A single-row DataFrame containing the credit risk model features.
    """
    # High-quality industry averages for the 5 NSE tickers to guard against empty API returns
    DEFAULT_RATIOS = {
        'RELIANCE.NS': {'DebtToEquity': 0.40, 'InterestCoverage': 6.5, 'CurrentRatio': 1.25, 'ROE': 0.09, 'NetProfitMargin': 0.08},
        'TCS.NS': {'DebtToEquity': 0.02, 'InterestCoverage': 85.0, 'CurrentRatio': 2.50, 'ROE': 0.45, 'NetProfitMargin': 0.19},
        'INFY.NS': {'DebtToEquity': 0.05, 'InterestCoverage': 60.0, 'CurrentRatio': 2.10, 'ROE': 0.32, 'NetProfitMargin': 0.16},
        'HDFCBANK.NS': {'DebtToEquity': 0.85, 'InterestCoverage': 2.5, 'CurrentRatio': 1.20, 'ROE': 0.16, 'NetProfitMargin': 0.18},
        'WIPRO.NS': {'DebtToEquity': 0.12, 'InterestCoverage': 18.0, 'CurrentRatio': 1.85, 'ROE': 0.15, 'NetProfitMargin': 0.11}
    }
    
    defaults = DEFAULT_RATIOS.get(ticker, {'DebtToEquity': 0.50, 'InterestCoverage': 5.0, 'CurrentRatio': 1.5, 'ROE': 0.15, 'NetProfitMargin': 0.10})
    
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        if not info or not isinstance(info, dict):
            info = {}
    except Exception:
        info = {}
        
    dte_val = info.get('debtToEquity')
    dte = dte_val / 100 if dte_val is not None else defaults['DebtToEquity']
    
    # Interest coverage ratio is rarely in info, so we use a safe corporate proxy
    icr = defaults['InterestCoverage']
    
    cr = info.get('currentRatio', defaults['CurrentRatio'])
    if cr is None: cr = defaults['CurrentRatio']
    
    roe = info.get('returnOnEquity', defaults['ROE'])
    if roe is None: roe = defaults['ROE']
    
    npm = info.get('profitMargins', defaults['NetProfitMargin'])
    if npm is None: npm = defaults['NetProfitMargin']
    
    return pd.DataFrame({
        'DebtToEquity': [float(dte)],
        'InterestCoverage': [float(icr)],
        'CurrentRatio': [float(cr)],
        'ROE': [float(roe)],
        'NetProfitMargin': [float(npm)]
    })

def render_module_7(ticker):
    """Renders the Credit Risk Modeling (PD) dashboard page in Streamlit.

    Args:
        ticker (str): The selected stock ticker.
    """
    st.subheader("Module 7: Credit Risk Modeling (PD)")
    
    model, auc, acc, cm = generate_and_train_pd_model()
    
    features_df = fetch_financial_ratios(ticker)
    pd_prob = model.predict_proba(features_df)[0, 1]
    pd_percentage = pd_prob * 100
    
    # Map PD to Credit Score (300-850)
    credit_score = 850 - (pd_prob * (850 - 300))
    
    # Map to Risk Grade
    if credit_score >= 800: grade = "AAA"
    elif credit_score >= 750: grade = "AA"
    elif credit_score >= 700: grade = "A"
    elif credit_score >= 650: grade = "BBB"
    elif credit_score >= 600: grade = "BB"
    elif credit_score >= 500: grade = "B"
    elif credit_score >= 400: grade = "CCC"
    else: grade = "D"
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown(f"**Probability of Default (PD):** <span style='font-size:24px; font-weight:bold;'>{pd_percentage:.2f}%</span>", unsafe_allow_html=True)
        
        # Semicircular Gauge Chart
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = credit_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': f"Credit Score<br><span style='font-size:0.8em;color:gray'>Grade: {grade}</span>"},
            gauge = {
                'axis': {'range': [300, 850]},
                'bar': {'color': "white"},
                'steps': [
                    {'range': [300, 500], 'color': "red"},
                    {'range': [500, 650], 'color': "orange"},
                    {'range': [650, 750], 'color': "yellow"},
                    {'range': [750, 850], 'color': "green"}],
                'threshold': {
                    'line': {'color': "white", 'width': 4},
                    'thickness': 0.75,
                    'value': credit_score}
            }))
            
        apply_theme(fig)
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.markdown("**Model Performance Metrics**")
        st.write(f"- **AUC-ROC Score:** {auc:.3f}")
        st.write(f"- **Accuracy:** {acc*100:.1f}%")
        
        st.markdown("**Confusion Matrix (Synthetic Data)**")
        cm_df = pd.DataFrame(cm, index=['Actual Non-Default', 'Actual Default'], columns=['Predicted Non-Default', 'Predicted Default'])
        st.dataframe(cm_df)
        
    # 7d: 15-month PD trend simulation
    st.markdown("**15-Month PD Trend Simulation**")
    
    months = [f"M{i}" for i in range(1, 16)]
    trend_pds = []
    
    current_features = features_df.copy()
    
    np.random.seed(100)
    for i in range(15):
        # Apply random shocks to features
        current_features *= np.random.normal(1.0, 0.05, size=current_features.shape)
        
        prob = model.predict_proba(current_features)[0, 1]
        trend_pds.append(prob * 100)
        
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(x=months, y=trend_pds, mode='lines+markers', line=dict(color='#00cc96', width=2)))
    apply_theme(fig_trend)
    st.plotly_chart(fig_trend, use_container_width=True)
