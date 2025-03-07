import pandas as pd

def stochastic(high, low, close, k_period=14, d_period=3):
  """Calculate Stochastic Oscillator."""

  lowest_low = low.rolling(k_period).min()
  highest_high = high.rolling(k_period).max()
  k = 100 * (close - lowest_low) / (highest_high - lowest_low)
  d = k.rolling(d_period).mean()
  return k, d
