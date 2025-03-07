import tweepy
import ccxt
import pandas as pd
import requests
from bs4 import BeautifulSoup
import logging

from settings import (
    BINANCE_API_KEY,
    BINANCE_API_SECRET,
    TWITTER_API_KEY,
    TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_TOKEN_SECRET,
    TIMEFRAME
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DataFetcher:
    def __init__(self):
        self.exchange = ccxt.binance({
            'apiKey': BINANCE_API_KEY,
            'secret': BINANCE_API_SECRET,
            'enableRateLimit': True,
        })
        auth = tweepy.OAuthHandler(TWITTER_ACCESS_TOKEN, TWITTER_API_SECRET)
        auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
        self.twitter_api = tweepy.API(auth, wait_on_rate_limit=True)

    def fetch_realtime_price(self, symbol):
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker['last']
        except Exception as e:
            logging.error(f"{symbol} için anlık fiyat çekme hatası: {e}")
            return None

    def fetch_historical_data(self, symbol, limit=200):
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, TIMEFRAME, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            logging.error(f"{symbol} için geçmiş veri çekme hatası: {e}")
            return None

    def fetch_twitter_data(self, coin_name, count=100):
        try:
            query = f"{coin_name} OR {coin_name.upper()} -filter:retweets"
            tweets = self.twitter_api.search_tweets(q=query, lang='en', count=count, tweet_mode='extended')
            return [tweet.full_text for tweet in tweets]
        except Exception as e:
            logging.error(f"{coin_name} için Twitter veri çekme hatası: {e}")
            return []

    def fetch_news(self, coin_name):
        try:
            url = f"https://www.coindesk.com/tag/{coin_name.lower()}/"
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            headlines = [h.text.strip() for h in soup.find_all('h3', limit=10)]
            logging.debug(f"{coin_name} için çekilen haber başlıkları: {headlines}")
            return headlines
        except Exception as e:
            logging.error(f"{coin_name} için haber çekme hatası: {e}")
            return []
