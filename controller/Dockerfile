FROM python:3.9-alpine

WORKDIR /app

COPY controller.py .
COPY data_driver.py .
COPY requirements.txt .

RUN pip3 install -r requirements.txt

ENTRYPOINT python3 -u controller.py
