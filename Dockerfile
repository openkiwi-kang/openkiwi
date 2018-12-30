FROM ubuntu:latest

USER root
ADD . /openkiwi
WORKDIR /openkiwi
RUN apt-get update
RUN apt install -y python3-pip python-dev python3-setuptools
RUN python3 -m pip install -r requirements.txt

CMD python3 wiki.py
EXPOSE 5555