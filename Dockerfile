# Container Configuration
FROM ubuntu:14.04
MAINTAINER outcastgeek <outcastgeek+github@gmail.com>
RUN apt-get -qq update
RUN apt-get -qqy install python-software-properties build-essential wget git
RUN apt-get -qqy install ruby ruby-dev python-dev python-pip libevent-dev libzmq-dev libsqlite3-dev
RUN pip install --upgrade pip
RUN gem install bundler
#RUN git clone https://github.com/outcastgeek/pyramid_and_zmq_on_docker /root/pyramid_and_zmq_on_docker
ADD . /root/pyramid_and_zmq_on_docker
WORKDIR /root/pyramid_and_zmq_on_docker
RUN bundle install
RUN pip install -r requirements.txt
RUN initialize_pazod_db development.ini
EXPOSE 6543
ENV PORT 6543
CMD ["/usr/local/bin/foreman","start","-d","/root/pyramid_and_zmq_on_docker"]

