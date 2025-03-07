import pandas as pd

def ema(data, period=20):
  """Calculate Exponential Moving Average."""
  return pd.Series(data).ewm(span=period).mean()
