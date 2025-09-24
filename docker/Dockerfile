FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

ARG PHYSICS="ST4"
ARG COMP="Gnu"
ARG SWITCH="Ifremer1"

RUN apt-get update -y && apt-get upgrade -y && \
    apt-get install -y \
    git vim sudo tar unzip subversion wget \
    gcc g++ gfortran lftp openmpi-bin libopenmpi-dev \
    libnetcdf-dev libnetcdff-dev make cmake python3 python3-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*


RUN mkdir -p /source && cd /source && \
    wget https://github.com/NOAA-EMC/WW3/archive/refs/tags/6.07.1.tar.gz && \
    tar -xvzf 6.07.1.tar.gz && rm 6.07.1.tar.gz && \
    mv WW3-6.07.1/model /source/model && rm -rf WW3-6.07.1

# Copy comp with fixed gfortran compile flags
COPY comp.Gnu_fix /source/model/bin/comp.Gnu

# Compile and install model
WORKDIR /source/model/bin

ENV WWATCH3_NETCDF=NC4
ENV NETCDF_CONFIG=/usr/bin/nf-config

RUN ./w3_setup /source/model -q -c ${COMP} -s ${SWITCH} -t /source/model/tmp && \
    ./make_MPI &&\
    cp /source/model/exe/ww3_* /usr/local/bin
