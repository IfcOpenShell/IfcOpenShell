# -*- mode: Dockerfile -*-

FROM ubuntu:22.04

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
    apt-get -y install python3 libxml2 libpython3.10 \
                    libboost-all-dev \
                    libocct-foundation-dev libocct-modeling-algorithms-dev libocct-modeling-data-dev \
                    libocct-ocaf-dev libocct-visualization-dev libocct-data-exchange-dev \
                    libhdf5-serial-dev python3-pytest ; \
    rm -rf /var/lib/apt/lists/* ; 

COPY . /home/IfcOpenShell/
RUN ls -lrtR /home/IfcOpenShell

RUN dpkg -i /home/IfcOpenShell/*.deb 

USER IfcOpenShell

