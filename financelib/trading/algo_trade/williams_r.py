import pandas as pd

def williams_r(high, low, close, period=14):
  """Calculate Williams %R."""

  highest_high = high.rolling(period).max()
  lowest_low = low.rolling(period).min()
  return -100 * (highest_high - close) / (highest_high - lowest_low)
