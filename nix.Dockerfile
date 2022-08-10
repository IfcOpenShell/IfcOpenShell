FROM continuumio/miniconda3

RUN apt-get update
RUN apt-get -y install \
    git gcc g++ autoconf bison make cmake libfreetype6-dev mesa-common-dev libffi-dev libfontconfig1-dev patch

COPY . .

RUN cd nix && python3 build-all.py