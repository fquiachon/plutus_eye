from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from ..utils.pse_tickers import custom_tickers, default_tickers


pse = Blueprint('pse', __name__)


@pse.route('/pse/tickers', methods=['POST'])
@jwt_required
def add_pse_tickers():
    existing_tickers = []
    added_tickers = []

    if request.is_json:
        tickers = request.json['tickers'].split(',')
    else:
        tickers = request.form['tickers'].split(',')

    for ticker in tickers:
        if ticker in custom_tickers:
            existing_tickers.append(ticker)
        else:
            added_tickers.append(ticker)
            custom_tickers.append(ticker)

    message = {
        'status': 201,
        'Message': f'Ticker Successfully added, {added_tickers}',
    }

    if len(existing_tickers) == 0:
        message['Error'] = []
    else:
        message['Error'] = f'Tickers already exist, {existing_tickers}'

    if len(added_tickers) == 0:
        message['status'] = 409
        message['Message'] = []

    return jsonify(message), message['status']


@pse.route('/pse/tickers', methods=['GET'])
@jwt_required
def get_pse_tickers():
    return jsonify({'tickers': custom_tickers}), 200


@pse.route('/pse/tickers/default', methods=['GET'])
@jwt_required
def get_tickers_by_category():
    return jsonify({'tickers': default_tickers}), 200


@pse.route('/pse/tickers', methods=['DELETE'])
@jwt_required
def del_pse_tickers():
    deleted_tickers = []
    if request.is_json:
        tickers = request.json['tickers'].split(',')
    else:
        tickers = request.form['tickers'].split(',')

    for ticker in tickers:
        if ticker in custom_tickers:
            removed_item = custom_tickers.pop(custom_tickers.index(ticker))
            deleted_tickers.append(removed_item)
    return jsonify({'Successfully deleted tickers': deleted_tickers}), 200
