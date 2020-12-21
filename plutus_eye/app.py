from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from .extensions import mongo


main = Blueprint('main', __name__)


@main.route('/')
def welcome():
    return jsonify(message="Welcome to Plutus Eye API 2020"), 200


@main.route('/register', methods=['POST'])
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


@main.route('/login', methods=['POST'])
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
