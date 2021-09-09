FROM python:latest

RUN apt-get update && apt-get upgrade -y
RUN apt-get install ffmpeg -y
RUN python3 -m pip install --upgrade pip

COPY . /py
WORKDIR /py

RUN python3 -m pip install -U -r requirements.txt

CMD python3 -m bot
