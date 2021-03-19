# -*- mode: Dockerfile -*-

FROM ubuntu:focal

ARG CHANNEL
ENV CHANNEL=${CHANNEL:-latest}
RUN apt-get update \
    && apt-get install -y \
    vim \
    ssh \
    sudo \
    wget \
    software-properties-common ;\
    rm -rf /var/lib/apt/lists/*

RUN useradd --user-group --create-home --shell /bin/bash IfcOpenShell ;\
    echo "IfcOpenShell ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers


ENV DEBIAN_FRONTEND=noninteractive        
RUN echo "deb http://archive.ubuntu.com/ubuntu focal-proposed main restricted" |  tee -a /etc/apt/sources.list; \ 
    echo "deb http://archive.ubuntu.com/ubuntu focal-proposed universe" |  tee -a /etc/apt/sources.list; \
    echo "deb http://archive.ubuntu.com/ubuntu focal-proposed multiverse" |  tee -a /etc/apt/sources.list; \
    apt-get -qq update; \
    apt-get -y install tzdata dos2unix rsync; \
    apt-get -y install python3 libxml2 liboce-foundation11 liboce-modeling11 liboce-ocaf11 liboce-visualization11 \
                     liboce-ocaf-lite11 libpython3.8 libboost-system1.67.0 libboost-program-options1.67.0 \
                    libboost-regex1.67.0 libboost-thread1.67.0 libboost-date-time1.67.0; \
    rm -rf /var/lib/apt/lists/* ; 

COPY . /home/IfcOpenShell/
RUN ls -lrtR /home/IfcOpenShell

RUN dpkg -i /home/IfcOpenShell/*.deb 

USER IfcOpenShell

