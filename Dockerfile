FROM python:3.8-slim-buster

WORKDIR /usr/src/app

RUN apt-get update -y
RUN apt install -y chromium-driver

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY main.py main.py
COPY .streamlit .streamlit

CMD streamlit run main.py --server.port $PORT