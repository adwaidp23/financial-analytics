# conftest.py – shared pytest fixtures

import pandas as pd
import numpy as np
import pytest

@pytest.fixture
def sample_stock_df():
    """Return a small DataFrame mimicking yfinance output for a single ticker."""
    dates = pd.date_range(start="2023-01-01", periods=5, freq="D")
    data = {
        "Open": [100, 101, 102, 103, 104],
        "High": [101, 102, 103, 104, 105],
        "Low": [99, 100, 101, 102, 103],
        "Close": [100.5, 101.5, 102.5, 103.5, 104.5],
        "Adj Close": [100.5, 101.5, 102.5, 103.5, 104.5],
        "Volume": [1000, 1100, 1200, 1300, 1400],
    }
    return pd.DataFrame(data, index=dates)
