FROM python:3.9

RUN apt update && apt upgrade -y
RUN apt install python3-pip -y
RUN apt install ffmpeg -y
RUN apt-get install npm

RUN curl -sL https://deb.nodesource.com/setup_16.x | bash -
RUN apt-get install -y nodejs
RUN npm install -g npm@7.22.0
RUN npm i -g npm

COPY . /py
WORKDIR /py

RUN pip3 install --upgrade pip
RUN pip3 install -U -r requirements.txt

CMD python3 -m bot
