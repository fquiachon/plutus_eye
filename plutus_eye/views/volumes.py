from uuid import uuid4
from threading import Thread
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from ..volume.volume_analyzer import VolumeAnalyzer
from ..utils.cache import volume_cache
from ..utils.ticker import custom_tickers, default_tickers
from ..utils.pse_tickers import default_tickers as pse_tickers
from ..utils.pse_tickers import custom_tickers as pse_custom_tickers
from plutus_eye.gateway.finnhub_api import FinnhubAPI
from plutus_eye.gateway.pse_api import PseAPI
from plutus_eye.utils.history_range import GlobalHistory, PSEHistory


volumes = Blueprint('volumes', __name__)
global_gateway = FinnhubAPI()
pse_gateway = PseAPI()
global_history = GlobalHistory()
pse_history = PSEHistory()


@volumes.route('/volume/transaction/<string:transaction>', methods=['GET'])
@jwt_required
def get_volume_by_transaction_id(transaction: str):
    if transaction in volume_cache:
        va = volume_cache.get(transaction)
        message = {
            'status': 200,
            'volume': va.increased_symbols
        }
        return jsonify(message), message['status']
    else:
        return jsonify(message='Transaction not found.', transaction_id=transaction), 404


@volumes.route('/volume/transaction/<string:transaction>', methods=['DELETE'])
@jwt_required
def delete_cache_volume(transaction: str):
    if transaction == 'ALL' or transaction == 'all':
        volume_cache.clear()
    elif transaction in volume_cache:
        volume_cache.pop(transaction)
    else:
        return jsonify(message=f'Transaction not found', transaction_id=transaction), 404
    return jsonify(message=f'transaction successfully removed from volume cache', transaction_id=transaction), 200


@volumes.route('/volume/global', methods=['POST'])
@jwt_required
def analyze_multiple_volume():
    if len(volume_cache) > 10:
        return jsonify(message='Cache is Full, try again later or free up some cache'), 409

    va = VolumeAnalyzer(global_gateway, global_history)
    transaction = str(uuid4())

    if request.is_json:
        tickers = request.json['tickers'].split(',')
    else:
        tickers = request.form['tickers'].split(',')

    if tickers[0] == 'CUSTOM' or tickers[0] == 'custom':
        if len(custom_tickers) == 0:
            return jsonify(message='Global tickers is Empty.'), 400
        tickers = custom_tickers

    if tickers[0] == 'ALL' or tickers[0] == 'all':
        all_tickers = []
        for ticks in default_tickers:
            all_tickers.extend(default_tickers[ticks])
        tickers = all_tickers

    if tickers[0] in default_tickers:
        tickers = default_tickers[tickers[0]]

    volume_cache[transaction] = va

    volume_thread = Thread(target=va.analyze_many, args=(tickers,))
    volume_thread.start()

    print(f'Created transaction:{transaction}')
    return jsonify(transaction_id=transaction), 200


@volumes.route('/volume/global/<string:ticker>', methods=['GET'])
@jwt_required
def analyze_volume(ticker: str):
    va = VolumeAnalyzer(global_gateway, global_history)
    volume = va.analyze(ticker)

    message = {
        'status': 200,
        'message': 'OK',
        'volume': volume
    }
    return jsonify(message), message['status']


@volumes.route('/volume/pse/<string:ticker>', methods=['GET'])
@jwt_required
def analyze_pse_volume(ticker: str):
    va = VolumeAnalyzer(pse_gateway, pse_history)
    volume = va.analyze(ticker)

    message = {
        'status': 200,
        'message': 'OK',
        'volume': volume
    }
    return jsonify(message), message['status']


@volumes.route('/volume/pse', methods=['POST'])
@jwt_required
def analyze_multiple_pse_volume():
    if len(volume_cache) > 10:
        return jsonify(message='Cache is Full, try again later or free up some cache'), 409

    va = VolumeAnalyzer(pse_gateway, pse_history)
    transaction = str(uuid4())

    if request.is_json:
        tickers = request.json['tickers'].split(',')
    else:
        tickers = request.form['tickers'].split(',')

    if tickers[0] == 'CUSTOM' or tickers[0] == 'custom':
        if len(pse_custom_tickers) == 0:
            return jsonify(message='Global tickers is Empty.'), 400
        tickers = pse_custom_tickers

    if tickers[0] == 'ALL' or tickers[0] == 'all':
        tickers = pse_tickers

    volume_cache[transaction] = va

    volume_thread = Thread(target=va.analyze_many, args=(tickers,))
    volume_thread.start()
    print(f'Created transaction:{transaction}')
    return jsonify(transaction_id=transaction), 200
