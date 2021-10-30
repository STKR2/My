FROM nikolaik/python-nodejs:python3.9-nodejs17
RUN apt update && apt upgrade -y
RUN apt install -y ffmpeg
COPY . /py
WORKDIR /py
RUN pip3 install -U pip
RUN pip3 install -U -r requirements.txt
CMD ["python3", "main.py"]
