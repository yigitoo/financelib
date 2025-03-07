import pandas as pd

def cci(high, low, close, period=20):
  """Calculate Commodity Channel Index."""

  tp = (high + low + close) / 3
  sma_tp = tp.rolling(period).mean()
  mad = tp.rolling(period).apply(lambda x: pd.Series(x).mad())
  return (tp - sma_tp) / (0.015 * mad)
