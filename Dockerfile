FROM nikolaik/python-nodejs:python3.10-nodejs17
RUN apt update && apt upgrade -y
RUN apt install -y ffmpeg python3-pip
COPY . /py
WORKDIR /py
RUN pip3 install -U pip
RUN pip3 install -U -r requirements.txt
CMD ["python3", "main.py"]
