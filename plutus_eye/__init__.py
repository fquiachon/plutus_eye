from flask import Flask
from plutus_eye.extensions import mongo, jwt
from plutus_eye.app import main
from plutus_eye.views.volumes import volumes
from plutus_eye.views.candles import candles
from plutus_eye.views.pse import pse
from plutus_eye.views.global_tickers import global_tickers


def create_app(config_object='plutus_eye.settings'):
    app = Flask(__name__)
    app.config.from_object(config_object)
    jwt.init_app(app)
    mongo.init_app(app)
    app.register_blueprint(main)
    app.register_blueprint(volumes)
    app.register_blueprint(candles)
    app.register_blueprint(global_tickers)
    app.register_blueprint(pse)
    return app
