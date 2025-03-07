import pandas as pd

def rsi(data, period=14):
  """Calculate Relative Strength Index."""

  delta = pd.Series(data).diff()
  gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
  loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
  rs = gain / loss
  return 100 - (100 / (1 + rs))
