from flask import Flask, jsonify, request
from .cryptor import CryptorTradeBot
import threading
import logging
from datetime import datetime
import time

from financelib.settings import BOT_SERVER_HOST, BOT_SERVER_PORT

app = Flask(__name__)
bot = CryptorTradeBot()
latest_data = {}
backtest_results = {}

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_bot(symbol, coin_name, market, leverage, option_params):
    global latest_data
    while True:
        data = bot.trading_strategy(symbol, coin_name, market, leverage, option_params)
        if data:
            latest_data = data
        time.sleep(60)

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify(latest_data)

@app.route('/api/trade', methods=['POST'])
def start_trade():
    data = request.get_json()
    symbol = data.get('symbol', 'BTC/USDT')
    coin_name = data.get('coin_name', symbol.split('/')[0].lower())
    market = data.get('market', 'spot')
    leverage = data.get('leverage', None)
    option_params = data.get('option_params', None) if market == 'option' else None

    bot_thread = threading.Thread(target=run_bot, args=(symbol, coin_name, market, leverage, option_params))
    bot_thread.daemon = True
    bot_thread.start()

    return jsonify({'message': f'{symbol} için {market} trading başlatıldı', 'symbol': symbol, 'market': market})

@app.route('/api/backtest', methods=['POST'])
def run_backtest():
    data = request.get_json()
    symbol = data.get('symbol', 'BTC/USDT')
    coin_name = data.get('coin_name', symbol.split('/')[0].lower())
    initial_balance = data.get('initial_balance', 10000)
    market = data.get('market', 'spot')
    leverage = data.get('leverage', None)

    result = bot.backtest(symbol, coin_name, initial_balance=initial_balance, market=market, leverage=leverage)
    if result:
        backtest_results[symbol] = result
        return jsonify({
            'symbol': symbol,
            'market': market,
            'initial_balance': result['initial_balance'],
            'final_balance': result['final_balance'],
            'profit': result['profit'],
            'trade_log': result['trade_log'],
            'leverage': result['leverage']
        })
    return jsonify({'error': 'Backtest başarısız'}), 500

@app.route('/api/backtest/<symbol>', methods=['GET'])
def get_backtest_result(symbol):
    result = backtest_results.get(symbol, {})
    if result:
        return jsonify(result)
    return jsonify({'error': f'{symbol} için backtest sonucu bulunamadı'}), 404

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': str(datetime.now())})

def run_server(symbol: str = 'BTC/USDT', coin_name: str = 'bitcoin'):
    bot_thread = threading.Thread(target=run_bot, args=(symbol, coin_name, 'spot', None, None))
    bot_thread.daemon = True
    bot_thread.start()

    app.run(host=BOT_SERVER_HOST, port=BOT_SERVER_PORT, debug=True)
