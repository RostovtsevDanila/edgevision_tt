FROM python:3.9-alpine

WORKDIR /app

COPY sensor.py .
COPY requirements.txt .

RUN pip3 install -r requirements.txt

ENTRYPOINT python3 -u sensor.py
