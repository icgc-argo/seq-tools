FROM continuumio/miniconda:4.7.12

LABEL maintainer="junju.zhang@oicr.on.ca"

ARG VERSION=1.0.0-rc.1
ARG NAME=seq-tools

ENV PATH=/opt/conda/condabin:$PATH

COPY . /tmp/${NAME}/

RUN cd /tmp/${NAME}/ && \
    conda env create -f environment.yml && \
    conda clean -a

ENV PATH=/opt/conda/envs/${NAME}-${VERSION}/bin:$PATH

RUN groupadd -g 1000 ubuntu && \
    useradd -l -u 1000 -g ubuntu ubuntu -s /bin/bash && \
    install -d -m 0755 -o ubuntu -g ubuntu /home/ubuntu

USER ubuntu

CMD /bin/bash
