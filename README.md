# Plutus Eye, Is a Global Market prediction web API that aims to improve and automate analysis of the stock market price direction based on available historical data. 

## Pre Setup
### Development Setup
<p>Create a new Python 3.x virtual environment</p>
* Setup python environment

`python3 -m venv env`

* Python Libraries
    * Flask==1.1.2
    * Flask-JWT-Extended==3.25.0
    * Flask-PyMongo==2.3.0
    * pymongo==3.11.2
    * python-dotenv==0.15.0
    * dnspython==2.0.0

* Environment Variables on `.env` file
    * FLASK_APP=app
    * FLASK_ENV=development
    * MONGO_URI=mongodb+srv://`dbuser`:`dbpassword`@`<mongodb-host>`/`<dbname>`?retryWrites=true&w=majority
    * JWT_SECRET_KEY='super-secret'
    * GATEWAY_TOKEN = 'bv1io9f48v6o8DemoX'
    
### Database Setup
See https://cloud.mongodb.com for the instruction


## Endpoints
POST /register 201

POST /login 200

POST /global/tickers 201

GET /global/tickers 200

DELETE /global/tickers 200

POST /global/candle  201

GET /global/candle/<string:ticker> 200

GET /global/candle/transaction/<string:transaction> 200

DELETE /global/candle/transaction/<string:transaction> 200

POST /global/volume 201

GET /global/volume/<string:ticker> 200

GET /global/volume/transaction/<string:transaction> 200

DELETE /global/volume/transaction/<string:transaction> 200
