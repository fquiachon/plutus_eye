# market

## Pre Setup
<p>Create a new Python 3.x virtual environment</p>

`python3 -m venv env`

### Database Setup
See https://cloud.mongodb.com for the instruction

## Libraries
* Flask==1.1.2
* Flask-JWT-Extended==3.25.0
* Flask-PyMongo==2.3.0
* pymongo==3.11.2
* python-dotenv==0.15.0
* dnspython==2.0.0


## Endpoints
POST /register 201

POST /login 200

POST /global/tickers 201

GET /global/tickers 200

DELETE /global/tickers 200






[https://cloud.mongodb.com]: https://cloud.mongodb.com