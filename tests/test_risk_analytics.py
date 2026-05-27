import pytest
import numpy as np
import pandas as pd
from modules.module_3_garch import run_garch_model
from modules.module_8_portfolio import optimize_portfolio
from modules.module_6_var import calc_kupiec_pof
from modules.module_5_monte_carlo import run_gbm_simulation

def test_run_garch_model():
    # Create sample returns that are stationary
    np.random.seed(42)
    dates = pd.date_range(start="2023-01-01", periods=150)
    # Simulate AR(1) plus GARCH-like noise
    returns = np.random.normal(0, 0.01, 150)
    close = 100 * np.exp(np.cumsum(returns))
    
    df = pd.DataFrame({
        'Close': close,
        'Log_Return': returns,
        'Rolling_Vol': pd.Series(returns).rolling(20).std()
    }, index=dates)
    
    cond_vol, omega, alpha, beta, is_stationary = run_garch_model(df)
    
    assert len(cond_vol) == len(df)
    assert isinstance(omega, float)
    assert isinstance(alpha, float)
    assert isinstance(beta, float)
    assert isinstance(is_stationary, bool)

def test_optimize_portfolio():
    np.random.seed(42)
    dates = pd.date_range(start="2023-01-01", periods=100)
    returns = pd.DataFrame({
        'Asset1': np.random.normal(0.0005, 0.01, 100),
        'Asset2': np.random.normal(0.0008, 0.015, 100)
    }, index=dates)
    
    opt_w, opt_ret, opt_vol, opt_sharpe = optimize_portfolio(returns)
    
    assert len(opt_w) == 2
    assert np.isclose(np.sum(opt_w), 1.0)
    assert opt_ret > -1.0
    assert opt_vol > 0.0
    assert opt_sharpe >= 0.0

def test_calc_kupiec_pof():
    # 0 exceptions is valid/safe (fail to reject) -> p-value should be 1.0
    p_val_0 = calc_kupiec_pof(0, 250, 0.95)
    assert p_val_0 == 1.0
    
    # Very high exceptions should lead to low p-value (reject)
    p_val_high = calc_kupiec_pof(50, 250, 0.95)
    assert p_val_high < 0.05
    
    # Expected exceptions (12.5 out of 250) should have high p-value
    p_val_normal = calc_kupiec_pof(12, 250, 0.95)
    assert p_val_normal > 0.05

def test_run_gbm_simulation():
    S0 = 100.0
    mu = 0.08
    sigma = 0.20
    T = 252
    N = 100
    
    paths = run_gbm_simulation(S0, mu, sigma, T, N)
    
    assert paths.shape == (T + 1, N)
    assert np.all(paths[0] == S0)
    assert np.all(paths > 0.0)  # GBM prices must be strictly positive
