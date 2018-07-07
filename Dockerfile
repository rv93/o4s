FROM ubuntu:14.04

RUN apt-get update
RUN apt-get install -y --force-yes python python-dev python-setuptools software-properties-common gcc python-pip
RUN apt-get clean all

RUN pip install pyzmq

COPY assignment/ /src 

EXPOSE 5000
EXPOSE 5001

WORKDIR /src

CMD /bin/sh init_script.sh
