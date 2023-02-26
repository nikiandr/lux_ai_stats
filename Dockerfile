FROM python:3.8-slim

WORKDIR /usr/src/app

RUN apt-get update -y && apt-get install -y chromium-driver

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY *.py ./
COPY .streamlit .streamlit

CMD streamlit run main.py