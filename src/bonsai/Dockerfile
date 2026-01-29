# Build Bonsai .zip.
# Usage:
#    # While in `bonsai` folder.
#    docker build -t bonsai-dist .
#    # Output zip file will be in `dist` folder.
#    # See possible values for variables in `Makefile`'s `dist` target description.
#    docker run --rm -v "$PWD/../../:/work" -w /work -e PLATFORM=win -e PYVERSION=py313 bonsai-dist

FROM ubuntu:24.04
RUN apt-get update
RUN apt-get install -y make git wget unzip zip

# Python
RUN apt-get install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get update
RUN apt-get install -y python3.11 python3.11-venv

RUN apt-get install -y npm

WORKDIR /work
CMD cd src/bonsai && make dist PLATFORM=$PLATFORM PYVERSION=$PYVERSION
