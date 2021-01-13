from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from ..utils.ticker import custom_tickers, default_tickers


global_tickers = Blueprint('global_tickers', __name__)


@global_tickers.route('/global/tickers', methods=['POST'])
@jwt_required
def add_global_tickers():
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


@global_tickers.route('/global/tickers', methods=['GET'])
@jwt_required
def get_global_tickers():
    return jsonify({'tickers': custom_tickers}), 200


@global_tickers.route('/global/tickers/<string:category>', methods=['GET'])
@jwt_required
def get_tickers_by_category(category: str):
    if category in default_tickers:
        return jsonify({category: default_tickers[category]}), 200
    else:
        return jsonify(message=f'Category not found. Use only technology, consumer_goods, health_care,' +
                               ' services, finance, conglomerates, industrial_goods,'
                               'basic_materials, utilities and commodities'), 404


@global_tickers.route('/global/tickers', methods=['DELETE'])
@jwt_required
def del_global_tickers():
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