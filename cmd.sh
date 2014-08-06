#!/bin/bash

case $1 in
  build_app)
    docker build -t outcastgeek/pazod $2
    ;;
  run_app)
    docker run -d -p $2 outcastgeek/pazod 
    ;;
  images)
    docker images
    ;;
  img_clean)
    docker rmi $@
    ;;
  processes)
    docker ps -a
    ;;
  clean_pcs)
    docker kill $(docker ps -a -q) && docker rm $(docker ps -a -q)
    ;;
  pc_clean)
    docker kill $2 && docker rm $2
    ;;
  build_es)
    docker build -t outcastgeek/es $2
    ;;
  run_es) # docker run -d -p 9200:9200 -p 9300:9300 dockerfile/elasticsearch
          # docker run -d -p 9200:9200 -p 9300:9300 -v <data-dir>:/data dockerfile/elasticsearch /elasticsearch/bin/elasticsearch -Des.config=/data/elasticsearch.yml
    docker run -d -p $2:9200 -p $3:9300 outcastgeek/es
    #docker run -d -p $2:9200 -p $3:9300 -v $4:/data outcastgeek/es /elasticsearch/bin/elasticsearch -Des.config=/data/elasticsearch.yml
    ;;
  build_pg)
    docker build -t outcastgeek/pg $2
    ;;
  run_pg) # run -d --name postgresql -p 5432:5432 -e POSTGRESQL_PASS=oe9jaacZLbR9pN imanel/postgresql
    docker run -d --name postgresql -p $2:5432 -e POSTGRESQL_PASS=$3 outcastgeek/pg
    ;;
  pg_client) # docker run -i --rm -t --entrypoint="bash" --link postgresql:postgresql imanel/postgresql -c 'psql -h $POSTGRESQL_PORT_5432_TCP_ADDR --user postgres'
    docker run -i --rm -t --entrypoint="bash" --link postgresql:postgresql outcastgeek/pg -c 'psql -h $POSTGRESQL_PORT_5432_TCP_ADDR --user postgres'
    ;;
  esac
exit 0



