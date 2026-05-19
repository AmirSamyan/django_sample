FROM python:3.14-alpine

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1
ENV PATH="/PY/BIN:$PATH"

RUN pip install --upgrade pip

COPY req.txt /app/req.txt
COPY . /app


RUN pip install -r req.txt

