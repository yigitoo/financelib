import pandas as pd

def macd(data, fast_period=12, slow_period=26, signal_period=9):
  """Calculate MACD (Moving Average Convergence Divergence)."""

  fast_ema = pd.Series(data).ewm(span=fast_period).mean()
  slow_ema = pd.Series(data).ewm(span=slow_period).mean()
  macd_line = fast_ema - slow_ema
  signal_line = macd_line.ewm(span=signal_period).mean()
  return macd_line, signal_line
