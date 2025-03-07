import pandas as pd

def atr(high, low, close, period=14):
  """Calculate Average True Range."""

  tr = pd.DataFrame({
    'HL': high - low,
    'HPC': abs(high - close.shift(1)),
    'LPC': abs(low - close.shift(1))
  }).max(axis=1)
  return tr.rolling(period).mean()
