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
  run_es)
    docker run -d -p $2 outcastgeek/es
    ;;
  esac
exit 0



