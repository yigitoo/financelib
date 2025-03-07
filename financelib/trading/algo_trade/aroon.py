import pandas as pd

def aroon(high, low, period=25):
  """Calculate Aroon Indicator."""

  aroon_up = 100 * (period - high.rolling(period + 1).apply(lambda x: x.argmax())) / period
  aroon_down = 100 * (period - low.rolling(period + 1).apply(lambda x: x.argmin())) / period
  return aroon_up, aroon_down
