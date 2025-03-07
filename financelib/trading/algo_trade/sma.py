import pandas as pd

def sma(data, period=20):
  """Calculate Simple Moving Average."""
  return pd.Series(data).rolling(window=period).mean()
