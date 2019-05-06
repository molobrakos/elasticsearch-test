FROM python:3

RUN pip install elasticsearch

WORKDIR /app

COPY main.py .

