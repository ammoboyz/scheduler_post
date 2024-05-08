FROM ubuntu:latest
FROM python:3.11

RUN apt update

WORKDIR /usr/app/src

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN apt-get update
ENV TZ=Europe/Moscow
RUN apt-get install -y tzdata
COPY . .
