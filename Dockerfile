# Container Configuration
FROM ubuntu:14.04
MAINTAINER outcastgeek <outcastgeek+github@gmail.com>
RUN apt-get -qq update
RUN apt-get -qqy install python-software-properties build-essential wget git
RUN apt-get -qqy install ruby ruby-dev python-dev python-pip libevent-dev libzmq-dev libsqlite3-dev
RUN pip install --upgrade pip
RUN git clone https://github.com/outcastgeek/pyramid_and_zmq_on_docker /root/pyramid_and_zmq_on_docker
RUN cd /root/pyramid_and_zmq_on_docker
RUN pip install -r requirements.txt

