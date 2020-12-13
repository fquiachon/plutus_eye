from flask import Flask, jsonify, request
from uuid import uuid4
from threading import Thread
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from flask_pymongo import PyMongo

from .utils.cache import pattern_cache
from .utils.ticker import global_tickers
from .settings import MONGO_URI, JWT_SECRET_KEY
from .candle_pattern.pattern_analyzer import PatternAnalyzer

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
app.config['MONGO_URI'] = MONGO_URI

jwt = JWTManager(app)
mongo = PyMongo(app)


@app.route('/global/candle/transaction/<string:transaction>', methods=['GET'])
@jwt_required
def get_pattern_by_transaction_id(transaction: str):
    if transaction in pattern_cache:
        pa = pattern_cache.get(transaction)
        message = {
            'pattern': pa.patterns
        }
        return jsonify(message), 200
    else:
        return jsonify(message=f'Transaction:{transaction} not found'), 404


@app.route('/global/candle/transaction/<string:transaction>', methods=['DELETE'])
@jwt_required
def delete_pattern_cache(transaction: str):
    if transaction == 'ALL' or transaction == 'all':
        pattern_cache.clear()
    elif transaction in pattern_cache:
        pattern_cache.pop(transaction)
    else:
        return jsonify(message=f'Transaction not found', transaction_id=transaction), 404
    return jsonify(message=f'transaction successfully removed from pattern cache', transaction_id=transaction), 200


@app.route('/global/candle', methods=['POST'])
@jwt_required
def analyze_all_pattern():
    if len(pattern_cache) > 10:
        return jsonify(message='Cache is Full, try again later or free up some cache'), 409

    pa = PatternAnalyzer()
    transaction = str(uuid4())

    if request.is_json:
        tickers = request.json['tickers'].split(',')
    else:
        tickers = request.form['tickers'].split(',')

    if tickers[0] == 'ALL' or tickers[0] == 'all':
        if len(global_tickers) == 0:
            return jsonify(message='Global tickers is Empty.'), 400
        tickers = global_tickers

    pattern_cache[transaction] = pa

    pattern_thread = Thread(target=pa.analyze_many, args=(tickers,))
    pattern_thread.start()

    return jsonify(transaction_id=transaction), 200


@app.route('/global/candle/<string:ticker>', methods=['GET'])
@jwt_required
def analyze_pattern(ticker: str):
    pa = PatternAnalyzer()
    patterns = pa.analyze(ticker)
    message = {
        'patterns': patterns
    }
    return jsonify(message), 200


@app.route('/global/tickers', methods=['POST'])
@jwt_required
def add_global_tickers():
    existing_tickers = []
    added_tickers = []

    if request.is_json:
        tickers = request.json['tickers'].split(',')
    else:
        tickers = request.form['tickers'].split(',')

    for ticker in tickers:
        if ticker in global_tickers:
            existing_tickers.append(ticker)
        else:
            added_tickers.append(ticker)
            global_tickers.append(ticker)

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


@app.route('/global/tickers', methods=['GET'])
@jwt_required
def get_global_tickers():
    return jsonify({'tickers' : global_tickers}), 200


@app.route('/global/tickers', methods=['DELETE'])
@jwt_required
def del_global_tickers():
    deleted_tickers = []
    if request.is_json:
        tickers = request.json['tickers'].split(',')
    else:
        tickers = request.form['tickers'].split(',')

    for ticker in tickers:
        if ticker in global_tickers:
            removed_item = global_tickers.pop(global_tickers.index(ticker))
            deleted_tickers.append(removed_item)
    return jsonify({'Successfully deleted tickers': deleted_tickers}), 200


@app.route('/')
def welcome():
    return jsonify(message="Welcome to Plutus Eye API 2020"), 200


@app.route('/register', methods=['POST'])
def register():
    try:
        email = request.form['email']
        users_collection = mongo.db.users
        in_use = users_collection.find_one({"email": email})
        if in_use:
            return jsonify(message="Email already in used."), 409
        else:
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            password = request.form['password']
            users_collection.insert({'first_name': first_name,
                                     'last_name': last_name,
                                     'email': email,
                                     'password': password
                                     })
            return jsonify(message="User created successfully"), 201
    except Exception as e:
        return jsonify(message=f"Error occurred, {e}"), 400


@app.route('/login', methods=['POST'])
def login():
    if request.is_json:
        email = request.json['email']
        password = request.json['password']
    else:
        email = request.form['email']
        password = request.form['password']
    users_collection = mongo.db.users
    user = users_collection.find_one({"$and": [{"email": email}, {"password": password}]})
    if user:
        access_token = create_access_token(identity=email)
        return jsonify(meassage="Login succeeded", access_token=access_token)
    else:
        return jsonify(meassage="Bad Email or Password"), 401


if __name__ == '__main__':
    app.run()
