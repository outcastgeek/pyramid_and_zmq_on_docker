# Container Configuration
FROM ubuntu:14.04
MAINTAINER outcastgeek <outcastgeek+github@gmail.com>
RUN apt-get -qq update
RUN apt-get -qqy install software-properties-common python-software-properties wget
RUN add-apt-repository ppa:webupd8team/java
RUN apt-get -qq update
# http://askubuntu.com/questions/190582/installing-java-automatically-with-silent-option
RUN echo debconf shared/accepted-oracle-license-v1-1 select true | debconf-set-selections
RUN echo debconf shared/accepted-oracle-license-v1-1 seen true | debconf-set-selections
RUN apt-get install -qqy oracle-java7-installer
RUN java -version
RUN wget -qO - http://packages.elasticsearch.org/GPG-KEY-elasticsearch | sudo apt-key add -
RUN echo "deb http://packages.elasticsearch.org/elasticsearch/1.3/debian stable main" >> /etc/apt/sources.list
#RUN cat /etc/apt/sources.list
RUN apt-get -qq update
RUN apt-get install elasticsearch
RUN sysctl -w vm.max_map_count=262144
RUN update-rc.d elasticsearch defaults 95 10
RUN /etc/init.d/elasticsearch start
EXPOSE 9200
CMD ["/etc/init.d/elasticsearch","start"]

