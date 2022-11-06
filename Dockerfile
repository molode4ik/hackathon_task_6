FROM python:3.9

WORKDIR /kyda-web
COPY requirements.txt /kyda-web
RUN pip install -r requirements.txt
COPY . /kyda-web
