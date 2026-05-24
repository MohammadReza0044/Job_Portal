# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . /app

RUN apt-get update && apt-get install -y libmagic1
RUN pip install --upgrade pip
RUN pip install -r requirements.txt


