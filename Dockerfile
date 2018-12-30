FROM ubuntu:latest

RUN sudo apt-get update
RUN sudo apt install python3-pip python-dev
RUN python3 -m pip install -r requirements.txt

CMD python3 wiki.py