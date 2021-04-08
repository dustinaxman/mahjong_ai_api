FROM ubuntu
FROM python:3
MAINTAINER Dustin Axman dustinaxman@gmail.com
ENV PYTHONPATH=/mahjong_server/:$PYTHONPATH
COPY ./api.py /mahjong_server/
COPY ./mahjong_ai.py /mahjong_server/
RUN pip install numpy
RUN pip install flask
RUN pip install flask_restful
CMD python /mahjong_server/api.py