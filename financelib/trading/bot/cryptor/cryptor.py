import ccxt
import pandas as pd
import numpy as np
import time
import logging

from .data_fetcher import DataFetcher
from .sentiment_analyzer import SentimentAnalyzer
from .price_predictor import PricePredictor

from settings import (
    BINANCE_API_KEY,
    BINANCE_API_SECRET,
    CRYPTO_TRADE_AMOUNT
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('trading_bot.log'), logging.StreamHandler()]
)

class CryptorTradeBot:
    def __init__(self):
        self.exchange = ccxt.binance({
            'apiKey': BINANCE_API_KEY,
            'secret': BINANCE_API_SECRET,
            'enableRateLimit': True,
        })
        self.futures_exchange = ccxt.binance({
            'apiKey': BINANCE_API_KEY,
            'secret': BINANCE_API_SECRET,
            'enableRateLimit': True,
            'options': {'defaultType': 'future'}
        })
        self.data_fetcher = DataFetcher()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.price_predictor = PricePredictor()
        self.amount = CRYPTO_TRADE_AMOUNT
        self.positions = {}
        self.trades = {}

        self.stop_loss_pct = 0.02
        self.take_profit_pct = 0.05
        self.leverage = 5
        self.min_leverage = 1
        self.max_leverage = 20
        self.margin_threshold = 0.2
        self.margin_buffer = 100

    def set_leverage(self, symbol, leverage):
        try:
            self.futures_exchange.fapiPrivate_post_leverage({
                'symbol': symbol.replace('/', ''),
                'leverage': min(max(leverage, self.min_leverage), self.max_leverage)
            })
            self.leverage = leverage
            logging.info(f"{symbol} için kaldıraç {leverage}x ayarlandı")
        except Exception as e:
            logging.error(f"Kaldıraç ayarlama hatası: {symbol} - {str(e)}")

    def calculate_volatility(self, df):
        volatilities = {
            'short_term': df['close'].pct_change().rolling(window=5).std().iloc[-1],
            'medium_term': df['close'].pct_change().rolling(window=20).std().iloc[-1],
            'long_term': df['close'].pct_change().rolling(window=50).std().iloc[-1]
        }
        avg_volatility = np.mean(list(volatilities.values()))
        logging.debug(f"{df['close'].name} volatilite: Kısa: {volatilities['short_term']:.4f}, "
                      f"Orta: {volatilities['medium_term']:.4f}, Uzun: {volatilities['long_term']:.4f}, "
                      f"Ortalama: {avg_volatility:.4f}")
        return volatilities, avg_volatility

    def calculate_dynamic_leverage(self, df, sentiment_score):
        _, avg_volatility = self.calculate_volatility(df)
        volatility_factor = min(max(avg_volatility * 100, 0.5), 2.0)
        sentiment_factor = 1 + (sentiment_score * 0.5)
        leverage = self.leverage * sentiment_factor / volatility_factor
        dynamic_leverage = min(max(int(leverage), self.min_leverage), self.max_leverage)
        logging.info(f"Dinamik kaldıraç: {dynamic_leverage}x (Volatilite: {avg_volatility:.4f}, Sentiment: {sentiment_score:.2f})")
        return dynamic_leverage

    def calculate_technical_indicators(self, df):
        df['sma_short'] = df['close'].rolling(window=10).mean()
        df['sma_long'] = df['close'].rolling(window=50).mean()
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        df['ema12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['ema26'] = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = df['ema12'] - df['ema26']
        df['signal_line'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['bb_middle'] = df['close'].rolling(window=20).mean()
        df['bb_std'] = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + (df['bb_std'] * 2)
        df['bb_lower'] = df['bb_middle'] - (df['bb_std'] * 2)
        return df.dropna()

    def get_balance(self, market='spot'):
        try:
            exchange = self.futures_exchange if market == 'futures' else self.exchange
            balance = exchange.fetch_balance()
            logging.debug(f"{market} bakiyesi: {balance['free']}")
            return balance['free']
        except Exception as e:
            logging.error(f"{market} bakiye kontrol hatası: {str(e)}")
            return None

    def check_margin_level(self, symbol):
        try:
            account = self.futures_exchange.fapiPrivate_get_account()
            for asset in account['assets']:
                if asset['asset'] == symbol.split('/')[1]:
                    margin_ratio = float(asset['marginRatio'])
                    logging.info(f"{symbol} margin oranı: {margin_ratio:.4f}")
                    if margin_ratio < self.margin_threshold:
                        logging.warning(f"{symbol} için margin düşük: {margin_ratio:.4f}")
                        return 'low_margin', margin_ratio
                    return None, margin_ratio
            return None, None
        except Exception as e:
            logging.error(f"Margin kontrol hatası: {symbol} - {str(e)}")
            return None, None

    def increase_margin(self, symbol, amount):
        try:
            self.futures_exchange.fapiPrivate_post_transfer({
                'asset': symbol.split('/')[1],
                'amount': amount,
                'type': 1
            })
            logging.info(f"{symbol} için {amount} USDT margin eklendi")
            return True
        except Exception as e:
            logging.error(f"Margin artırma hatası: {symbol} - {str(e)}")
            return False

    def execute_spot_trade(self, symbol, side, price):
        try:
            if side == 'buy':
                order = self.exchange.create_limit_buy_order(symbol, self.amount, price)
                logging.info(f"Spot {symbol} için alım: {self.amount} @ {price}")
                self.trades[symbol] = {
                    'entry_price': price,
                    'stop_loss': price * (1 - self.stop_loss_pct),
                    'take_profit': price * (1 + self.take_profit_pct),
                    'side': 'long',
                    'market': 'spot'
                }
            elif side == 'sell':
                order = self.exchange.create_limit_sell_order(symbol, self.amount, price)
                logging.info(f"Spot {symbol} için satış: {self.amount} @ {price}")
                del self.trades[symbol]
            return order
        except Exception as e:
            logging.error(f"Spot {symbol} için trade hatası: {str(e)}")
            return None

    def execute_futures_trade(self, symbol, side, price):
        try:
            futures_symbol = symbol.replace('/', '')
            if side == 'buy':
                order = self.futures_exchange.create_limit_buy_order(symbol, self.amount, price)
                logging.info(f"Futures {symbol} için alım: {self.amount} @ {price} (Kaldıraç: {self.leverage}x)")
                self.trades[symbol] = {
                    'entry_price': price,
                    'stop_loss': price * (1 - self.stop_loss_pct),
                    'take_profit': price * (1 + self.take_profit_pct),
                    'side': 'long',
                    'market': 'futures'
                }
            elif side == 'sell':
                order = self.futures_exchange.create_limit_sell_order(symbol, self.amount, price)
                logging.info(f"Futures {symbol} için satış: {self.amount} @ {price} (Kaldıraç: {self.leverage}x)")
                del self.trades[symbol]
            return order
        except Exception as e:
            logging.error(f"Futures {symbol} için trade hatası: {str(e)}")
            return None

    def execute_option_trade(self, symbol, option_type='call', strike_price=None, expiry=None):
        try:
            current_price = self.data_fetcher.fetch_realtime_price(symbol)
            logging.info(f"{symbol} için {option_type} opsiyonu alındı: Strike {strike_price}, Expiry {expiry}")
            self.trades[symbol] = {
                'entry_price': current_price,
                'strike_price': strike_price,
                'option_type': option_type,
                'expiry': expiry,
                'market': 'option'
            }
            return {'status': 'success', 'symbol': symbol, 'type': option_type}
        except Exception as e:
            logging.error(f"Opsiyon {symbol} için hata: {str(e)}")
            return None

    def check_risk_management(self, symbol, current_price):
        if symbol in self.trades:
            trade = self.trades[symbol]
            if trade['market'] in ['spot', 'futures'] and trade['side'] == 'long':
                if current_price <= trade['stop_loss']:
                    logging.info(f"{symbol} için stop-loss tetiklendi: {current_price}")
                    self.execute_trade(symbol, 'sell', current_price, trade['market'])
                    return 'sell'
                elif current_price >= trade['take_profit']:
                    logging.info(f"{symbol} için take-profit tetiklendi: {current_price}")
                    self.execute_trade(symbol, 'sell', current_price, trade['market'])
                    return 'sell'
                elif trade['market'] == 'futures':
                    margin_status, margin_ratio = self.check_margin_level(symbol)
                    if margin_status == 'low_margin':
                        logging.warning(f"{symbol} için margin düşük: {margin_ratio:.4f}")
                        if self.increase_margin(symbol, self.margin_buffer):
                            logging.info(f"{symbol} için margin artırıldı")
                        else:
                            logging.info(f"{symbol} için margin artırma başarısız, pozisyon kapatılıyor")
                            self.execute_trade(symbol, 'sell', current_price, 'futures')
                            return 'sell'
            elif trade['market'] == 'option':
                if time.time() > trade['expiry'] and trade['option_type'] == 'call' and current_price < trade['strike_price']:
                    logging.info(f"{symbol} call opsiyonu değersiz kapandı")
                    del self.trades[symbol]
                    return 'expired'
        return None

    def execute_trade(self, symbol, side, price, market='spot'):
        if market == 'spot':
            return self.execute_spot_trade(symbol, side, price)
        elif market == 'futures':
            return self.execute_futures_trade(symbol, side, price)
        return None

    def trading_strategy(self, symbol, coin_name, market='spot', leverage=None, option_params=None):
        df = self.data_fetcher.fetch_historical_data(symbol)
        if df is None:
            return None

        df = self.calculate_technical_indicators(df)
        current_price = self.data_fetcher.fetch_realtime_price(symbol)
        tweets = self.data_fetcher.fetch_twitter_data(coin_name)
        news = self.data_fetcher.fetch_news(coin_name)
        sentiment_score = self.sentiment_analyzer.get_sentiment_score(coin_name, tweets, news)

        self.price_predictor.train(df)
        predicted_price = self.price_predictor.predict(df)

        volatilities, avg_volatility = self.calculate_volatility(df)

        if market == 'futures':
            dynamic_leverage = self.calculate_dynamic_leverage(df, sentiment_score)
            self.set_leverage(symbol, leverage if leverage else dynamic_leverage)

        latest = df.iloc[-1]
        previous = df.iloc[-2]

        sma_cross_buy = previous['sma_short'] < previous['sma_long'] and latest['sma_short'] > latest['sma_long']
        sma_cross_sell = previous['sma_short'] > previous['sma_long'] and latest['sma_short'] < latest['sma_long']
        rsi_buy = latest['rsi'] < 30
        rsi_sell = latest['rsi'] > 70
        macd_buy = previous['macd'] < previous['signal_line'] and latest['macd'] > latest['signal_line']
        macd_sell = previous['macd'] > previous['signal_line'] and latest['macd'] < latest['signal_line']
        bb_buy = current_price < latest['bb_lower']
        bb_sell = current_price > latest['bb_upper']

        momentum_score = (predicted_price - current_price) / current_price
        mean_reversion_score = (latest['bb_middle'] - current_price) / latest['bb_std']

        sentiment_weight = abs(sentiment_score)
        buy_confidence = (0.3 * sma_cross_buy + 0.2 * rsi_buy + 0.2 * macd_buy + 0.3 * bb_buy +
                          0.2 * (momentum_score > 0.015) + 0.1 * (mean_reversion_score > 1)) * (1 + sentiment_weight)
        sell_confidence = (0.3 * sma_cross_sell + 0.2 * rsi_sell + 0.2 * macd_sell + 0.3 * bb_sell +
                           0.2 * (momentum_score < -0.015) + 0.1 * (mean_reversion_score < -1)) * (1 + sentiment_weight)

        buy_signal = buy_confidence > 0.7
        sell_signal = sell_confidence > 0.7

        risk_action = self.check_risk_management(symbol, current_price)
        if risk_action == 'sell':
            self.positions[symbol] = False

        balance = self.get_balance(market)
        if balance is None:
            return None

        logging.info(f"{symbol} ({market}) - Mevcut: {current_price}, Tahmin: {predicted_price}, "
                     f"Duygu: {sentiment_score:.2f}, Alım Güven: {buy_confidence:.2f}, Satış Güven: {sell_confidence:.2f}, "
                     f"Kaldıraç: {self.leverage}, Volatilite: {avg_volatility:.4f}")

        in_position = self.positions.get(symbol, False)
        base_currency = symbol.split('/')[1]
        coin = symbol.split('/')[0]

        if market == 'option' and option_params and not in_position:
            self.execute_option_trade(symbol, option_params['type'], option_params['strike_price'], option_params['expiry'])
            self.positions[symbol] = True
        elif market in ['spot', 'futures']:
            leverage_factor = self.leverage if market == 'futures' else 1
            if buy_signal and not in_position and balance[base_currency] > self.amount * current_price / leverage_factor:
                self.execute_trade(symbol, 'buy', current_price, market)
                self.positions[symbol] = True
            elif sell_signal and in_position and balance[coin] >= self.amount:
                self.execute_trade(symbol, 'sell', current_price, market)
                self.positions[symbol] = False

        margin_status, margin_ratio = self.check_margin_level(symbol) if market == 'futures' else (None, None)

        return {
            'symbol': symbol,
            'market': market,
            'current_price': current_price,
            'predicted_price': predicted_price,
            'sentiment_score': sentiment_score,
            'buy_confidence': buy_confidence,
            'sell_confidence': sell_confidence,
            'buy_signal': buy_signal,
            'sell_signal': sell_signal,
            'in_position': in_position,
            'rsi': latest['rsi'],
            'macd': latest['macd'],
            'bb_upper': latest['bb_upper'],
            'bb_lower': latest['bb_lower'],
            'stop_loss': self.trades.get(symbol, {}).get('stop_loss', None),
            'take_profit': self.trades.get(symbol, {}).get('take_profit', None),
            'leverage': self.leverage if market == 'futures' else 1,
            'margin_ratio': margin_ratio,
            'volatility': volatilities
        }

    def run(self, symbol='BTC/USDT', coin_name='bitcoin', market='spot', leverage=None, option_params=None):
        logging.info(f"{symbol} ({market}) için Trading Bot başlatıldı...")
        while True:
            try:
                self.trading_strategy(symbol, coin_name, market, leverage, option_params)
                time.sleep(3600)
            except Exception as e:
                logging.error(f"{symbol} için bot hatası: {str(e)}")
                time.sleep(60)
