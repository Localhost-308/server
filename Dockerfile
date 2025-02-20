FROM python:3.11-alpine

COPY . /api-6-semestre

WORKDIR /api-6-semestre

RUN pip3 install -r requirements.txt