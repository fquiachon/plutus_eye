FROM python:3.6.1-alpine

WORKDIR /plutus
ADD . /plutus

RUN pip install -r requirements.txt

CMD ["flask","run","--cert=cert.pem","--key=key.pem"]
