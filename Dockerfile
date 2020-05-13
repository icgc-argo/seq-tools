FROM continuumio/miniconda:4.7.12-alpine

ENV PATH=/opt/conda/condabin:$PATH

COPY environment.yml /tmp/

RUN conda env create -f /tmp/environment.yml && \
    conda clean -a


ENV PATH=/opt/conda/envs/seq-tools-0.1.0/bin:$PATH

