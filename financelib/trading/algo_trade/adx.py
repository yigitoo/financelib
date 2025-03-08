import pandas as pd

def adx(high, low, close, period=14):
  """Calculate Average Directional Index. (ADX)"""

  plus_dm = high.diff()
  minus_dm = low.diff()
  tr = pd.DataFrame({
    'HL': high - low,
    'HPC': abs(high - close.shift(1)),
    'LPC': abs(low - close.shift(1))
  }).max(axis=1)

  atr = tr.rolling(period).mean()
  plus_di = 100 * (plus_dm.rolling(period).mean() / atr)
  minus_di = 100 * (minus_dm.rolling(period).mean() / atr)
  dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
  return dx.rolling(period).mean()
