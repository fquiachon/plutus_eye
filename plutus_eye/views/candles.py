from uuid import uuid4
from threading import Thread
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from ..utils.cache import pattern_cache
from ..candle_pattern.pattern_analyzer import PatternAnalyzer
from ..utils.ticker import custom_tickers, default_tickers
from plutus_eye.gateway.finnhub_api import FinnhubAPI
from ..utils.pse_tickers import default_tickers as pse_tickers
from ..utils.pse_tickers import custom_tickers as pse_custom_tickers
from plutus_eye.gateway.pse_api import PseAPI
from plutus_eye.utils.history_range import GlobalHistory, PSEHistory


candles = Blueprint('candles', __name__)
gateway = FinnhubAPI()
pse_gateway = PseAPI()
global_history = GlobalHistory()
pse_history = PSEHistory()


@candles.route('/candle/transaction/<string:transaction>', methods=['GET'])
@jwt_required
def get_pattern_by_transaction_id(transaction: str):
    if transaction in pattern_cache:
        pa = pattern_cache.get(transaction)
        message = {
            'pattern': pa.patterns
        }
        return jsonify(message), 200
    else:
        return jsonify(message='Transaction not found.', transaction_id=transaction), 404


@candles.route('/candle/transaction/<string:transaction>', methods=['DELETE'])
@jwt_required
def delete_pattern_cache(transaction: str):
    if transaction == 'ALL' or transaction == 'all':
        pattern_cache.clear()
    elif transaction in pattern_cache:
        pattern_cache.pop(transaction)
    else:
        return jsonify(message=f'Transaction not found', transaction_id=transaction), 404
    return jsonify(message=f'transaction successfully removed from pattern cache', transaction_id=transaction), 200


@candles.route('/global/candle', methods=['POST'])
@jwt_required
def analyze_all_pattern():
    if len(pattern_cache) > 10:
        return jsonify(message='Cache is Full, try again later or free up some cache'), 409

    pa = PatternAnalyzer(gateway, global_history)
    transaction = str(uuid4())

    if request.is_json:
        tickers = request.json['tickers'].split(',')
    else:
        tickers = request.form['tickers'].split(',')

    if tickers[0] == 'ALL' or tickers[0] == 'all':
        if len(custom_tickers) == 0:
            return jsonify(message='Global tickers is Empty.'), 400
        tickers = custom_tickers

    if tickers[0] in default_tickers:
        tickers = default_tickers[tickers[0]]

    pattern_cache[transaction] = pa

    pattern_thread = Thread(target=pa.analyze_many, args=(tickers,))
    pattern_thread.start()

    return jsonify(transaction_id=transaction), 200


@candles.route('/candle/global/<string:ticker>', methods=['GET'])
@jwt_required
def analyze_pattern(ticker: str):
    pa = PatternAnalyzer(gateway, global_history)
    patterns = pa.analyze(ticker)
    message = {
        'patterns': patterns
    }
    return jsonify(message), 200


@candles.route('/candle/pse/<string:ticker>', methods=['GET'])
@jwt_required
def analyze_pse_pattern(ticker: str):
    pa = PatternAnalyzer(gateway, pse_history)
    patterns = pa.analyze(ticker)
    message = {
        'patterns': patterns
    }
    return jsonify(message), 200


@candles.route('/pse/candle', methods=['POST'])
@jwt_required
def analyze_pse_all_pattern():
    if len(pattern_cache) > 10:
        return jsonify(message='Cache is Full, try again later or free up some cache'), 409

    pa = PatternAnalyzer(gateway, pse_history)
    transaction = str(uuid4())

    if request.is_json:
        tickers = request.json['tickers'].split(',')
    else:
        tickers = request.form['tickers'].split(',')

    if tickers[0] == 'ALL' or tickers[0] == 'all':
        tickers = pse_tickers

    if tickers[0] == 'CUSTOM' or tickers[0] == 'custom':
        if len(pse_custom_tickers) == 0:
            return jsonify(message='PSE tickers is Empty.'), 400
        tickers = pse_custom_tickers

    pattern_cache[transaction] = pa

    pattern_thread = Thread(target=pa.analyze_many, args=(tickers,))
    pattern_thread.start()

    return jsonify(transaction_id=transaction), 200
