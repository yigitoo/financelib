import pandas as pd

def bollinger_bands(data, period=20, std_dev=2):
  """Calculate Bollinger Bands."""

  middle_band = pd.Series(data).rolling(window=period).mean()
  std = pd.Series(data).rolling(window=period).std()
  upper_band = middle_band + (std * std_dev)
  lower_band = middle_band - (std * std_dev)
  return upper_band, middle_band, lower_band
